"""
Reusable UI components for Streamlit app
"""
import streamlit as st
from typing import Dict, Any, List, Optional

def status_badge(status: str, language: str = "ar") -> str:
    """Generate status badge with appropriate styling"""
    status_mapping = {
        "COMPLIANT": ("🟢", "متوافق" if language == "ar" else "COMPLIANT"),
        "GAPS": ("🟡", "فجوات" if language == "ar" else "GAPS"), 
        "NON_COMPLIANT": ("🔴", "غير متوافق" if language == "ar" else "NON_COMPLIANT"),
        "UNKNOWN": ("⚪", "غير معروف" if language == "ar" else "UNKNOWN")
    }
    
    icon, text = status_mapping.get(status, ("⚪", status))
    return f"{icon} {text}"

def metrics_card(title: str, value: Any, delta: Optional[str] = None):
    """Display a metrics card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=title, value=value, delta=delta)

def requirement_card(requirement: Dict[str, Any], language: str = "ar"):
    """Display a requirement card"""
    control_id = requirement.get("control_id", "N/A")
    title = requirement.get("title", "No title")
    description = requirement.get("description", "No description")
    
    with st.expander(f"{control_id} - {title}"):
        if language == "ar":
            st.write(f"**الوصف:** {description}")
        else:
            st.write(f"**Description:** {description}")
        
        if "vendor_capability" in requirement:
            capability = requirement["vendor_capability"]
            if language == "ar":
                st.write(f"**المزود:** {capability.get('vendor', 'N/A')}")
                st.write(f"**النطاق:** {capability.get('scope', 'N/A')}")
            else:
                st.write(f"**Vendor:** {capability.get('vendor', 'N/A')}")
                st.write(f"**Scope:** {capability.get('scope', 'N/A')}")

def loading_spinner(text: str):
    """Display loading spinner with text"""
    return st.spinner(text)

def error_message(message: str, language: str = "ar"):
    """Display standardized error message"""
    if language == "ar":
        st.error(f"❌ خطأ: {message}")
    else:
        st.error(f"❌ Error: {message}")

def success_message(message: str, language: str = "ar"):
    """Display standardized success message"""
    if language == "ar":
        st.success(f"✅ {message}")
    else:
        st.success(f"✅ {message}")

def info_message(message: str, language: str = "ar"):
    """Display standardized info message"""
    if language == "ar":
        st.info(f"ℹ️ {message}")
    else:
        st.info(f"ℹ️ {message}")
