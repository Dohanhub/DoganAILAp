import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.data import get_functional_layers_data, get_compliance_coverage_data

st.set_page_config(
    page_title="Product Overview - Doğan AI Lab",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Product Overview")
st.markdown("**AI-driven compliance validation and risk management platform purpose-built for Saudi regulations**")

# What is Doğan AI Lab
st.header("🎯 What is Doğan AI Lab?")

st.markdown("""
Doğan AI Lab is an AI-driven compliance validation and risk management platform purpose-built for Saudi regulations. 
Delivered as an integrated software-and-hardware solution, it continuously monitors an organization's controls 
against local standards and automates compliance workflows.

**Vision**: Turn compliance from a periodic, painful audit exercise into a proactive, streamlined process.
""")

# Core Functional Layers
st.header("🏗️ Core Functional Layers")

st.markdown("Doğan AI Lab consists of three primary layers that work in concert:")

# Create tabs for each layer
tab1, tab2, tab3 = st.tabs(["🤖 Automated Compliance Engine", "👥 Vendor Risk Module", "📊 Reporting & Dashboard"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Automated Compliance Engine")
        st.markdown("""
        The core rules engine codifies all major Saudi cybersecurity and privacy requirements and checks 
        the organization's environment against them in real-time.
        
        **Key Features:**
        - ✅ 100% coverage of NCA ECC v2.0 controls
        - ✅ Complete SAMA CSF controls mapping
        - ✅ PDPL compliance monitoring
        - ✅ International standards (ISO 27001, NIST 800-53, GDPR)
        - ✅ Real-time validation and alerting
        - ✅ Automated evidence collection
        """)
    
    with col2:
        # Compliance coverage chart
        coverage_data = get_compliance_coverage_data()
        fig_coverage = px.bar(
            coverage_data,
            x="framework",
            y="coverage",
            title="Framework Coverage %",
            color="coverage",
            color_continuous_scale="Blues"
        )
        fig_coverage.update_layout(height=300)
        st.plotly_chart(fig_coverage, use_container_width=True)

with tab2:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Vendor Risk Module")
        st.markdown("""
        Recognizing that third-party suppliers are a critical part of risk, the platform includes 
        a dedicated vendor risk management module.
        
        **Capabilities:**
        - 🔍 Automated vendor due diligence
        - 📝 Structured questionnaires aligned to NCA/SAMA requirements
        - 🤖 AI-powered compliance scoring
        - 📊 Continuous vendor monitoring
        - ⚠️ Risk-based vendor categorization
        - 📈 Vendor performance trending
        """)
    
    with col2:
        # Vendor risk distribution
        risk_levels = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
        risk_counts = [45, 30, 20, 5]
        
        fig_risk = px.pie(
            values=risk_counts,
            names=risk_levels,
            title="Vendor Risk Distribution",
            color_discrete_sequence=["#2e8b57", "#ffa500", "#ff6347", "#dc143c"]
        )
        fig_risk.update_layout(height=300)
        st.plotly_chart(fig_risk, use_container_width=True)

with tab3:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Reporting & Dashboard Layer")
        st.markdown("""
        All findings feed into a real-time reporting dashboard that is bilingual (Arabic/English) 
        and auditor-ready.
        
        **Features:**
        - 🌐 Bilingual interface (Arabic/English)
        - 📊 Real-time compliance monitoring
        - 📋 On-demand report generation
        - 🎯 Framework-specific dashboards
        - 👥 Role-based access control
        - 📤 Automated report distribution
        """)
    
    with col2:
        # Language support indicator
        languages = ["Arabic", "English"]
        support_level = [100, 100]
        
        fig_lang = px.bar(
            x=languages,
            y=support_level,
            title="Language Support",
            color=support_level,
            color_continuous_scale="Greens"
        )
        fig_lang.update_layout(height=300, yaxis_range=[0, 100])
        st.plotly_chart(fig_lang, use_container_width=True)

# Regulation Support Matrix
st.header("📜 Regulation Support Matrix")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Saudi Regulations (Built-in)")
    regulations = [
        {"name": "NCA Essential Cybersecurity Controls (v2.0)", "coverage": "100%", "status": "✅"},
        {"name": "SAMA Cybersecurity Framework", "coverage": "100%", "status": "✅"},
        {"name": "Personal Data Protection Law (PDPL)", "coverage": "100%", "status": "✅"},
        {"name": "Saudi Data & AI Authority Guidelines", "coverage": "95%", "status": "✅"}
    ]
    
    for reg in regulations:
        st.markdown(f"{reg['status']} **{reg['name']}** - {reg['coverage']}")

with col2:
    st.subheader("International Standards (Mapped)")
    intl_standards = [
        {"name": "ISO 27001:2022", "coverage": "100%", "status": "✅"},
        {"name": "NIST Cybersecurity Framework", "coverage": "100%", "status": "✅"},
        {"name": "GDPR", "coverage": "95%", "status": "✅"},
        {"name": "PCI DSS", "coverage": "90%", "status": "✅"}
    ]
    
    for std in intl_standards:
        st.markdown(f"{std['status']} **{std['name']}** - {std['coverage']}")

# Key Benefits
st.header("🎯 Key Benefits")

benefit_cols = st.columns(4)

with benefit_cols[0]:
    st.metric(
        label="Time Reduction",
        value="80%",
        delta="vs manual audits"
    )

with benefit_cols[1]:
    st.metric(
        label="Compliance Score",
        value="95%+",
        delta="average improvement"
    )

with benefit_cols[2]:
    st.metric(
        label="Cost Savings",
        value="60%",
        delta="in compliance costs"
    )

with benefit_cols[3]:
    st.metric(
        label="Audit Readiness",
        value="24/7",
        delta="continuous monitoring"
    )

# Use Cases
st.header("💼 Primary Use Cases")

use_case_tabs = st.tabs(["🏦 Banking & Finance", "🏛️ Government", "🏥 Healthcare", "🏢 Enterprise"])

with use_case_tabs[0]:
    st.markdown("""
    **Banking & Financial Services**
    - SAMA CSF compliance automation
    - PCI DSS payment card security
    - Anti-money laundering (AML) controls
    - Customer data protection (PDPL)
    - Continuous regulatory monitoring
    """)

with use_case_tabs[1]:
    st.markdown("""
    **Government Agencies**
    - NCA ECC v2.0 implementation
    - Critical infrastructure protection
    - Inter-agency compliance coordination
    - Public data security
    - National cybersecurity standards
    """)

with use_case_tabs[2]:
    st.markdown("""
    **Healthcare Sector**
    - Medical data protection
    - HIPAA-equivalent Saudi standards
    - Patient privacy compliance
    - Medical device security
    - Healthcare data governance
    """)

with use_case_tabs[3]:
    st.markdown("""
    **Enterprise Organizations**
    - Multi-framework compliance
    - Vendor risk management
    - Supply chain security
    - Data localization requirements
    - Business continuity planning
    """)

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("🏗️ Next: Architecture", use_container_width=True):
        st.switch_page("pages/2_Architecture.py")

with col3:
    if st.button("📊 View Market Analysis", use_container_width=True):
        st.switch_page("pages/4_Market_Analysis.py")
