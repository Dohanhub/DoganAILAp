import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.data import get_architecture_layers_data, get_hardware_specs_data

st.set_page_config(
    page_title="Architecture - Doğan AI Lab",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Architecture & Hardware Stack")
st.markdown("**Layered system design from hardware appliance to user dashboard**")

# Architecture Overview
st.header("🏢 Layered System Design")

st.markdown("""
The platform architecture is designed in layers, from the physical appliance up to the user dashboard. 
This modular architecture ensures each layer can evolve independently and makes the system deployable 
in various models.
""")

# Architecture Diagram
st.subheader("📊 Architecture Layers Visualization")

layers_data = get_architecture_layers_data()

fig_arch = go.Figure()

# Create stacked architecture visualization
colors = ['#1f4e79', '#2d5aa0', '#4a90e2', '#7bb3f0']
y_positions = [0, 1, 2, 3]

for i, layer in enumerate(layers_data):
    fig_arch.add_trace(go.Bar(
        x=[1],
        y=[1],
        name=layer['name'],
        orientation='v',
        marker_color=colors[i],
        text=f"<b>{layer['name']}</b><br>{layer['description']}",
        textposition='inside',
        textfont=dict(color='white', size=12),
        base=y_positions[i],
        width=0.8
    ))

fig_arch.update_layout(
    title="Doğan AI Lab - Layered Architecture",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    height=500,
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig_arch, use_container_width=True)

# Detailed Layer Breakdown
st.header("🔍 Layer Details")

layer_tabs = st.tabs(["🖥️ Hardware Layer", "🐳 Services & Containerization", "🤖 Compliance Engine & AI", "🌐 Reporting & Dashboard"])

with layer_tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Hardware Layer - Compliance Validation Appliance")
        st.markdown("""
        Doğan AI Lab runs on a dedicated on-premises server optimized for AI and compliance workloads.
        
        **MVP Hardware Specifications:**
        - 💾 **Memory**: 128 GB RAM (ECC)
        - 💽 **Storage**: 10 TB NVMe SSD
        - 🎮 **GPU**: Dual NVIDIA GPUs
        - 🔧 **CPU**: Enterprise-grade multi-core processor
        - 🌐 **Network**: High-speed Ethernet connectivity
        - 🔒 **Security**: Hardware-level encryption
        
        This enterprise-grade hardware ensures the platform can store years of audit data 
        and run heavy analytics locally with complete data sovereignty.
        """)
    
    with col2:
        # Hardware specs visualization
        specs_data = get_hardware_specs_data()
        
        fig_specs = px.bar(
            specs_data,
            x="component",
            y="capacity",
            title="Hardware Specifications",
            color="component",
            text="capacity"
        )
        fig_specs.update_layout(height=400)
        fig_specs.update_traces(textposition='outside')
        st.plotly_chart(fig_specs, use_container_width=True)

with layer_tabs[1]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Services & Containerization Layer")
        st.markdown("""
        The platform's software is fully containerized using Docker and orchestrated by Kubernetes.
        
        **Key Services:**
        - 🐍 **Backend API**: Python FastAPI application
        - 🗃️ **Database**: PostgreSQL for compliance data
        - 🔍 **Search Engine**: Elasticsearch for audit logs
        - 📊 **Analytics**: Real-time data processing
        - 🔐 **Auth Service**: Identity and access management
        - 📡 **Message Queue**: Asynchronous task processing
        
        **Benefits:**
        - Isolated environments for reliability
        - Easy scaling and updates
        - Consistent deployment across environments
        - Self-healing capabilities
        """)
    
    with col2:
        # Container health status
        services = ["API Server", "Database", "Search Engine", "Analytics", "Auth Service", "Message Queue"]
        health_status = ["Healthy", "Healthy", "Healthy", "Healthy", "Healthy", "Healthy"]
        
        fig_health = px.pie(
            names=health_status,
            title="Service Health Status",
            color_discrete_map={"Healthy": "#2e8b57", "Warning": "#ffa500", "Critical": "#dc143c"}
        )
        fig_health.update_layout(height=300)
        st.plotly_chart(fig_health, use_container_width=True)

with layer_tabs[2]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Compliance Engine & AI Layer")
        st.markdown("""
        The heart of the platform – the compliance rules engine and AI analytics.
        
        **Compliance Rules Engine:**
        - 📋 Machine-readable control definitions
        - ⚡ Real-time validation methods
        - 🔄 Automated evidence collection
        - 📊 Risk scoring algorithms
        
        **AI Analytics:**
        - 🧠 Machine learning for anomaly detection
        - 📈 Predictive compliance modeling
        - 🎯 Risk pattern recognition
        - 📉 Trend analysis and forecasting
        
        **GPU Acceleration:**
        - Deep learning models for compliance prediction
        - Time-series analysis of compliance scores
        - Early warning system for control failures
        """)
    
    with col2:
        # AI model performance
        ai_metrics = {
            "Accuracy": 95,
            "Precision": 92,
            "Recall": 89,
            "F1-Score": 90
        }
        
        fig_ai = px.bar(
            x=list(ai_metrics.keys()),
            y=list(ai_metrics.values()),
            title="AI Model Performance (%)",
            color=list(ai_metrics.values()),
            color_continuous_scale="Blues"
        )
        fig_ai.update_layout(height=300, yaxis_range=[0, 100])
        st.plotly_chart(fig_ai, use_container_width=True)

with layer_tabs[3]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Reporting & Dashboard Layer")
        st.markdown("""
        User-facing layer with web-based dashboard built with React.js.
        
        **Dashboard Features:**
        - 🌐 Bilingual interface (Arabic/English)
        - 📊 Real-time compliance status
        - 👥 Role-based access control
        - 📱 Responsive design for all devices
        - 📈 Interactive charts and visualizations
        - 📋 Customizable report templates
        
        **User Roles:**
        - 👔 Compliance Officers
        - 🔧 IT Administrators
        - 📊 Auditors
        - 👨‍💼 Executive Management
        """)
    
    with col2:
        # User activity
        user_roles = ["Compliance Officers", "IT Admins", "Auditors", "Executives"]
        activity_levels = [85, 70, 45, 30]
        
        fig_users = px.bar(
            x=user_roles,
            y=activity_levels,
            title="User Activity Levels (%)",
            color=activity_levels,
            color_continuous_scale="Greens"
        )
        fig_users.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig_users, use_container_width=True)

# Hardware Configurations
st.header("⚙️ Hardware Configurations & Deployment Models")

config_cols = st.columns(3)

with config_cols[0]:
    st.subheader("MVP (Single Appliance)")
    st.markdown("""
    **Target**: Mid-sized organizations
    
    **Specifications:**
    - 🖥️ Single compliance appliance
    - 💾 128GB RAM, 10TB SSD
    - 🎮 Dual GPU configuration
    - 👥 Up to 500 users
    - 📊 Complete compliance workload
    
    **Timeline**: MVP hardware arriving in 6 weeks
    """)
    
    st.metric("Supported Users", "500", "per appliance")

with config_cols[1]:
    st.subheader("Pilot Cluster (2-3 Nodes)")
    st.markdown("""
    **Target**: Large organizations POC
    
    **Specifications:**
    - 🔗 2-3 clustered appliances
    - 🔄 High availability & failover
    - 📂 Data replication for resilience
    - ⚖️ Load balancing capabilities
    - 👥 Up to 2,000 users
    
    **Benefits**: Enterprise-scale testing
    """)
    
    st.metric("Supported Users", "2,000", "clustered deployment")

with config_cols[2]:
    st.subheader("Production at Scale")
    st.markdown("""
    **Target**: Enterprise/Government
    
    **Specifications:**
    - 🌐 Distributed fleet of appliances
    - 🏢 One appliance per region/department
    - ☁️ Hybrid cloud integration
    - 📈 Enterprise-wide visibility
    - 👥 Unlimited scaling
    
    **Use Cases**: Nationwide deployment
    """)
    
    st.metric("Supported Users", "Unlimited", "distributed architecture")

# Performance Metrics
st.header("📊 Performance Characteristics")

perf_cols = st.columns(4)

with perf_cols[0]:
    st.metric(
        label="Data Processing",
        value="10TB",
        delta="per appliance"
    )

with perf_cols[1]:
    st.metric(
        label="Response Time",
        value="<100ms",
        delta="API responses"
    )

with perf_cols[2]:
    st.metric(
        label="Availability",
        value="99.9%",
        delta="SLA target"
    )

with perf_cols[3]:
    st.metric(
        label="Backup Retention",
        value="7 years",
        delta="audit compliance"
    )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📋 Back: Product Overview", use_container_width=True):
        st.switch_page("pages/1_Product_Overview.py")

with col2:
    if st.button("⚙️ Next: Technical Stack", use_container_width=True):
        st.switch_page("pages/3_Technical_Stack.py")

with col3:
    if st.button("🚀 View Deployment Models", use_container_width=True):
        st.switch_page("pages/6_Deployment_Models.py")
