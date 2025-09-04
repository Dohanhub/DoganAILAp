import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.data import get_tech_stack_data, get_performance_benchmarks

st.set_page_config(
    page_title="Technical Stack - Doğan AI Lab",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Technical Stack")
st.markdown("**Modern, scalable tech stack prioritizing performance, security, and integration**")

# Stack Overview
st.header("🔧 Technology Stack Overview")

st.markdown("""
Doğan AI Lab is built with a modern, scalable tech stack that prioritizes performance, security, and ease of integration. 
The platform marries proven enterprise technology with cutting-edge AI capabilities and user-centric design.
""")

# Tech Stack Diagram
tech_data = get_tech_stack_data()

fig_stack = go.Figure()

# Create tech stack layers
layers = ["Frontend", "Backend", "Database", "Infrastructure", "AI/ML"]
technologies = [
    ["React.js", "Material-UI", "i18n Support"],
    ["Python", "FastAPI", "RESTful APIs"],
    ["PostgreSQL", "JSON Support", "ACID Compliance"],
    ["Docker", "Kubernetes", "GitHub Actions"],
    ["PyTorch", "NVIDIA GPUs", "Deep Learning"]
]
colors = ['#61dafb', '#3776ab', '#336791', '#2496ed', '#ee4c2c']

for i, (layer, techs, color) in enumerate(zip(layers, technologies, colors)):
    fig_stack.add_trace(go.Bar(
        x=[1],
        y=[1],
        name=layer,
        orientation='v',
        marker_color=color,
        text=f"<b>{layer}</b><br>" + "<br>".join(techs),
        textposition='inside',
        textfont=dict(color='white', size=10),
        base=i,
        width=0.8
    ))

fig_stack.update_layout(
    title="Doğan AI Lab - Technology Stack",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    height=600,
    showlegend=False
)

st.plotly_chart(fig_stack, use_container_width=True)

# Detailed Tech Breakdown
st.header("🔍 Technology Details")

tech_tabs = st.tabs(["🐍 Backend", "🗃️ Database", "⚛️ Frontend", "🐳 Infrastructure", "🤖 AI/ML"])

with tech_tabs[0]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Backend - Python & FastAPI")
        st.markdown("""
        **Technology Choice**: Python with FastAPI framework
        
        **Why Python?**
        - 🐍 Rich ecosystem in cybersecurity and data science
        - 📚 Extensive libraries for compliance logic
        - 🤖 Native machine learning integration
        - 🔒 Strong security frameworks
        
        **FastAPI Benefits:**
        - ⚡ High performance with async I/O
        - 📖 Automatic interactive API documentation
        - 🔧 Easy integration with external systems
        - ✅ Built-in data validation
        
        **Key Components:**
        - Compliance rules engine
        - Vendor risk assessment
        - Report generation
        - Authentication & authorization
        """)
    
    with col2:
        # API performance metrics
        api_metrics = {
            "Requests/sec": 1000,
            "Avg Response (ms)": 85,
            "99th Percentile (ms)": 200,
            "Error Rate (%)": 0.1
        }
        
        fig_api = px.bar(
            x=list(api_metrics.keys()),
            y=list(api_metrics.values()),
            title="API Performance Metrics",
            color=list(api_metrics.values()),
            color_continuous_scale="Blues"
        )
        fig_api.update_layout(height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig_api, use_container_width=True)

with tech_tabs[1]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Database - PostgreSQL")
        st.markdown("""
        **Technology Choice**: PostgreSQL as the core database
        
        **Why PostgreSQL?**
        - 🛡️ ACID compliance for audit integrity
        - 📊 JSON document storage capabilities
        - 🔒 Advanced security features
        - 📈 Excellent performance at scale
        
        **Data Storage:**
        - 📋 Control libraries and frameworks
        - 🔍 Compliance findings and evidence
        - 👥 User data and access logs
        - 📊 Audit trails and history
        
        **Features:**
        - Multi-user concurrent access
        - Advanced indexing for fast queries
        - Backup and replication
        - Data encryption at rest
        """)
    
    with col2:
        # Database metrics
        db_metrics = ["Compliance Data", "Audit Logs", "User Data", "Evidence Files"]
        storage_gb = [2500, 1800, 200, 3500]
        
        fig_db = px.pie(
            values=storage_gb,
            names=db_metrics,
            title="Database Storage Distribution (GB)"
        )
        fig_db.update_layout(height=300)
        st.plotly_chart(fig_db, use_container_width=True)

with tech_tabs[2]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Frontend - React.js")
        st.markdown("""
        **Technology Choice**: React.js single-page application
        
        **UI Framework**: Material-UI for professional design
        
        **Key Features:**
        - 🌐 Bilingual support (Arabic/English)
        - 📱 Responsive design for all devices
        - ⚡ Real-time dashboard updates
        - 🎨 Modern, intuitive interface
        
        **Internationalization (i18n):**
        - Complete Arabic translation
        - RTL (Right-to-Left) layout support
        - Cultural localization
        - Instant language switching
        
        **Components:**
        - Compliance dashboards
        - Report generation interface
        - Vendor management portal
        - Administrative panels
        """)
    
    with col2:
        # Language support metrics
        lang_features = ["UI Translation", "RTL Support", "Cultural Adaptation", "Help Documentation"]
        completion = [100, 100, 95, 90]
        
        fig_lang = px.bar(
            x=lang_features,
            y=completion,
            title="Localization Completion (%)",
            color=completion,
            color_continuous_scale="Greens"
        )
        fig_lang.update_layout(height=300, xaxis_tickangle=-45, yaxis_range=[0, 100])
        st.plotly_chart(fig_lang, use_container_width=True)

with tech_tabs[3]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Infrastructure - Docker & Kubernetes")
        st.markdown("""
        **Containerization**: Docker for consistent deployment
        
        **Orchestration**: Kubernetes for service management
        
        **CI/CD Pipeline**: GitHub Actions
        
        **Benefits:**
        - 🔄 Consistent environments (dev to production)
        - 📦 Easy updates and rollbacks
        - 🔧 Service discovery and load balancing
        - 🛡️ Self-healing capabilities
        
        **Security:**
        - Container image scanning
        - Vulnerability assessments
        - Network policies
        - Secret management
        
        **Monitoring:**
        - Application performance monitoring
        - Resource usage tracking
        - Alert management
        - Log aggregation
        """)
    
    with col2:
        # Infrastructure health
        services = ["API Gateway", "Web Server", "Database", "Message Queue", "Auth Service"]
        uptime = [99.9, 99.8, 99.9, 99.7, 99.9]
        
        fig_infra = px.bar(
            x=services,
            y=uptime,
            title="Service Uptime (%)",
            color=uptime,
            color_continuous_scale="RdYlGn"
        )
        fig_infra.update_layout(height=300, xaxis_tickangle=-45, yaxis_range=[99, 100])
        st.plotly_chart(fig_infra, use_container_width=True)

with tech_tabs[4]:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("AI/ML - PyTorch & GPU Acceleration")
        st.markdown("""
        **ML Framework**: PyTorch for deep learning models
        
        **Hardware**: NVIDIA GPUs for acceleration
        
        **AI Capabilities:**
        - 🔍 Anomaly detection in compliance data
        - 📈 Predictive compliance modeling
        - 🎯 Risk pattern recognition
        - ⚠️ Early warning systems
        
        **Models:**
        - Time-series analysis for compliance trends
        - Natural language processing for document analysis
        - Classification models for risk assessment
        - Recommendation systems for controls
        
        **Performance:**
        - Real-time inference
        - Batch processing for historical analysis
        - Continuous model training
        - A/B testing for model improvements
        """)
    
    with col2:
        # AI model performance
        models = ["Anomaly Detection", "Risk Prediction", "Document Analysis", "Trend Forecasting"]
        accuracy = [96, 94, 92, 88]
        
        fig_ai = px.bar(
            x=models,
            y=accuracy,
            title="AI Model Accuracy (%)",
            color=accuracy,
            color_continuous_scale="Plasma"
        )
        fig_ai.update_layout(height=300, xaxis_tickangle=-45, yaxis_range=[80, 100])
        st.plotly_chart(fig_ai, use_container_width=True)

# Performance Benchmarks
st.header("📊 Performance Benchmarks")

benchmark_data = get_performance_benchmarks()

perf_cols = st.columns(4)

with perf_cols[0]:
    st.metric(
        label="API Response Time",
        value="<100ms",
        delta="95th percentile"
    )

with perf_cols[1]:
    st.metric(
        label="Concurrent Users",
        value="1,000+",
        delta="per appliance"
    )

with perf_cols[2]:
    st.metric(
        label="Data Processing",
        value="1M records",
        delta="per minute"
    )

with perf_cols[3]:
    st.metric(
        label="Model Inference",
        value="10ms",
        delta="average latency"
    )

# Technology Comparison
st.header("🔄 Technology Stack Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Doğan AI Lab Stack")
    st.markdown("""
    ✅ **Python/FastAPI** - Modern, fast, developer-friendly
    ✅ **PostgreSQL** - Enterprise-grade reliability
    ✅ **React.js** - Component-based, maintainable UI
    ✅ **Docker/K8s** - Cloud-native, scalable
    ✅ **PyTorch** - State-of-the-art AI capabilities
    ✅ **Full Arabic Support** - Cultural localization
    """)

with col2:
    st.subheader("Traditional GRC Platforms")
    st.markdown("""
    ❌ **Legacy Languages** - Slower development cycles
    ❌ **Proprietary Databases** - Vendor lock-in
    ❌ **Monolithic Architecture** - Difficult to scale
    ❌ **Limited AI** - Rule-based systems only
    ❌ **English-only** - No Arabic localization
    ❌ **High Customization Costs** - Manual integration
    """)

# Security Considerations
st.header("🔒 Security & Compliance")

security_cols = st.columns(3)

with security_cols[0]:
    st.subheader("Data Security")
    st.markdown("""
    - 🔐 Encryption at rest and in transit
    - 🛡️ Hardware security modules
    - 🔑 Advanced key management
    - 📊 Audit logging
    """)

with security_cols[1]:
    st.subheader("Access Control")
    st.markdown("""
    - 👥 Role-based access control (RBAC)
    - 🔐 Multi-factor authentication
    - 📝 Session management
    - 🚫 Principle of least privilege
    """)

with security_cols[2]:
    st.subheader("Compliance")
    st.markdown("""
    - 📜 PDPL compliance
    - 🌍 GDPR alignment
    - 🔒 ISO 27001 controls
    - 🏛️ Government security standards
    """)

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏗️ Back: Architecture", use_container_width=True):
        st.switch_page("pages/2_Architecture.py")

with col2:
    if st.button("📊 Next: Market Analysis", use_container_width=True):
        st.switch_page("pages/4_Market_Analysis.py")

with col3:
    if st.button("📜 View Compliance Frameworks", use_container_width=True):
        st.switch_page("pages/5_Compliance_Frameworks.py")
