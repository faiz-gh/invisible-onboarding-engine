import streamlit as st
import base64
import difflib
import os
from api_client import generate_onboarding_packet, get_file_content, ask_policy_question

# 1. Page Config
st.set_page_config(
    page_title="Deriv | Invisible Onboarding",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Safety: Load CSS with Error Handling
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ CSS file not found. UI might look unstyled.")

load_css()

# 3. Session State Initialization
if "onboarding_data" not in st.session_state:
    st.session_state["onboarding_data"] = None
if "approval_status" not in st.session_state:
    st.session_state["approval_status"] = "pending"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "👋 Hi! I'm the Deriv Policy Bot. Ask me about remote work, expenses, or relocation!"}
    ]

# 4. Helper: Diff Generator (Improved HTML)
def create_diff_html(text1, text2):
    d = difflib.Differ()
    diff = list(d.compare(text1.splitlines(), text2.splitlines()))
    html = ['<div class="diff-container">']
    for line in diff:
        if line.startswith('+ '):
            html.append(f'<span class="diff-add">{line[2:]}</span>')
        elif line.startswith('- '):
            html.append(f'<span class="diff-del">{line[2:]}</span>')
        elif not line.startswith('? '):
            html.append(f'<span class="diff-normal">{line[2:]}</span>')
    html.append('</div>')
    return "\n".join(html)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Deriv_Logo.svg/2560px-Deriv_Logo.svg.png", width=150)
    st.title("Deriv HR OS")
    app_mode = st.radio("Navigate", ["🚀 Onboarding Engine", "💬 Ask HR Assistant"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📊 Status")
    if st.session_state["onboarding_data"]:
        st.success("● Active Candidate")
    else:
        st.info("○ Ready")
    
    st.markdown("---")
    st.caption("v2.0 | Invisible Onboarding")

# ==========================================
# PAGE 1: ONBOARDING ENGINE
# ==========================================
if app_mode == "🚀 Onboarding Engine":
    
    # Header
    col_h1, col_h2 = st.columns([0.1, 0.9])
    with col_h1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    with col_h2:
        st.title("Invisible Onboarding Engine")
        st.caption("AI-Powered Contract Generation & Compliance Intelligence")
    
    st.markdown("---")

    # INPUT SECTION
    is_locked = st.session_state["approval_status"] == "approved"
    
    with st.expander("📝 New Hire Context", expanded=not st.session_state["onboarding_data"]):
        input_text = st.text_area(
            "Paste Email or Notes",
            height=120,
            disabled=is_locked,
            placeholder="e.g., Hire Alex Smith as Senior DevOps Engineer in Dubai...",
            help="The AI will extract name, role, salary, and location from natural language."
        )
        
        c_btn1, c_btn2 = st.columns([1, 5])
        with c_btn1:
            if not is_locked:
                if st.button("🚀 Generate Packet", type="primary", disabled=not input_text.strip()):
                    with st.spinner("🤖 Processing with AI..."):
                        data = generate_onboarding_packet(input_text)
                        if "error" in data:
                            st.error(f"❌ {data['error']}")
                        else:
                            st.session_state["onboarding_data"] = data
                            st.session_state["approval_status"] = "pending"
                            st.rerun()
        with c_btn2:
            if st.button("🗑️ Clear", disabled=is_locked):
                st.session_state["onboarding_data"] = None
                st.rerun()

    # RESULTS SECTION
    if st.session_state["onboarding_data"]:
        data = st.session_state["onboarding_data"]
        cand = data["candidate"]
        
        # Tabs for better organization
        tab1, tab2, tab3 = st.tabs(["👤 Candidate Profile", "⚖️ Compliance & Risks", "📝 Contract Review"])
        
        with tab1:
            st.subheader("Candidate Details")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <b>Name</b><br>{cand['name']}
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-card">
                    <b>Role</b><br>{cand['role']}
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <b>Location</b><br>{cand['location_country']}
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-card">
                    <b>Citizenship</b><br>{cand['citizenship']}
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <b>Salary</b><br>{cand['currency']} {cand['salary']:,}
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-card">
                    <b>Job Family</b><br>{cand.get('job_family', 'General')}
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            st.subheader("Automated Compliance Analysis")
            
            # Jurisdiction
            st.markdown(f"""
            <div style="background-color: #e3f2fd; padding:15px; border-radius:10px; margin-bottom:20px; border-left: 5px solid #2196f3;">
                <b>🏛️ Detected Jurisdiction:</b> {data['jurisdiction_detected']}
            </div>
            """, unsafe_allow_html=True)

            # Alerts
            alerts = data.get("compliance_alerts", [])
            if not alerts:
                st.markdown('<div class="status-badge success">✅ No Critical Risks Detected</div>', unsafe_allow_html=True)
                st.balloons() # Maybe too much?
            else:
                for alert in alerts:
                    msg = alert.get("message", str(alert)) if isinstance(alert, dict) else str(alert)
                    if "Risk" in msg or "Visa" in msg:
                        st.markdown(f'<div class="status-badge error">🚨 {msg}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-badge warning">⚠️ {msg}</div>', unsafe_allow_html=True)

        with tab3:
            st.subheader("Review & Approve")
            
            # Interactive Diff
            st.info("Review changes made to the template by AI (Green = Added).")
            diff_html = create_diff_html(
                data.get("original_template_text", ""), 
                data.get("final_contract_text", "")
            )
            st.markdown(diff_html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Action Buttons
            c_act1, c_act2 = st.columns([2, 1])
            
            with c_act1:
                 # PDF Preview
                st.markdown("#### 📄 PDF Preview")
                pdf_path = data["generated_files"][0]
                pdf_bytes = get_file_content(pdf_path)
                if pdf_bytes:
                    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
            
            with c_act2:
                st.markdown("#### ✅ Decision")
                st.markdown('<div class="action-area">', unsafe_allow_html=True)
                
                if st.session_state["approval_status"] == "approved":
                    st.markdown('<h3 style="color: green;">🎉 OFFER SENT!</h3>', unsafe_allow_html=True)
                    if st.button("Start New Candidate"):
                        st.session_state["onboarding_data"] = None
                        st.session_state["approval_status"] = "pending"
                        st.rerun()
                else:
                    if st.button("✅ Approve & Send", type="primary"):
                        st.session_state["approval_status"] = "approved"
                        st.balloons()
                        st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if st.button("❌ Reject / Edit"):
                        st.session_state["onboarding_data"] = None
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# PAGE 2: ASK HR ASSISTANT
# ==========================================
elif app_mode == "💬 Ask HR Assistant":
    st.title("💬 Deriv Policy Assistant")
    st.caption("Instant answers from the Employee Handbook (RAG Powered)")
    st.markdown("---")

    # Chat Container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state["chat_history"]:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

    # Input
    if prompt := st.chat_input("Ex: Can I work from Bali?"):
        # User Message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)

        # AI Response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Consulting the handbook..."):
                data = ask_policy_question(prompt)
                answer = data.get("answer", "Error retrieving answer.")
                st.write(answer)
        
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})