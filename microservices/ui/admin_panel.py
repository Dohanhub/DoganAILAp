import streamlit as st
import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8003"  # Integrations microservice
API_KEY = os.getenv("API_KEY", "")  # MUST BE SET IN PRODUCTION - NO DEFAULT

st.set_page_config(page_title='Admin Panel - Integrations', layout='centered')
st.title('🔒 Admin Panel: Integration Management')

# REAL RBAC CHECK - SECURITY CRITICAL
def check_admin_access():
    """Check if user has admin access - IMPLEMENT WITH REAL AUTH"""
    # TODO: Implement real authentication check
    # For now, check environment variable for demo purposes
    return os.getenv("ADMIN_ACCESS_GRANTED", "false").lower() == "true"

if not check_admin_access():
    st.error('🔒 Access denied. Admin authentication required.')
    st.info('Set ADMIN_ACCESS_GRANTED=true in environment for demo access.')
    st.stop()

# Helper functions
def get_integrations():
    """Fetch integrations from backend API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/integrations",
            headers={"X-API-Key": API_KEY}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch integrations: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def add_integration(vendor_name, integration_type, capabilities, compliance_frameworks):
    """Add new integration via backend API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/admin/integrations",
            headers={"X-API-Key": API_KEY},
            params={
                "vendor_name": vendor_name,
                "integration_type": integration_type,
                "capabilities": capabilities,
                "compliance_frameworks": compliance_frameworks
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to add integration: {response.status_code}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def toggle_integration(vendor_name, enable):
    """Enable/disable integration via backend API"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/admin/integrations/{vendor_name}/enable",
            headers={"X-API-Key": API_KEY},
            params={"enable": enable}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to toggle integration: {response.status_code}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def update_integration(vendor_name, capabilities, compliance_frameworks):
    """Update integration via backend API"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/admin/integrations/{vendor_name}",
            headers={"X-API-Key": API_KEY},
            params={
                "capabilities": capabilities,
                "compliance_frameworks": compliance_frameworks
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to update integration: {response.status_code}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

# Main admin panel
st.subheader('📊 Current Integrations')

# Fetch real-time data from backend
integrations_data = get_integrations()

if integrations_data:
    integrations = integrations_data.get('integrations', [])
    st.info(f"Total: {integrations_data.get('total_count', 0)} | Active: {integrations_data.get('active_count', 0)}")
    
    for i, integ in enumerate(integrations):
        with st.expander(f"🔗 {integ['display_name']} ({integ['type']}) - Status: {integ['integration_status']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Vendor:** {integ['vendor_name']}")
                st.write(f"**Type:** {integ['type']}")
                st.write(f"**Status:** {integ['integration_status']}")
                st.write(f"**Compliance Score:** {integ['compliance_score']:.1f}%")
                st.write(f"**Last Updated:** {integ['last_updated']}")
            
            with col2:
                st.write("**Capabilities:**")
                for cap in integ['capabilities'][:3]:  # Show first 3
                    st.write(f"• {cap}")
                if len(integ['capabilities']) > 3:
                    st.write(f"... and {len(integ['capabilities']) - 3} more")
                
                st.write("**Compliance Frameworks:**")
                for framework in integ['compliance_frameworks'][:3]:  # Show first 3
                    st.write(f"• {framework}")
                if len(integ['compliance_frameworks']) > 3:
                    st.write(f"... and {len(integ['compliance_frameworks']) - 3} more")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"Configure {integ['display_name']}", key=f"cfg_{i}"):
                    st.session_state[f"config_{integ['vendor_name']}"] = True
            
            with col2:
                if integ['integration_status'] == 'active':
                    if st.button(f"Disable {integ['display_name']}", key=f"dis_{i}"):
                        result = toggle_integration(integ['vendor_name'], False)
                        if 'error' not in result:
                            st.success(f"{integ['display_name']} disabled successfully!")
                            st.rerun()
                        else:
                            st.error(result['error'])
                else:
                    if st.button(f"Enable {integ['display_name']}", key=f"ena_{i}"):
                        result = toggle_integration(integ['vendor_name'], True)
                        if 'error' not in result:
                            st.success(f"{integ['display_name']} enabled successfully!")
                            st.rerun()
                        else:
                            st.error(result['error'])
            
            with col3:
                if st.button(f"Delete {integ['display_name']}", key=f"del_{i}"):
                    if st.button(f"Confirm Delete {integ['display_name']}", key=f"confirm_del_{i}"):
                        # Add delete functionality here
                        st.warning("Delete functionality to be implemented")
            
            # Configuration form
            if st.session_state.get(f"config_{integ['vendor_name']}", False):
                with st.form(f"config_form_{integ['vendor_name']}"):
                    st.write(f"**Configure {integ['display_name']}**")
                    
                    new_capabilities = st.text_area(
                        "Capabilities (one per line)",
                        value="\n".join(integ['capabilities']),
                        key=f"cap_{integ['vendor_name']}"
                    )
                    
                    new_frameworks = st.text_area(
                        "Compliance Frameworks (one per line)",
                        value="\n".join(integ['compliance_frameworks']),
                        key=f"fw_{integ['vendor_name']}"
                    )
                    
                    if st.form_submit_button("Update Integration"):
                        capabilities_list = [cap.strip() for cap in new_capabilities.split('\n') if cap.strip()]
                        frameworks_list = [fw.strip() for fw in new_frameworks.split('\n') if fw.strip()]
                        
                        result = update_integration(integ['vendor_name'], capabilities_list, frameworks_list)
                        if 'error' not in result:
                            st.success(f"{integ['display_name']} updated successfully!")
                            st.session_state[f"config_{integ['vendor_name']}"] = False
                            st.rerun()
                        else:
                            st.error(result['error'])
                    
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"config_{integ['vendor_name']}"] = False
                        st.rerun()
else:
    st.warning("Unable to fetch integrations from backend. Check if the integrations service is running.")

st.markdown('---')

# Add New Integration
st.subheader('➕ Add New Integration')
with st.form('add_integration'):
    vendor_name = st.text_input('Vendor Name (e.g., New_Vendor)', key='new_vendor_name')
    integration_type = st.selectbox(
        'Integration Type',
        ['AI Platform', 'Cloud AI', 'Network Security', 'Cybersecurity', 'Next Gen Firewall', 'Hardware Infrastructure', 'Other'],
        key='new_type'
    )
    
    capabilities = st.text_area(
        'Capabilities (one per line)',
        placeholder="Enter capabilities, one per line...",
        key='new_capabilities'
    )
    
    compliance_frameworks = st.text_area(
        'Compliance Frameworks (one per line)',
        placeholder="Enter compliance frameworks, one per line...",
        key='new_frameworks'
    )
    
    submit = st.form_submit_button('Add Integration')
    if submit:
        if vendor_name and capabilities and compliance_frameworks:
            capabilities_list = [cap.strip() for cap in capabilities.split('\n') if cap.strip()]
            frameworks_list = [fw.strip() for fw in compliance_frameworks.split('\n') if fw.strip()]
            
            result = add_integration(vendor_name, integration_type, capabilities_list, frameworks_list)
            if 'error' not in result:
                st.success(f"Integration '{vendor_name}' added successfully!")
                st.rerun()
            else:
                st.error(result['error'])
        else:
            st.error("Please fill in all fields")

# System Status
st.markdown('---')
st.subheader('📡 System Status')

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Data"):
        st.rerun()

with col2:
    if st.button("🔍 Check Backend Health"):
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                st.success(f"Backend Healthy - {health_data.get('vendors_available', 0)} vendors available")
            else:
                st.error(f"Backend Error: {response.status_code}")
        except Exception as e:
            st.error(f"Backend Unreachable: {str(e)}")

with col3:
    if st.button("📊 View API Docs"):
        st.info("API Documentation available at:")
        st.write(f"**Swagger UI:** {API_BASE_URL}/docs")
        st.write(f"**ReDoc:** {API_BASE_URL}/redoc")
