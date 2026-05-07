"""Liepin search engine using Playwright."""
from typing import Optional
import asyncio

from src.search.models import JobSummary


class LiepinEngine:
    """Search engine for Liepin (liepin.com)."""

    BASE_URL = "https://www.liepin.com/zhaopin/"

    async def search(
        self,
        keyword: str,
        city: Optional[str] = None,
        **kwargs
    ) -> list[JobSummary]:
        """Search jobs on Liepin.

        Args:
            keyword: Search keyword
            city: City name (Liepin uses city code in URL or dq param)
            **kwargs: Additional parameters

        Returns:
            List of job summaries
        """
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Build URL with keyword
                url = f"{self.BASE_URL}?key={keyword}"
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)

                jobs = await self._extract_jobs(page)
                await browser.close()
                return jobs
        except Exception:
            return []

    async def _extract_jobs(self, page) -> list[JobSummary]:
        """Extract job listings from page using DOM traversal."""
        jobs = []

        try:
            # Wait for job list to load
            await page.wait_for_selector(".job-list-box", timeout=10000)

            # Get job list container
            job_list_box = await page.query_selector(".job-list-box")
            if not job_list_box:
                return []

            # Get all direct children (job cards)
            cards = await job_list_box.query_selector_all(":scope > div")

            for card in cards[:20]:  # Limit to 20 results
                try:
                    # Get job link and URL
                    link_el = await card.query_selector("a[href*='/job/']")
                    if not link_el:
                        continue

                    job_url = await link_el.get_attribute("href")
                    if job_url and not job_url.startswith("http"):
                        job_url = f"https://www.liepin.com{job_url}"

                    # Extract text content from card
                    card_text = await card.inner_text()
                    lines = [line.strip() for line in card_text.split("\n") if line.strip()]

                    if not lines:
                        continue

                    # Parse job info from text lines
                    # Structure: title, location (multi-line with brackets), salary, workYears, company, scale
                    title = lines[0] if lines else ""
                    address = None
                    salary = None
                    company = None

                    # Track which line index we've seen job requirements
                    found_requirements = False

                    # Combine lines for address detection (handle multi-line address format)
                    text_combined = "".join(lines)

                    for i, line in enumerate(lines):
                        # Skip title (first line) and emoji-only lines
                        if i == 0:
                            continue
                        if line in ["急聘", "最新", "在线"]:
                            continue

                        # Salary patterns
                        if any(c in line.lower() for c in ["k", "万", "薪", "元"]):
                            if not salary:
                                if "面议" in line:
                                    salary = "薪资面议"
                                else:
                                    salary = line
                        # Location patterns (multi-line format with 【 】)
                        elif line == "【":
                            # Next non-empty line is likely the city/district
                            continue
                        elif line == "】":
                            continue
                        elif "-" in line and any(c in line for c in ["区", "市", "州"]):
                            if not address:
                                # Check if it's between 【 and 】
                                if i > 1 and lines[i-1] == "【":
                                    address = line
                                # Or just look for city-district pattern
                                elif any(seg in lines[max(0,i-2):i+1] for seg in ["【", '【\n']):
                                    address = line
                                else:
                                    address = line
                        # Work experience and education patterns
                        elif any(c in line for c in ["年", "本科", "硕士", "博士", "大专", "学历"]):
                            found_requirements = True
                        # Company name (after requirements, before recruiter info)
                        elif found_requirements and company is None:
                            # Skip recruiter info patterns
                            if "·" in line or "在线" in line or any(c.isdigit() for c in line):
                                continue
                            if len(line) > 2 and len(line) < 50:
                                company = line
                                break

                    # If no company found, try to find it by pattern (line with company-like content)
                    if not company:
                        for line in lines[3:8]:  # Look in early-to-mid lines
                            if any(c in line for c in ["公司", "有限", "集团", "科技", "软件", "银行", "证券", "基金"]):
                                company = line
                                break
                            # Also try lines that look like company names (Chinese characters with specific patterns)
                            if len(line) >= 4 and len(line) <= 30 and not any(c in line for c in ["年", "k", "K", "万", "薪", "元", "在线", "急聘"]):
                                import re
                                if re.match(r'^[\u4e00-\u9fa5]+', line):
                                    company = line
                                    break

                    jobs.append(
                        JobSummary(
                            source="liepin",
                            title=title or "",
                            company=company or "",
                            salary=salary,
                            address=address,
                            job_url=job_url,
                        )
                    )
                except Exception:
                    continue

        except Exception:
            pass

        return jobs
