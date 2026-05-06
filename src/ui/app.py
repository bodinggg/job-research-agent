"""Streamlit UI for Job Research Agent."""
import streamlit as st
import requests
from datetime import datetime

# API configuration
API_URL = "http://localhost:8002"


def init_session_state():
    """Initialize Streamlit session state."""
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sessions" not in st.session_state:
        st.session_state.sessions = []
    if "is_researching" not in st.session_state:
        st.session_state.is_researching = False
    if "current_report" not in st.session_state:
        st.session_state.current_report = None


def api_request(method: str, endpoint: str, data: dict = None, params: dict = None):
    """Make API request."""
    try:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到API，请确保后端正在运行。"}
    except requests.exceptions.Timeout:
        return {"error": "请求超时，请重试。"}
    except Exception as e:
        return {"error": str(e)}


def research_company(company: str, position: str, session_id: str = None) -> dict:
    """Call the research API."""
    data = {"company": company, "position": position}
    if session_id:
        data["session_id"] = session_id
    return api_request("POST", "/research", data)


def send_dialogue(query: str, session_id: str) -> dict:
    """Send dialogue message."""
    return api_request("POST", "/dialogue", {"query": query, "session_id": session_id})


def get_sessions() -> list:
    """Get all sessions."""
    result = api_request("GET", "/sessions")
    if isinstance(result, list):
        return result
    return []


def get_session_history(session_id: str) -> list:
    """Get session conversation history."""
    result = api_request("GET", f"/sessions/{session_id}/history")
    if isinstance(result, dict) and "messages" in result:
        return result["messages"]
    return []


def get_session_reports(session_id: str) -> list:
    """Get session reports."""
    result = api_request("GET", f"/sessions/{session_id}/reports")
    if isinstance(result, dict) and "reports" in result:
        return result["reports"]
    return []


def render_sidebar():
    """Render sidebar with session management."""
    st.sidebar.title("会话管理")
    st.sidebar.markdown("---")

    # Refresh sessions
    if st.sidebar.button("🔄 刷新会话列表"):
        st.session_state.sessions = get_sessions()
        st.rerun()

    # Session list
    st.sidebar.subheader("研究历史")
    sessions = st.session_state.get("sessions", [])

    if not sessions:
        st.sidebar.info("暂无研究记录")
    else:
        for sess in reversed(sessions[-10:]):
            is_current = sess["id"] == st.session_state.current_session_id
            label = f"**{sess['company']}** - {sess['position']}"
            if is_current:
                label = f"👉 {label}"

            if st.sidebar.button(label, key=sess["id"]):
                st.session_state.current_session_id = sess["id"]
                st.session_state.messages = get_session_history(sess["id"])
                reports = get_session_reports(sess["id"])
                if reports:
                    st.session_state.current_report = reports[-1]["content"]
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 选择一个会话继续对话，或开启新的研究"
    )


def render_research_form():
    """Render research input form."""
    st.subheader("🔍 新研究")

    with st.form("research_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            company = st.text_input(
                "公司",
                placeholder="例如：字节跳动、Google",
            )
        with col2:
            position = st.text_input(
                "职位",
                placeholder="例如：后端工程师、SRE",
            )

        submitted = st.form_submit_button(
            "🚀 开始研究",
            type="primary",
            disabled=st.session_state.is_researching
        )

    if submitted and company and position:
        st.session_state.is_researching = True

        with st.spinner("🔄 研究中... 这可能需要1-2分钟。"):
            result = research_company(company, position, st.session_state.current_session_id)

        st.session_state.is_researching = False

        if "error" in result:
            st.error(f"错误: {result['error']}")
        else:
            st.session_state.current_session_id = result["session_id"]
            st.session_state.current_report = result["report"]
            st.session_state.messages = []
            st.session_state.sessions = get_sessions()
            st.rerun()

    return company, position


def render_report_section():
    """Render the research report section."""
    report = st.session_state.get("current_report")

    if not report:
        st.info("👆 输入公司名称和职位，开始一项研究")
        return

    st.subheader("📊 研究报告")
    st.markdown(report, unsafe_allow_html=True)


def render_chat_section():
    """Render the conversation chat section."""
    if not st.session_state.current_session_id:
        return

    session_id = st.session_state.current_session_id
    st.subheader("💬 对话")

    # Display chat messages
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(content)

    # Chat input
    if query := st.chat_input("输入问题..."):
        # Save user message to display
        st.session_state.messages.append({"role": "user", "content": query})

        # Display user message
        with st.chat_message("user"):
            st.markdown(query)

        # Send to API
        with st.spinner("思考中..."):
            result = send_dialogue(query, session_id)

        if "error" in result:
            st.error(result["error"])
        else:
            # Display assistant response
            answer = result.get("answer", "")
            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="求职研究助手",
        page_icon="🔍",
        layout="wide"
    )

    init_session_state()
    render_sidebar()

    st.title("🔍 求职研究助手")
    st.markdown("输入公司名称和职位，获取AI驱动的研究报告，并随时追问。")

    # Main content area
    col_main, col_chat = st.columns([1, 1])

    with col_main:
        company, position = render_research_form()
        st.markdown("---")
        render_report_section()

    with col_chat:
        render_chat_section()

    # Load sessions on startup
    if not st.session_state.sessions:
        st.session_state.sessions = get_sessions()


if __name__ == "__main__":
    main()