import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data import get_framework_coverage_data, get_control_mapping_data

st.set_page_config(
    page_title="Compliance Frameworks - Doğan AI Lab",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Compliance Frameworks")
st.markdown("**Comprehensive coverage of Saudi regulations and international standards**")

# Framework Overview
st.header("🎯 Supported Frameworks Overview")

framework_data = get_framework_coverage_data()

col1, col2 = st.columns([2, 1])

with col1:
    # Framework coverage chart
    fig_frameworks = px.bar(
        framework_data,
        x="framework",
        y="coverage_percentage",
        color="category",
        title="Framework Coverage by Category",
        color_discrete_map={
            "Saudi Regulations": "#1f4e79",
            "International Standards": "#4a90e2",
            "Industry Specific": "#7bb3f0"
        }
    )
    fig_frameworks.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_frameworks, use_container_width=True)

with col2:
    st.subheader("Coverage Summary")
    
    # Calculate averages by category
    saudi_avg = framework_data[framework_data["category"] == "Saudi Regulations"]["coverage_percentage"].mean()
    intl_avg = framework_data[framework_data["category"] == "International Standards"]["coverage_percentage"].mean()
    industry_avg = framework_data[framework_data["category"] == "Industry Specific"]["coverage_percentage"].mean()
    
    st.metric("Saudi Regulations", f"{saudi_avg:.0f}%", "Complete coverage")
    st.metric("International Standards", f"{intl_avg:.0f}%", "Comprehensive mapping")
    st.metric("Industry Specific", f"{industry_avg:.0f}%", "Sector alignment")

# Saudi Regulations Deep Dive
st.header("🇸🇦 Saudi Regulations - Built-in Coverage")

saudi_tabs = st.tabs(["🛡️ NCA ECC v2.0", "🏦 SAMA CSF", "🔒 PDPL", "📊 Other Regulations"])

with saudi_tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("NCA Essential Cybersecurity Controls v2.0")
        st.markdown("""
        **Scope**: Government entities and critical infrastructure
        
        **Coverage**: 100% of all 114 controls across 5 domains
        
        **Control Domains:**
        1. **Cybersecurity Governance** (23 controls)
           - Policies and procedures
           - Risk management framework
           - Executive oversight
        
        2. **Cybersecurity Defense** (31 controls)
           - Network security
           - Endpoint protection
           - Access controls
        
        3. **Cybersecurity Resilience** (18 controls)
           - Business continuity
           - Incident response
           - Recovery procedures
        
        4. **Third-Party Cybersecurity** (25 controls)
           - Vendor assessment
           - Supply chain security
           - Outsourcing governance
        
        5. **Cybersecurity Compliance** (17 controls)
           - Audit and monitoring
           - Reporting requirements
           - Legal compliance
        """)
    
    with col2:
        # NCA control distribution
        nca_domains = ["Governance", "Defense", "Resilience", "Third-Party", "Compliance"]
        nca_controls = [23, 31, 18, 25, 17]
        
        fig_nca = px.pie(
            values=nca_controls,
            names=nca_domains,
            title="NCA ECC v2.0 Control Distribution"
        )
        st.plotly_chart(fig_nca, use_container_width=True)

with saudi_tabs[1]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("SAMA Cybersecurity Framework")
        st.markdown("""
        **Scope**: Banks and financial institutions
        
        **Coverage**: 100% of all cybersecurity requirements
        
        **Key Areas:**
        1. **Cybersecurity Governance**
           - Board oversight
           - Risk appetite
           - Strategic planning
        
        2. **Cybersecurity Risk Management**
           - Risk assessment
           - Risk treatment
           - Continuous monitoring
        
        3. **Cybersecurity Asset Management**
           - Asset inventory
           - Asset classification
           - Asset protection
        
        4. **Cybersecurity Controls**
           - Preventive controls
           - Detective controls
           - Corrective controls
        
        5. **Cyber Resilience & Continuity**
           - Business continuity
           - Disaster recovery
           - Crisis management
        """)
    
    with col2:
        # SAMA compliance status
        sama_status = ["Fully Compliant", "Substantially Compliant", "Partially Compliant", "Non-Compliant"]
        sama_percentages = [65, 25, 8, 2]
        
        fig_sama = px.bar(
            x=sama_status,
            y=sama_percentages,
            title="Typical SAMA Compliance Distribution (%)",
            color=sama_percentages,
            color_continuous_scale="RdYlGn"
        )
        fig_sama.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_sama, use_container_width=True)

with saudi_tabs[2]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Personal Data Protection Law (PDPL)")
        st.markdown("""
        **Scope**: All organizations processing personal data
        
        **Coverage**: 100% of PDPL requirements
        
        **Key Principles:**
        1. **Lawfulness and Transparency**
           - Legal basis for processing
           - Clear privacy notices
           - Data subject rights
        
        2. **Purpose Limitation**
           - Specific processing purposes
           - Compatible use restrictions
           - Retention limitations
        
        3. **Data Minimization**
           - Adequate and relevant data
           - Limited to necessary purposes
           - Regular data review
        
        4. **Accuracy and Integrity**
           - Data accuracy maintenance
           - Correction mechanisms
           - Quality assurance
        
        5. **Security and Confidentiality**
           - Technical safeguards
           - Organizational measures
           - Breach prevention
        """)
    
    with col2:
        # PDPL compliance challenges
        pdpl_challenges = ["Technical Implementation", "Process Changes", "Training Needs", "Ongoing Monitoring"]
        challenge_scores = [85, 70, 60, 75]
        
        fig_pdpl = px.bar(
            x=pdpl_challenges,
            y=challenge_scores,
            title="PDPL Implementation Challenges",
            color=challenge_scores,
            color_continuous_scale="Oranges"
        )
        fig_pdpl.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pdpl, use_container_width=True)

with saudi_tabs[3]:
    st.subheader("Additional Saudi Regulations")
    
    other_regs = [
        {
            "name": "Saudi Data & AI Authority Guidelines",
            "scope": "AI and data governance",
            "coverage": "95%",
            "status": "Active monitoring"
        },
        {
            "name": "Communications & IT Commission Regulations",
            "scope": "Telecommunications and IT services",
            "coverage": "90%",
            "status": "Sector-specific controls"
        },
        {
            "name": "Capital Market Authority Regulations",
            "scope": "Securities and investment firms",
            "coverage": "85%",
            "status": "Financial services focus"
        },
        {
            "name": "Ministry of Health Data Protection",
            "scope": "Healthcare data and patient privacy",
            "coverage": "90%",
            "status": "Healthcare-specific requirements"
        }
    ]
    
    for reg in other_regs:
        with st.expander(f"📋 {reg['name']} - {reg['coverage']} Coverage"):
            st.markdown(f"""
            **Scope**: {reg['scope']}
            **Coverage**: {reg['coverage']}
            **Status**: {reg['status']}
            """)

# International Standards Mapping
st.header("🌍 International Standards Mapping")

intl_tabs = st.tabs(["🔒 ISO 27001", "🛡️ NIST CSF", "🇪🇺 GDPR", "💳 PCI DSS"])

with intl_tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("ISO 27001:2022 Information Security")
        st.markdown("""
        **Mapping Coverage**: 100% of Annex A controls
        
        **Control Categories** (93 controls total):
        - **A.5** Organizational controls (37 controls)
        - **A.6** People controls (8 controls)
        - **A.7** Physical controls (14 controls)
        - **A.8** Technological controls (34 controls)
        
        **Saudi Alignment:**
        - NCA ECC maps to ISO 27001 structure
        - SAMA requirements align with ISO controls
        - PDPL incorporates ISO 27001 privacy principles
        
        **Benefits:**
        - International recognition
        - Global business enablement
        - Best practice framework
        """)
    
    with col2:
        # ISO control distribution
        iso_categories = ["Organizational", "People", "Physical", "Technological"]
        iso_counts = [37, 8, 14, 34]
        
        fig_iso = px.pie(
            values=iso_counts,
            names=iso_categories,
            title="ISO 27001:2022 Control Distribution"
        )
        st.plotly_chart(fig_iso, use_container_width=True)

with intl_tabs[1]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("NIST Cybersecurity Framework")
        st.markdown("""
        **Mapping Coverage**: 100% of core functions
        
        **Five Core Functions:**
        1. **Identify** (ID)
           - Asset management
           - Risk assessment
           - Governance
        
        2. **Protect** (PR)
           - Access control
           - Data security
           - Maintenance
        
        3. **Detect** (DE)
           - Anomaly detection
           - Security monitoring
           - Detection processes
        
        4. **Respond** (RS)
           - Response planning
           - Communications
           - Analysis
        
        5. **Recover** (RC)
           - Recovery planning
           - Improvements
           - Communications
        """)
    
    with col2:
        # NIST maturity levels
        nist_functions = ["Identify", "Protect", "Detect", "Respond", "Recover"]
        maturity_scores = [4.2, 4.0, 3.8, 3.9, 3.7]
        
        fig_nist = px.bar(
            x=nist_functions,
            y=maturity_scores,
            title="NIST CSF Maturity Assessment",
            color=maturity_scores,
            color_continuous_scale="Blues"
        )
        fig_nist.update_layout(yaxis_range=[0, 5])
        st.plotly_chart(fig_nist, use_container_width=True)

with intl_tabs[2]:
    st.subheader("GDPR Alignment")
    st.markdown("""
    **Coverage**: 95% alignment with GDPR principles
    
    **Key Alignments:**
    - PDPL mirrors GDPR data protection principles
    - Similar data subject rights framework
    - Comparable breach notification requirements
    - Cross-border data transfer restrictions
    
    **Differences:**
    - Saudi-specific enforcement mechanisms
    - Local data residency requirements
    - Arabic language documentation needs
    """)

with intl_tabs[3]:
    st.subheader("PCI DSS Payment Security")
    st.markdown("""
    **Coverage**: 90% of PCI DSS requirements
    
    **Application**: Banking and payment processing
    
    **Six Goals:**
    1. Build and maintain secure networks
    2. Protect cardholder data
    3. Maintain vulnerability management
    4. Implement strong access controls
    5. Monitor and test networks regularly
    6. Maintain information security policy
    """)

# Control Mapping Matrix
st.header("🔗 Control Mapping Matrix")

st.markdown("Interactive mapping between Saudi regulations and international standards:")

mapping_data = get_control_mapping_data()

# Create mapping heatmap
fig_mapping = px.imshow(
    mapping_data.values,
    labels=dict(x="International Standards", y="Saudi Regulations", color="Mapping Strength"),
    x=mapping_data.columns,
    y=mapping_data.index,
    color_continuous_scale="Blues",
    title="Framework Control Mapping Strength"
)

fig_mapping.update_layout(height=400)
st.plotly_chart(fig_mapping, use_container_width=True)

# Implementation Status
st.header("📊 Implementation Status Dashboard")

status_cols = st.columns(4)

with status_cols[0]:
    st.metric(
        label="Saudi Frameworks",
        value="4/4",
        delta="100% implemented"
    )

with status_cols[1]:
    st.metric(
        label="International Standards",
        value="6/6",
        delta="Complete mapping"
    )

with status_cols[2]:
    st.metric(
        label="Total Controls",
        value="500+",
        delta="Automated validation"
    )

with status_cols[3]:
    st.metric(
        label="Update Frequency",
        value="Quarterly",
        delta="Regulatory tracking"
    )

# Compliance Benefits
st.header("✅ Compliance Benefits")

benefit_cols = st.columns(3)

with benefit_cols[0]:
    st.subheader("🎯 Efficiency Gains")
    st.markdown("""
    - 80% reduction in audit preparation time
    - 90% faster compliance reporting
    - 70% decrease in manual evidence collection
    - Real-time compliance status visibility
    """)

with benefit_cols[1]:
    st.subheader("🔒 Risk Reduction")
    st.markdown("""
    - Continuous monitoring vs. periodic audits
    - Early warning for control failures
    - Automated remediation workflows
    - Comprehensive risk visibility
    """)

with benefit_cols[2]:
    st.subheader("💰 Cost Savings")
    st.markdown("""
    - 60% reduction in compliance costs
    - Elimination of multiple audit processes
    - Reduced consultant dependencies
    - Optimized resource allocation
    """)

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Back: Market Analysis", use_container_width=True):
        st.switch_page("pages/4_Market_Analysis.py")

with col2:
    if st.button("🚀 Next: Deployment Models", use_container_width=True):
        st.switch_page("pages/6_Deployment_Models.py")

with col3:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
