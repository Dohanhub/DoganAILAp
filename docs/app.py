"""
Dogan AI Compliance Platform - Complete Application
Saudi Arabia Regulatory Compliance & Risk Management
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import hashlib
import json

# Configure page
st.set_page_config(
    page_title="Dogan AI Compliance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
        transform: translateY(-2px);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .compliance-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'compliance_data' not in st.session_state:
    st.session_state.compliance_data = None
if 'selected_framework' not in st.session_state:
    st.session_state.selected_framework = "NCA"

# Header
st.title("🛡️ Dogan AI Compliance Platform")
st.markdown("### Saudi Arabia Regulatory Compliance & Risk Management")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Framework selection
    framework = st.selectbox(
        "Select Compliance Framework",
        ["NCA - National Cybersecurity", "SAMA - Financial Services", "PDPL - Data Protection", "ISO 27001", "NIST CSF"],
        index=0
    )
    st.session_state.selected_framework = framework
    
    # Organization info
    st.subheader("Organization Details")
    org_name = st.text_input("Organization Name", value="Sample Organization")
    sector = st.selectbox("Sector", ["Banking", "Healthcare", "Government", "Retail", "Technology", "Energy"])
    
    # API Settings
    st.subheader("Backend Connection")
    api_url = st.text_input("API URL", value="http://localhost:5000")
    
    # Actions
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "✅ Compliance Assessment", "📈 Analytics", "📋 Reports", "⚙️ Settings"])

with tab1:
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Overall Compliance", "87%", "↑ 5%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Controls", "245", "↑ 12")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Risk Score", "Low", "↓ Medium")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Open Issues", "8", "↓ 3")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Compliance trend chart
    st.subheader("📈 Compliance Trend")
    
    # Generate sample data for visualization
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    compliance_scores = [75, 78, 80, 82, 83, 85, 86, 87, 88, 89, 91, 87]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=compliance_scores,
        mode='lines+markers',
        name='Compliance Score',
        line=dict(color='#2E7D32', width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title="Monthly Compliance Score Trend",
        xaxis_title="Month",
        yaxis_title="Compliance Score (%)",
        yaxis=dict(range=[0, 100]),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Framework coverage
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Framework Coverage")
        frameworks_data = {
            'Framework': ['NCA', 'SAMA', 'PDPL', 'ISO 27001', 'NIST'],
            'Coverage': [92, 88, 85, 90, 87]
        }
        df_frameworks = pd.DataFrame(frameworks_data)
        
        fig = px.bar(df_frameworks, x='Framework', y='Coverage', 
                    color='Coverage', color_continuous_scale='Viridis',
                    title="Compliance Coverage by Framework")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Risk Distribution")
        risk_data = {
            'Risk Level': ['Critical', 'High', 'Medium', 'Low'],
            'Count': [2, 6, 15, 45]
        }
        df_risk = pd.DataFrame(risk_data)
        
        fig = px.pie(df_risk, values='Count', names='Risk Level',
                    color_discrete_map={'Critical': '#d32f2f', 'High': '#f57c00',
                                      'Medium': '#fbc02d', 'Low': '#388e3c'},
                    title="Risk Distribution")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("✅ Compliance Assessment")
    
    # Assessment controls
    col1, col2, col3 = st.columns(3)
    with col1:
        assessment_type = st.selectbox("Assessment Type", ["Quick Scan", "Full Assessment", "Gap Analysis"])
    with col2:
        st.date_input("Assessment Date", datetime.now())
    with col3:
        if st.button("🚀 Run Assessment", use_container_width=True):
            with st.spinner("Running compliance assessment..."):
                # Here we would call the FastAPI backend
                st.success("Assessment completed successfully!")
    
    # Assessment results
    st.subheader("Assessment Results")
    
    # Control categories
    categories = ['Access Control', 'Data Protection', 'Incident Response', 
                 'Business Continuity', 'Compliance Management']
    scores = [85, 92, 78, 88, 95]
    
    fig = go.Figure(data=[
        go.Bar(x=categories, y=scores, 
               marker_color=['green' if s >= 80 else 'orange' if s >= 60 else 'red' for s in scores])
    ])
    fig.update_layout(
        title="Control Category Scores",
        xaxis_title="Category",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 100])
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed controls table
    st.subheader("📋 Control Details")
    controls_data = {
        'Control ID': ['NCA-1.1', 'NCA-1.2', 'NCA-2.1', 'NCA-2.2', 'NCA-3.1'],
        'Description': [
            'User Access Management',
            'Privileged Access Control',
            'Data Classification',
            'Data Encryption',
            'Incident Detection'
        ],
        'Status': ['✅ Compliant', '⚠️ Partial', '✅ Compliant', '✅ Compliant', '❌ Non-Compliant'],
        'Score': [100, 60, 95, 90, 30],
        'Priority': ['High', 'Critical', 'Medium', 'High', 'Critical']
    }
    df_controls = pd.DataFrame(controls_data)
    st.dataframe(df_controls, use_container_width=True, hide_index=True)

with tab3:
    st.header("📈 Analytics & Insights")
    
    # Time period selector
    period = st.select_slider(
        "Select Time Period",
        options=["Last 7 Days", "Last 30 Days", "Last Quarter", "Last Year"],
        value="Last 30 Days"
    )
    
    # Key metrics over time
    st.subheader("📊 Key Metrics Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Compliance score heatmap
        st.subheader("Compliance Heatmap")
        
        # Generate heatmap data
        import numpy as np
        frameworks = ['NCA', 'SAMA', 'PDPL', 'ISO', 'NIST']
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        
        heatmap_data = np.random.randint(70, 100, size=(len(frameworks), len(months)))
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=months,
            y=frameworks,
            colorscale='RdYlGn',
            text=heatmap_data,
            texttemplate="%{text}",
            textfont={"size": 12},
        ))
        fig.update_layout(title="Compliance Scores by Framework and Month")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Improvement areas
        st.subheader("🎯 Top Improvement Areas")
        improvement_data = {
            'Area': ['Incident Response', 'Access Reviews', 'Data Retention', 
                    'Vendor Management', 'Security Training'],
            'Current': [65, 70, 72, 68, 75],
            'Target': [90, 90, 85, 85, 90]
        }
        df_improvement = pd.DataFrame(improvement_data)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Current', x=df_improvement['Area'], y=df_improvement['Current'],
                            marker_color='lightblue'))
        fig.add_trace(go.Bar(name='Target', x=df_improvement['Area'], y=df_improvement['Target'],
                            marker_color='darkblue', opacity=0.5))
        fig.update_layout(barmode='overlay', title="Current vs Target Scores")
        st.plotly_chart(fig, use_container_width=True)
    
    # Predictive analytics
    st.subheader("🔮 Predictive Analytics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Predicted Compliance (Q1 2025):** 92%")
    with col2:
        st.warning("**Risk Alert:** 3 controls trending downward")
    with col3:
        st.success("**Recommendation:** Focus on Access Management")

with tab4:
    st.header("📋 Reports & Documentation")
    
    # Report generation
    st.subheader("Generate Reports")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        report_type = st.selectbox("Report Type", 
                                  ["Executive Summary", "Detailed Compliance", "Gap Analysis", "Audit Report"])
    with col2:
        report_format = st.selectbox("Format", ["PDF", "Excel", "Word", "CSV"])
    with col3:
        if st.button("📥 Generate Report", use_container_width=True):
            st.success("Report generated successfully!")
            st.download_button(
                label="Download Report",
                data="Sample report content",
                file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # Recent reports
    st.subheader("📂 Recent Reports")
    reports_data = {
        'Report Name': [
            'Q4 2024 Compliance Summary',
            'NCA Assessment Report',
            'Risk Analysis December 2024',
            'Vendor Compliance Review',
            'Annual Audit Report 2024'
        ],
        'Type': ['Executive', 'Assessment', 'Risk', 'Vendor', 'Audit'],
        'Date': ['2024-12-15', '2024-12-10', '2024-12-05', '2024-11-30', '2024-11-15'],
        'Status': ['✅ Ready', '✅ Ready', '✅ Ready', '⏳ Processing', '✅ Ready']
    }
    df_reports = pd.DataFrame(reports_data)
    st.dataframe(df_reports, use_container_width=True, hide_index=True)

with tab5:
    st.header("⚙️ Platform Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔔 Notifications")
        st.toggle("Email Notifications", value=True)
        st.toggle("SMS Alerts", value=False)
        st.toggle("Dashboard Alerts", value=True)
        
        st.subheader("🎨 Display Settings")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        language = st.selectbox("Language", ["English", "Arabic"])
    
    with col2:
        st.subheader("🔐 Security Settings")
        st.toggle("Two-Factor Authentication", value=True)
        st.toggle("Session Timeout", value=True)
        timeout = st.slider("Timeout (minutes)", 5, 60, 30)
        
        st.subheader("📊 Data Settings")
        st.toggle("Auto-refresh Dashboard", value=True)
        refresh_interval = st.slider("Refresh Interval (seconds)", 10, 300, 60)
    
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🛡️ Dogan AI Compliance Platform | Built with Latest Technologies | © 2024</p>
    </div>
    """,
    unsafe_allow_html=True
)