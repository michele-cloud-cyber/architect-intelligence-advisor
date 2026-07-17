import os
import sys
print("APP STARTED")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from sr.engines.bedrock_engine import BedrockEngine
from sr.engines.fingerprint_engine import FingerprintEngine
from sr.models.landing_zone import LandingZone
from sr.engines.history_engine import HistoryEngine
from sr.services.landing_zone_service import build_landing_zone

st.set_page_config(
    page_title="AI Architect Advisor",
    page_icon="🤖",
    layout="wide"
)

# ==========================================================
# Landing Zone
# ==========================================================

landing_zone = build_landing_zone()

fingerprint = landing_zone.fingerprint
# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🤖 AI Architect Advisor")

st.sidebar.markdown("---")

st.sidebar.selectbox(
    "AWS Account",
    [
        "All Accounts",
        "Production",
        "Shared Services",
        "Development",
        "Security"
    ]
)

st.sidebar.selectbox(
    "Region",
    [
        "All Regions",
        "eu-west-1",
        "eu-central-1",
        "us-east-1"
    ]
)

st.sidebar.selectbox(
    "Environment",
    [
        "All",
        "Production",
        "Development",
        "Test"
    ]
)

st.sidebar.markdown("---")
st.sidebar.success("🟢 Bedrock Connected")
st.sidebar.metric("Landing Zone", "Healthy")
st.sidebar.metric("AI Status", "Online")
st.sidebar.metric("Last Scan", "2 min ago")

# ==========================================================
# HEADER
# ==========================================================

st.title("🤖 AI Architect Advisor")
st.subheader("AWS Landing Zone Intelligence Platform")

st.divider()

# ==========================================================
# KPI
# ==========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Security Score", "92/100", "+4")

with col2:
    st.metric("AWS Accounts", "18", "+2")

with col3:
    st.metric("Critical Risks", "3", "-1")

with col4:
    st.metric("Monthly Cost", "$487", "-8%")

# ==========================================================
# Fingerprint
# ==========================================================

st.divider()

st.subheader("🔐 Landing Zone Fingerprint")

c1, c2 = st.columns(2)

with c1:
    st.metric("Architecture Rating", fingerprint["architecture"])
    st.metric("Overall Score", f"{fingerprint['overall']:.1f}")

with c2:
    st.metric("Security", fingerprint["security"])
    st.metric("Logging", fingerprint["logging"])

st.code(fingerprint["hash"])

# ==========================================================
# Executive Summary
# ==========================================================

st.divider()

st.subheader("🧠 Executive Summary")

st.info("""
The AI Architect Advisor analyzed your AWS Landing Zone.

Overall posture has improved compared to the previous assessment.

✅ Networking posture is healthy after reducing public exposure.

⚠️ The primary risk has shifted to IAM permissions.

💰 FinOps analysis shows decreasing EC2 costs but NAT Gateway remains the largest networking expense.

📈 Forecast indicates the Security Score could improve from 92 to 97 after recommended remediations.
""")

# ==========================================================
# Landing Zone Posture
# ==========================================================

st.subheader("📈 Landing Zone Posture")

chart = pd.DataFrame({
    "Security":[90,87,84,92],
    "Networking":[80,84,89,94],
    "IAM":[88,82,76,73],
    "FinOps":[65,69,74,81]
})

st.line_chart(chart)

# ==========================================================
# Landing Zone Health
# ==========================================================

st.subheader("🛡️ Landing Zone Health")

col1, col2 = st.columns(2)

with col1:
    st.write("Security")
    st.progress(92)

    st.write("Networking")
    st.progress(94)

with col2:
    st.write("IAM Governance")
    st.progress(73)

    st.write("FinOps")
    st.progress(81)

# ==========================================================
# AI Assessment
# ==========================================================

st.subheader("🧠 AI Executive Assessment")

st.success("""
The Landing Zone is evolving positively.

Networking security has significantly improved.

Identity management is now the main operational concern.

Cost optimization initiatives are reducing EC2 spend.

Forecast models indicate a Security Score of 97/100 after the recommended actions are completed.
""")

# ==========================================================
# Recommendations
# ==========================================================

st.subheader("✅ Recommended Actions")

st.checkbox("Remove unused IAM Administrator policies")
st.checkbox("Create additional VPC Endpoints")
st.checkbox("Enable GuardDuty organization-wide")
st.checkbox("Optimize NAT Gateway traffic")
st.checkbox("Enable automatic Security Hub remediation")

# ==========================================================
# AI Chat
# ==========================================================

st.divider()

st.subheader("💬 AI Advisor")

question = st.text_input(
    "Ask something about your Landing Zone"
)

if st.button("Ask AI"):

    try:

        engine = BedrockEngine()

        prompt = engine.generate_prompt(landing_zone)

        if question:
            prompt += f"\n\nUser Question:\n{question}"

        answer = engine.invoke(prompt)

        st.success(answer)

    except Exception as e:
        st.error(f"Error: {e}")

# ==========================================================
# AI Assessment
# ==========================================================

st.markdown("### 🔍 AI Assessment")
# ===========================
# Historical Changes
# ===========================

st.divider()

st.subheader("📜 Historical Changes")

try:

    history = HistoryEngine()

    landing_zone = LandingZone()

    current_report = {
        "overall_score": 92,
        "risk_score": 18
    }

    changes = history.compare(current_report)

    for change in changes:
        st.info(change)

except Exception as e:
    st.warning(f"History unavailable: {e}")

st.info("""
The account **Production-Shared** currently has the highest operational risk.

**Reason**

- 12 Security Hub findings
- 3 IAM Administrator roles
- Security Score: **68/100**

**Recommendation**

Remove unused Administrator policies and enable GuardDuty delegated administration.
""")
