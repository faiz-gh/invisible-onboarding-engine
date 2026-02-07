import streamlit as st
import base64
import difflib
from api_client import generate_onboarding_packet, get_file_content, ask_policy_question

# 1. Page Config
st.set_page_config(
    page_title="Deriv | Invisible Onboarding",
    page_icon="⚡",
    layout="wide"
)

# 2. Session State Initialization
if "onboarding_data" not in st.session_state:
    st.session_state["onboarding_data"] = None
if "approval_status" not in st.session_state:
    st.session_state["approval_status"] = "pending"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "👋 Hi! I'm the Deriv Policy Bot. Ask me about remote work, expenses, or relocation!"}
    ]

# 3. Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        color: #333333 !important;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff444f;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .metric-card b { color: #000000 !important; }
    .stButton>button { width: 100%; font-weight: bold; }
    .status-approved {
        background-color: #d4edda; color: #155724;
        padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Helper: Diff Generator
def create_diff_html(text1, text2):
    d = difflib.Differ()
    diff = list(d.compare(text1.splitlines(), text2.splitlines()))
    html = ['<div style="font-family: monospace; white-space: pre-wrap; background-color: #f0f0f0; padding: 10px; border-radius: 5px; height: 300px; overflow-y: scroll;">']
    for line in diff:
        if line.startswith('+ '):
            html.append(f'<div style="background-color: #d4edda; color: #155724;">{line[2:]}</div>')
        elif line.startswith('- '):
            html.append(f'<div style="background-color: #f8d7da; color: #721c24; text-decoration: line-through;">{line[2:]}</div>')
        elif not line.startswith('? '):
            html.append(f'<div style="color: #333;">{line[2:]}</div>')
    html.append('</div>')
    return "\n".join(html)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Deriv_Logo.svg/2560px-Deriv_Logo.svg.png", width=150)
st.sidebar.title("Deriv HR OS")
app_mode = st.sidebar.radio("Navigate:", ["🚀 Onboarding Engine", "💬 Ask HR Assistant"])

# ==========================================
# PAGE 1: ONBOARDING ENGINE
# ==========================================
if app_mode == "🚀 Onboarding Engine":
    
    col1, col2 = st.columns([0.5, 5])
    with col2:
        st.title("Invisible Onboarding Engine")
        st.caption("AI-Powered Contract Generation & Compliance Intelligence")
    st.markdown("---")

    # INPUT SECTION
    is_locked = st.session_state["approval_status"] == "approved"
    with st.container():
        input_text = st.text_area(
            "1. New Hire Context (Paste Email/Notes):",
            height=100,
            disabled=is_locked,
            value="Hire Alex Smith as Senior DevOps Engineer in Dubai. Salary 25000 AED. He is a UK citizen starting next Monday." if not st.session_state["onboarding_data"] else ""
        )
        
        if not is_locked:
            if st.button("🚀 Generate Onboarding Packet", type="primary"):
                with st.spinner("🤖 Extracting data, checking laws, and drafting contract..."):
                    data = generate_onboarding_packet(input_text)
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        st.session_state["onboarding_data"] = data
                        st.session_state["approval_status"] = "pending"
                        st.rerun()

    # RESULTS SECTION
    if st.session_state["onboarding_data"]:
        data = st.session_state["onboarding_data"]
        
        # Row 1: Profile & Risks
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.subheader("👤 Candidate Profile")
            cand = data["candidate"]
            st.markdown(f"""
            <div class="metric-card">
                <b>Name:</b> {cand['name']}<br>
                <b>Role:</b> {cand['role']} ({cand.get('job_family', 'General')})<br>
                <b>Location:</b> {cand['location_country']}<br>
                <b>Citizenship:</b> {cand['citizenship']}<br>
                <b>Salary:</b> {cand['currency']} {cand['salary']:,}
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.subheader("📜 Jurisdiction")
            st.info(f"Detected: {data['jurisdiction_detected']}")
            
        with c3:
            st.subheader("🛡️ Compliance Check")
            alerts = data.get("compliance_alerts", [])
            if not alerts:
                st.success("✅ No Critical Risks Detected")
            else:
                for alert in alerts:
                    # Handle both dictionary and string alerts
                    msg = alert.get("message", str(alert)) if isinstance(alert, dict) else str(alert)
                    if "Risk" in msg or "Visa" in msg:
                        st.error(f"🚨 {msg}")
                    else:
                        st.warning(f"⚠️ {msg}")

        st.markdown("---")

        # Row 2: Diff View
        st.subheader("2. Review & Approve Contract")
        with st.expander("🔍 Inspect Changes (Interactive Diff)", expanded=True):
            diff_html = create_diff_html(
                data.get("original_template_text", ""), 
                data.get("final_contract_text", "")
            )
            st.caption("Green highlights show data automatically filled by AI.")
            st.components.v1.html(diff_html, height=300, scrolling=True)
        
        # Row 3: PDF & Actions
        p1, p2 = st.columns([2, 1])
        with p1:
            st.markdown("### 📄 PDF Preview")
            pdf_path = data["generated_files"][0]
            pdf_bytes = get_file_content(pdf_path)
            if pdf_bytes:
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

        with p2:
            st.markdown("### ✅ Action")
            if st.session_state["approval_status"] == "approved":
                st.markdown('<div class="status-approved">🎉 OFFER SENT!</div>', unsafe_allow_html=True)
                if st.button("Start New Candidate"):
                    st.session_state["onboarding_data"] = None
                    st.session_state["approval_status"] = "pending"
                    st.rerun()
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("❌ Reject"):
                        st.session_state["onboarding_data"] = None
                        st.rerun()
                with col_b:
                    if st.button("✅ Approve", type="primary"):
                        st.session_state["approval_status"] = "approved"
                        st.balloons()
                        st.rerun()

# ==========================================
# PAGE 2: ASK HR ASSISTANT
# ==========================================
elif app_mode == "💬 Ask HR Assistant":
    st.title("💬 Deriv Policy Assistant")
    st.caption("Instant answers from the Employee Handbook (RAG Powered)")

    # Chat UI
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ex: Can I work from Bali?"):
        # User Message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # AI Response
        with st.chat_message("assistant"):
            with st.spinner("Consulting the handbook..."):
                data = ask_policy_question(prompt)
                answer = data.get("answer", "Error retrieving answer.")
                st.write(answer)
        
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})