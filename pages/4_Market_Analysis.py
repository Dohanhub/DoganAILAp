import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data import get_market_growth_data, get_sector_analysis_data, get_competitive_landscape

st.set_page_config(
    page_title="Market Analysis - Doğan AI Lab",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Market Analysis")
st.markdown("**Saudi Arabia's GRC market growth and industry landscape**")

# Market Overview
st.header("📈 Saudi GRC Market Growth")

market_data = get_market_growth_data()

col1, col2 = st.columns([2, 1])

with col1:
    # Market growth chart
    fig_growth = go.Figure()
    
    fig_growth.add_trace(go.Scatter(
        x=market_data['year'],
        y=market_data['market_size_usd_millions'],
        mode='lines+markers',
        name='Market Size (USD Millions)',
        line=dict(color='#1f4e79', width=3),
        marker=dict(size=8)
    ))
    
    fig_growth.update_layout(
        title="Saudi Arabia GRC Market Growth (2024-2033)",
        xaxis_title="Year",
        yaxis_title="Market Size (USD Millions)",
        height=400
    )
    
    st.plotly_chart(fig_growth, use_container_width=True)

with col2:
    st.subheader("Key Market Metrics")
    
    st.metric(
        label="2024 Market Size",
        value="$442.5M",
        delta="Base year"
    )
    
    st.metric(
        label="2033 Projected Size",
        value="$1.23B",
        delta="+178% growth"
    )
    
    st.metric(
        label="CAGR (2024-2033)",
        value="11.5%",
        delta="Strong growth trajectory"
    )
    
    st.metric(
        label="Vision 2030 Impact",
        value="High",
        delta="Regulatory driver"
    )

# Market Drivers
st.header("🚀 Market Growth Drivers")

driver_cols = st.columns(4)

with driver_cols[0]:
    st.markdown("""
    **🏛️ Regulatory Pressure**
    - New PDPL enforcement
    - NCA ECC v2.0 requirements
    - SAMA banking regulations
    - Vision 2030 compliance
    """)

with driver_cols[1]:
    st.markdown("""
    **💰 Digital Transformation**
    - Government digitization
    - E-commerce growth
    - Fintech expansion
    - Smart city initiatives
    """)

with driver_cols[2]:
    st.markdown("""
    **🔒 Cybersecurity Threats**
    - Increasing cyber attacks
    - Data breach costs
    - Reputation risks
    - Critical infrastructure protection
    """)

with driver_cols[3]:
    st.markdown("""
    **🌍 International Standards**
    - ISO 27001 adoption
    - GDPR-like requirements
    - Cross-border data flows
    - Multinational compliance
    """)

# Sector Analysis
st.header("🏢 Sector Analysis")

sector_data = get_sector_analysis_data()

sector_tabs = st.tabs(["🏦 Banking & Finance", "🏛️ Government", "🏥 Healthcare", "⚡ Energy & Utilities"])

with sector_tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Banking & Financial Services")
        st.markdown("""
        **Market Characteristics:**
        - 🏦 Largest GRC spending sector in Saudi Arabia
        - 📊 SAMA requirements drive 100% compliance needs
        - 💳 PCI-DSS for payment processing
        - 🌍 International banking standards
        
        **Pain Points:**
        - Multiple framework compliance (SAMA CSF, PCI-DSS, FATF)
        - Frequent regulatory audits
        - High consultant costs
        - Manual compliance processes
        
        **Market Size:** ~$180M (40% of total GRC market)
        """)
    
    with col2:
        # Banking compliance spending
        banking_spending = {
            "Regulatory Compliance": 45,
            "Risk Management": 25,
            "Audit & Assurance": 20,
            "Technology Solutions": 10
        }
        
        fig_banking = px.pie(
            values=list(banking_spending.values()),
            names=list(banking_spending.keys()),
            title="Banking GRC Spending Distribution (%)"
        )
        st.plotly_chart(fig_banking, use_container_width=True)

with sector_tabs[1]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Government Sector")
        st.markdown("""
        **Market Characteristics:**
        - 🏛️ Vision 2030 digital transformation mandate
        - 🔒 NCA ECC v2.0 comprehensive coverage required
        - 🌐 Critical infrastructure protection focus
        - 📊 Inter-agency coordination needs
        
        **Pain Points:**
        - Complex multi-agency compliance
        - Legacy system integration challenges
        - Limited Arabic-language solutions
        - Budget constraints with efficiency demands
        
        **Market Size:** ~$155M (35% of total GRC market)
        """)
    
    with col2:
        # Government priorities
        gov_priorities = ["Cybersecurity", "Data Protection", "Digital Services", "Infrastructure"]
        priority_scores = [95, 88, 82, 75]
        
        fig_gov = px.bar(
            x=gov_priorities,
            y=priority_scores,
            title="Government Compliance Priorities",
            color=priority_scores,
            color_continuous_scale="Blues"
        )
        fig_gov.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_gov, use_container_width=True)

with sector_tabs[2]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Healthcare Sector")
        st.markdown("""
        **Market Characteristics:**
        - 🏥 Rapid digitization of health records
        - 👥 Patient data privacy critical
        - 🔒 Medical device security requirements
        - 📊 Health insurance compliance
        
        **Pain Points:**
        - Patient data protection complexity
        - Medical device vulnerability management
        - Telemedicine security requirements
        - Integration with national health systems
        
        **Market Size:** ~$65M (15% of total GRC market)
        """)
    
    with col2:
        # Healthcare compliance areas
        health_areas = ["Patient Privacy", "Device Security", "Data Governance", "Audit Trails"]
        investment_levels = [40, 30, 20, 10]
        
        fig_health = px.pie(
            values=investment_levels,
            names=health_areas,
            title="Healthcare Compliance Investment (%)"
        )
        st.plotly_chart(fig_health, use_container_width=True)

with sector_tabs[3]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Energy & Utilities")
        st.markdown("""
        **Market Characteristics:**
        - ⚡ Critical infrastructure designation
        - 🛡️ SCADA and OT security requirements
        - 🌍 International energy partnerships
        - 📊 Environmental compliance tracking
        
        **Pain Points:**
        - OT/IT convergence security
        - Legacy industrial system protection
        - Supply chain risk management
        - Environmental regulation compliance
        
        **Market Size:** ~$45M (10% of total GRC market)
        """)
    
    with col2:
        # Energy sector risks
        energy_risks = ["Cyber Attacks", "Operational Failures", "Regulatory Changes", "Supply Chain"]
        risk_levels = [85, 70, 60, 55]
        
        fig_energy = px.bar(
            x=energy_risks,
            y=risk_levels,
            title="Energy Sector Risk Priorities",
            color=risk_levels,
            color_continuous_scale="Reds"
        )
        fig_energy.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_energy, use_container_width=True)

# Competitive Landscape
st.header("🏆 Competitive Landscape")

competitive_data = get_competitive_landscape()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Global Players in Saudi Market")
    
    global_vendors = [
        {"name": "RSA Archer", "market_share": 25, "saudi_localization": "Low"},
        {"name": "ServiceNow GRC", "market_share": 20, "saudi_localization": "Low"},
        {"name": "MetricStream", "market_share": 15, "saudi_localization": "Medium"},
        {"name": "IBM OpenPages", "market_share": 12, "saudi_localization": "Low"},
        {"name": "Others", "market_share": 28, "saudi_localization": "Varies"}
    ]
    
    for vendor in global_vendors:
        st.markdown(f"**{vendor['name']}**: {vendor['market_share']}% market share, {vendor['saudi_localization']} Saudi localization")

with col2:
    st.subheader("Market Share Distribution")
    
    vendor_names = [v["name"] for v in global_vendors]
    market_shares = [v["market_share"] for v in global_vendors]
    
    fig_market_share = px.pie(
        values=market_shares,
        names=vendor_names,
        title="GRC Platform Market Share in Saudi Arabia"
    )
    st.plotly_chart(fig_market_share, use_container_width=True)

# Competitive Advantages
st.header("🎯 Doğan AI Lab Competitive Advantages")

advantage_cols = st.columns(3)

with advantage_cols[0]:
    st.subheader("🌍 Localization")
    st.markdown("""
    **Saudi-First Design:**
    - ✅ 100% Arabic language support
    - ✅ Pre-built Saudi regulatory frameworks
    - ✅ Cultural adaptation
    - ✅ Local compliance expertise
    
    **vs Competitors:**
    - ❌ English-only interfaces
    - ❌ Costly customization required
    - ❌ Limited local framework support
    """)

with advantage_cols[1]:
    st.subheader("🤖 AI Innovation")
    st.markdown("""
    **Advanced Analytics:**
    - ✅ GPU-accelerated AI models
    - ✅ Predictive compliance insights
    - ✅ Automated risk assessment
    - ✅ Continuous learning systems
    
    **vs Competitors:**
    - ❌ Rule-based systems only
    - ❌ Limited AI capabilities
    - ❌ Manual analysis required
    """)

with advantage_cols[2]:
    st.subheader("⚡ Performance")
    st.markdown("""
    **On-Premises Power:**
    - ✅ Dedicated hardware appliance
    - ✅ Data sovereignty guaranteed
    - ✅ Real-time processing
    - ✅ Scalable architecture
    
    **vs Competitors:**
    - ❌ Cloud-only limitations
    - ❌ Data residency concerns
    - ❌ Performance bottlenecks
    """)

# Market Opportunity
st.header("💡 Market Opportunity Analysis")

opportunity_data = {
    "Market Segment": ["Underserved SMEs", "Government Agencies", "Healthcare Digitization", "Fintech Growth"],
    "Size (USD Millions)": [120, 155, 65, 85],
    "Growth Rate (%)": [15, 12, 18, 25],
    "Doğan Advantage": ["High", "Very High", "High", "Medium"]
}

opportunity_df = pd.DataFrame(opportunity_data)

fig_opportunity = px.scatter(
    opportunity_df,
    x="Size (USD Millions)",
    y="Growth Rate (%)",
    size="Size (USD Millions)",
    color="Doğan Advantage",
    hover_name="Market Segment",
    title="Market Opportunity Matrix",
    color_discrete_map={"Very High": "#1f4e79", "High": "#4a90e2", "Medium": "#87ceeb"}
)

fig_opportunity.update_layout(height=400)
st.plotly_chart(fig_opportunity, use_container_width=True)

# Revenue Projections
st.header("💰 Revenue Projections")

revenue_cols = st.columns(4)

with revenue_cols[0]:
    st.metric(
        label="Year 1 Target",
        value="$5M",
        delta="Initial market penetration"
    )

with revenue_cols[1]:
    st.metric(
        label="Year 3 Target",
        value="$25M",
        delta="Market expansion"
    )

with revenue_cols[2]:
    st.metric(
        label="Year 5 Target",
        value="$75M",
        delta="Market leadership"
    )

with revenue_cols[3]:
    st.metric(
        label="Market Share Target",
        value="15%",
        delta="by Year 5"
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⚙️ Back: Technical Stack", use_container_width=True):
        st.switch_page("pages/3_Technical_Stack.py")

with col2:
    if st.button("📜 Next: Compliance Frameworks", use_container_width=True):
        st.switch_page("pages/5_Compliance_Frameworks.py")

with col3:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
