import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data import get_deployment_comparison_data, get_scaling_projections

st.set_page_config(
    page_title="Deployment Models - Doğan AI Lab",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Deployment Models")
st.markdown("**Flexible deployment options from single appliance to enterprise-scale clusters**")

# Deployment Overview
st.header("📋 Deployment Model Overview")

st.markdown("""
Doğan AI Lab supports three main deployment scenarios to accommodate organizations of different sizes and requirements. 
Each model maintains the same core functionality while providing different levels of scale, redundancy, and performance.
""")

# Model Comparison
deployment_data = get_deployment_comparison_data()

fig_comparison = px.bar(
    deployment_data,
    x="model",
    y=["users", "appliances", "storage_tb"],
    title="Deployment Model Comparison",
    barmode="group"
)

fig_comparison.update_layout(height=400)
st.plotly_chart(fig_comparison, use_container_width=True)

# Detailed Model Breakdown
st.header("🔍 Deployment Model Details")

model_tabs = st.tabs(["💻 MVP (Single Appliance)", "🔗 Pilot Cluster (2-3 Nodes)", "🏢 Production at Scale"])

with model_tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("MVP - Single Appliance Deployment")
        st.markdown("""
        **Target Organizations:**
        - Mid-sized enterprises (100-500 employees)
        - Single-location businesses
        - Initial pilot implementations
        - Budget-conscious deployments
        
        **Hardware Specifications:**
        - 🖥️ **Single Compliance Appliance**
        - 💾 **128GB RAM** (ECC memory)
        - 💽 **10TB NVMe SSD** storage
        - 🎮 **Dual NVIDIA GPUs** for AI acceleration
        - 🌐 **High-speed network connectivity**
        
        **Capabilities:**
        - Complete compliance workload for mid-sized org
        - All frameworks supported
        - Full AI analytics capabilities
        - Bilingual dashboard access
        - Up to 500 concurrent users
        
        **Timeline:**
        - ✅ Hardware secured and arriving in 6 weeks
        - ✅ Software stack ready for deployment
        - ✅ Initial pilot customers identified
        """)
    
    with col2:
        # MVP metrics
        mvp_metrics = {
            "Users Supported": 500,
            "Storage (TB)": 10,
            "Processing Power": 85,
            "Redundancy": 0
        }
        
        fig_mvp = px.bar(
            x=list(mvp_metrics.keys()),
            y=list(mvp_metrics.values()),
            title="MVP Capabilities",
            color=list(mvp_metrics.values()),
            color_continuous_scale="Blues"
        )
        fig_mvp.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig_mvp, use_container_width=True)
        
        # Deployment timeline
        st.subheader("MVP Timeline")
        st.markdown("""
        **Week 1-6**: Hardware arrival & setup
        **Week 7-8**: Software deployment
        **Week 9-10**: Initial customer pilot
        **Week 11-12**: Feedback integration
        """)

with model_tabs[1]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Pilot Cluster - 2-3 Node Deployment")
        st.markdown("""
        **Target Organizations:**
        - Large enterprises (500-2000 employees)
        - Multi-location businesses
        - High availability requirements
        - Proof-of-concept for enterprise scale
        
        **Architecture:**
        - 🔗 **2-3 Clustered Appliances**
        - 🔄 **High Availability & Failover**
        - 📂 **Data Replication** across nodes
        - ⚖️ **Load Balancing** for optimal performance
        - 🛡️ **Automatic Failover** in case of node failure
        
        **Enhanced Capabilities:**
        - Zero-downtime operations
        - Distributed processing power
        - Improved response times
        - Enterprise-grade resilience
        - Up to 2,000 concurrent users
        
        **Use Cases:**
        - Large bank proof-of-concept
        - Government agency pilot
        - Multi-department enterprise deployment
        - Disaster recovery testing
        """)
    
    with col2:
        # Cluster metrics
        cluster_metrics = {
            "Users Supported": 2000,
            "Storage (TB)": 30,
            "Processing Power": 95,
            "Redundancy": 100
        }
        
        fig_cluster = px.bar(
            x=list(cluster_metrics.keys()),
            y=list(cluster_metrics.values()),
            title="Cluster Capabilities",
            color=list(cluster_metrics.values()),
            color_continuous_scale="Greens"
        )
        fig_cluster.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig_cluster, use_container_width=True)
        
        # High availability visualization
        ha_components = ["Node 1", "Node 2", "Node 3", "Load Balancer"]
        availability = [99.9, 99.9, 99.9, 99.99]
        
        fig_ha = px.bar(
            x=ha_components,
            y=availability,
            title="High Availability (%)",
            color=availability,
            color_continuous_scale="RdYlGn"
        )
        fig_ha.update_layout(height=250, yaxis_range=[99, 100])
        st.plotly_chart(fig_ha, use_container_width=True)

with model_tabs[2]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Production at Scale - Enterprise Deployment")
        st.markdown("""
        **Target Organizations:**
        - Large enterprises (2000+ employees)
        - Government ministries
        - Multi-national corporations
        - Critical infrastructure operators
        
        **Deployment Options:**
        
        **🌐 Distributed Fleet:**
        - One appliance per region/department
        - Centralized management console
        - Enterprise-wide compliance visibility
        - Regional data sovereignty
        
        **☁️ Hybrid Cloud Integration:**
        - On-premises appliances + cloud services
        - Existing private cloud integration
        - Kubernetes cluster deployment
        - Multi-cloud redundancy
        
        **🏢 Data Center Deployment:**
        - Rack-mounted appliances
        - Dedicated compliance infrastructure
        - Maximum performance configuration
        - Enterprise SLA guarantees
        
        **Capabilities:**
        - Unlimited user scaling
        - Global deployment support
        - 24/7 enterprise support
        - Custom integration services
        """)
    
    with col2:
        # Enterprise metrics
        enterprise_metrics = {
            "Users": "Unlimited",
            "Storage": "Unlimited",
            "Availability": "99.99%",
            "Support": "24/7"
        }
        
        for metric, value in enterprise_metrics.items():
            st.metric(metric, value)
        
        # Scaling projections
        scaling_data = get_scaling_projections()
        
        fig_scaling = px.line(
            scaling_data,
            x="users",
            y="appliances_needed",
            title="Scaling Requirements",
            markers=True
        )
        fig_scaling.update_layout(height=250)
        st.plotly_chart(fig_scaling, use_container_width=True)

# Deployment Scenarios
st.header("🎯 Real-World Deployment Scenarios")

scenario_cols = st.columns(2)

with scenario_cols[0]:
    st.subheader("🏦 Large Saudi Bank")
    with st.expander("Click to view deployment details"):
        st.markdown("""
        **Organization**: Major Saudi commercial bank
        **Size**: 5,000 employees, 200 branches
        **Requirements**: SAMA CSF, PCI DSS, PDPL compliance
        
        **Recommended Deployment**: Production at Scale
        - 🏢 **3 regional data centers** (Riyadh, Jeddah, Dammam)
        - 🔗 **2 appliances per data center** (6 total)
        - 🛡️ **Active-active clustering** for 99.99% availability
        - 📊 **Centralized dashboard** for enterprise view
        
        **Benefits**:
        - Regional failover capability
        - Compliance with data residency requirements
        - 24/7 operations support
        - Automated SAMA reporting
        """)

with scenario_cols[1]:
    st.subheader("🏛️ Government Ministry")
    with st.expander("Click to view deployment details"):
        st.markdown("""
        **Organization**: Saudi government ministry
        **Size**: 2,000 employees, multiple agencies
        **Requirements**: NCA ECC v2.0, PDPL compliance
        
        **Recommended Deployment**: Pilot Cluster
        - 🏢 **Central government facility**
        - 🔗 **3-node cluster** for high availability
        - 🌐 **Secure government network** integration
        - 📊 **Arabic-first interface** for all users
        
        **Benefits**:
        - Government-grade security
        - Complete NCA ECC coverage
        - Inter-agency compliance coordination
        - Automated audit preparation
        """)

# Cost Comparison
st.header("💰 Total Cost of Ownership")

cost_data = {
    "Deployment Model": ["MVP", "Pilot Cluster", "Production Scale"],
    "Initial Investment": [150, 400, 1000],
    "Annual Operating": [50, 120, 300],
    "3-Year TCO": [300, 760, 1900]
}

cost_df = pd.DataFrame(cost_data)

fig_cost = px.bar(
    cost_df,
    x="Deployment Model",
    y=["Initial Investment", "Annual Operating"],
    title="Cost Comparison (USD Thousands)",
    barmode="group"
)

fig_cost.update_layout(height=400)
st.plotly_chart(fig_cost, use_container_width=True)

# Migration Path
st.header("🔄 Migration & Upgrade Path")

st.markdown("""
Organizations can start with any deployment model and seamlessly upgrade as requirements grow:
""")

migration_cols = st.columns(3)

with migration_cols[0]:
    st.markdown("""
    **MVP → Pilot Cluster**
    - Add 1-2 additional appliances
    - Enable clustering software
    - Migrate data with zero downtime
    - Timeline: 2-4 weeks
    """)

with migration_cols[1]:
    st.markdown("""
    **Pilot → Production**
    - Scale to distributed architecture
    - Add regional deployments
    - Implement enterprise features
    - Timeline: 4-8 weeks
    """)

with migration_cols[2]:
    st.markdown("""
    **Continuous Evolution**
    - Regular software updates
    - Hardware refresh cycles
    - Capacity expansion
    - Feature enhancements
    """)

# Selection Guide
st.header("🎯 Deployment Selection Guide")

selection_questions = [
    {
        "question": "How many users will access the system?",
        "mvp": "< 500 users",
        "cluster": "500 - 2,000 users",
        "enterprise": "2,000+ users"
    },
    {
        "question": "What is your availability requirement?",
        "mvp": "99% (8.7 hours downtime/year)",
        "cluster": "99.9% (52 minutes downtime/year)",
        "enterprise": "99.99% (5 minutes downtime/year)"
    },
    {
        "question": "Do you need high availability?",
        "mvp": "Single point of failure acceptable",
        "cluster": "Automatic failover required",
        "enterprise": "Zero downtime operations"
    },
    {
        "question": "What is your budget range?",
        "mvp": "$150K - $300K (3 years)",
        "cluster": "$400K - $760K (3 years)",
        "enterprise": "$1M+ (3 years)"
    }
]

for i, q in enumerate(selection_questions):
    st.subheader(f"Q{i+1}: {q['question']}")
    
    option_cols = st.columns(3)
    with option_cols[0]:
        st.info(f"**MVP**: {q['mvp']}")
    with option_cols[1]:
        st.success(f"**Cluster**: {q['cluster']}")
    with option_cols[2]:
        st.warning(f"**Enterprise**: {q['enterprise']}")

# Quick Assessment Tool
st.header("⚡ Quick Deployment Assessment")

with st.form("deployment_assessment"):
    st.markdown("Answer these questions to get a personalized deployment recommendation:")
    
    org_size = st.selectbox(
        "Organization size:",
        ["Small (< 100 employees)", "Medium (100-500)", "Large (500-2000)", "Enterprise (2000+)"]
    )
    
    availability_req = st.selectbox(
        "Availability requirement:",
        ["Standard (99%)", "High (99.9%)", "Mission Critical (99.99%)"]
    )
    
    budget_range = st.selectbox(
        "Budget range (3-year TCO):",
        ["< $500K", "$500K - $1M", "> $1M"]
    )
    
    compliance_urgency = st.selectbox(
        "Compliance timeline:",
        ["Immediate (< 3 months)", "Near-term (3-6 months)", "Long-term (6+ months)"]
    )
    
    submitted = st.form_submit_button("Get Recommendation")
    
    if submitted:
        # Simple recommendation logic
        if org_size.startswith("Small") or org_size.startswith("Medium"):
            recommendation = "MVP (Single Appliance)"
            details = "Perfect for your organization size with room to grow"
        elif org_size.startswith("Large") and availability_req != "Mission Critical":
            recommendation = "Pilot Cluster (2-3 Nodes)"
            details = "Ideal balance of performance and availability for large organizations"
        else:
            recommendation = "Production at Scale"
            details = "Enterprise-grade deployment for maximum performance and availability"
        
        st.success(f"**Recommended Deployment**: {recommendation}")
        st.info(f"**Rationale**: {details}")

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📜 Back: Compliance Frameworks", use_container_width=True):
        st.switch_page("pages/5_Compliance_Frameworks.py")

with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")

with col3:
    if st.button("📋 Product Overview", use_container_width=True):
        st.switch_page("pages/1_Product_Overview.py")
