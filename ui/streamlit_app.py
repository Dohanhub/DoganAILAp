"""
Streamlit frontend for DoganAI KSA Compliance Platform
"""
import streamlit as st
import requests
import yaml
import json
from datetime import datetime
from pathlib import Path
import time

# Configure page
st.set_page_config(
    page_title="منصة الامتثال والعمليات - المملكة العربية السعودية",
    page_icon="🇸🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load localization
@st.cache_data
def load_locales():
    """Load localization files"""
    try:
        with open('locales/ar.yaml', 'r', encoding='utf-8') as f:
            ar_locale = yaml.safe_load(f)
        with open('locales/en.yaml', 'r', encoding='utf-8') as f:
            en_locale = yaml.safe_load(f)
        return ar_locale, en_locale
    except Exception:
        # Fallback if locale files don't exist
        return {"ui": {}}, {"ui": {}}

# API Configuration - try both localhost and 0.0.0.0
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def make_api_request(endpoint: str, method: str = "GET", **kwargs):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.request(method, url, timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ لا يمكن الاتصال بالخادم. تأكد من تشغيل API على المنفذ 8000")
        st.error("❌ Cannot connect to server. Make sure API is running on port 8000")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ خطأ في الطلب: {str(e)}")
        st.error(f"❌ Request error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ خطأ غير متوقع: {str(e)}")
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def main():
    """Main Streamlit application"""
    
    # Load locales
    ar_locale, en_locale = load_locales()
    
    # Language selection
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        language = st.selectbox(
            "اللغة / Language",
            ["العربية", "English"],
            index=0
        )
    
    # Select locale based on language
    locale = ar_locale if language == "العربية" else en_locale
    ui_text = locale.get("ui", {})
    
    # App title
    if language == "العربية":
        st.title("🇸🇦 منصة الامتثال والعمليات")
        st.subheader("المملكة العربية السعودية")
    else:
        st.title("🇸🇦 Compliance & Operations Platform")
        st.subheader("Kingdom of Saudi Arabia")
    
    # Sidebar
    with st.sidebar:
        if language == "العربية":
            st.header("📋 لوحة التحكم")
        else:
            st.header("📋 Control Panel")
        
        # Health Check
        if st.button("🔍 فحص حالة النظام / Health Check"):
            with st.spinner("جاري فحص النظام..."):
                health_data = make_api_request("/health")
                if health_data:
                    st.success("✅ النظام يعمل بشكل طبيعي")
                    with st.expander("تفاصيل الفحص / Health Details"):
                        st.json(health_data)
    
    # Main content tabs
    if language == "العربية":
        tab1, tab2, tab3 = st.tabs(["📊 تقييم الامتثال", "📈 المقاييس", "📋 السجلات"])
    else:
        tab1, tab2, tab3 = st.tabs(["📊 Compliance Evaluation", "📈 Metrics", "📋 Audit Logs"])
    
    with tab1:
        compliance_tab(language, ui_text)
    
    with tab2:
        metrics_tab(language)
    
    with tab3:
        audit_tab(language)

def compliance_tab(language: str, ui_text: dict):
    """Compliance evaluation tab"""
    
    if language == "العربية":
        st.header("📊 تقييم الامتثال للمتطلبات التنظيمية")
    else:
        st.header("📊 Regulatory Compliance Evaluation")
    
    # Get available mappings
    mappings_data = make_api_request("/mappings")
    if not mappings_data:
        return
    
    mappings = mappings_data.get("mappings", [])
    
    if not mappings:
        if language == "العربية":
            st.warning("⚠️ لا توجد ملفات تخطيط متاحة")
        else:
            st.warning("⚠️ No mapping files available")
        return
    
    # Mapping selection
    if language == "العربية":
        selected_mapping = st.selectbox(
            "اختر المقترح / المزود",
            mappings,
            index=0 if "MAP-GOV-SecurePortal-IBM-Lenovo" in mappings else 0
        )
    else:
        selected_mapping = st.selectbox(
            "Select Proposal / Vendor",
            mappings,
            index=0 if "MAP-GOV-SecurePortal-IBM-Lenovo" in mappings else 0
        )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if language == "العربية":
            evaluate_btn = st.button("🔍 تقييم الامتثال", type="primary")
            force_refresh = st.checkbox("إعادة تحديث البيانات")
        else:
            evaluate_btn = st.button("🔍 Evaluate Compliance", type="primary")
            force_refresh = st.checkbox("Force Refresh")
    
    if evaluate_btn and selected_mapping:
        with st.spinner("جاري تقييم الامتثال... / Evaluating compliance..."):
            evaluation_data = make_api_request(
                "/evaluate",
                method="POST",
                json={
                    "mapping_name": selected_mapping,
                    "force_refresh": force_refresh
                }
            )
            
            if evaluation_data:
                display_evaluation_results(evaluation_data, language, ui_text)

def display_evaluation_results(data: dict, language: str, ui_text: dict):
    """Display compliance evaluation results"""
    
    status = data.get("status", "UNKNOWN")
    summary = data.get("summary", {})
    details = data.get("details", {})
    
    # Status indicator
    status_colors = {
        "COMPLIANT": "🟢",
        "GAPS": "🟡", 
        "NON_COMPLIANT": "🔴"
    }
    
    status_icon = status_colors.get(status, "⚪")
    
    if language == "العربية":
        st.subheader(f"{status_icon} حالة الامتثال: {status}")
    else:
        st.subheader(f"{status_icon} Compliance Status: {status}")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            ui_text.get("required", "المتطلبات / Required"),
            summary.get("total_controls", 0)
        )
    
    with col2:
        st.metric(
            ui_text.get("provided", "المغطى / Provided"),
            summary.get("covered_controls", 0)
        )
    
    with col3:
        st.metric(
            ui_text.get("missing", "الناقص / Missing"),
            summary.get("missing_controls", 0)
        )
    
    with col4:
        coverage = summary.get("coverage_percentage", 0)
        st.metric(
            "نسبة التغطية / Coverage %",
            f"{coverage:.1f}%"
        )
    
    # Progress bar
    st.progress(coverage / 100)
    
    # Detailed results
    if language == "العربية":
        st.subheader("📋 التفاصيل")
        
        tab1, tab2 = st.tabs(["✅ المتطلبات المغطاة", "❌ المتطلبات الناقصة"])
    else:
        st.subheader("📋 Details")
        
        tab1, tab2 = st.tabs(["✅ Covered Requirements", "❌ Missing Requirements"])
    
    with tab1:
        provided = details.get("provided", [])
        if provided:
            for item in provided:
                with st.expander(f"✅ {item.get('control_id', 'N/A')} - {item.get('title', 'No title')}"):
                    capability = item.get('vendor_capability', {})
                    st.write(f"**المزود / Vendor:** {capability.get('vendor', 'N/A')}")
                    st.write(f"**النطاق / Scope:** {capability.get('scope', 'N/A')}")
                    if capability.get('evidence'):
                        st.write(f"**الدليل / Evidence:** {capability['evidence']}")
        else:
            if language == "العربية":
                st.info("لا توجد متطلبات مغطاة")
            else:
                st.info("No covered requirements")
    
    with tab2:
        missing = details.get("missing", [])
        if missing:
            for item in missing:
                with st.expander(f"❌ {item.get('control_id', 'N/A')} - {item.get('title', 'No title')}"):
                    st.write(f"**الوصف / Description:** {item.get('description', 'No description')}")
        else:
            if language == "العربية":
                st.success("🎉 جميع المتطلبات مغطاة!")
            else:
                st.success("🎉 All requirements covered!")
    
    # Export functionality
    if language == "العربية":
        if st.button("📄 تصدير التقرير"):
            export_report(data, language)
    else:
        if st.button("📄 Export Report"):
            export_report(data, language)

def metrics_tab(language: str):
    """Metrics and monitoring tab"""
    
    if language == "العربية":
        st.header("📈 مقاييس الأداء والمراقبة")
    else:
        st.header("📈 Performance Metrics & Monitoring")
    
    # Get metrics
    metrics_data = make_api_request("/metrics")
    if metrics_data:
        if language == "العربية":
            st.success("✅ تم جمع المقاييس بنجاح")
        else:
            st.success("✅ Metrics collected successfully")
        
        # Display timestamp
        timestamp = metrics_data.get("timestamp", "")
        if timestamp:
            if language == "العربية":
                st.write(f"**آخر تحديث:** {timestamp}")
            else:
                st.write(f"**Last Updated:** {timestamp}")

def audit_tab(language: str):
    """Enhanced enterprise-level audit logs tab"""
    
    if language == "العربية":
        st.header("📋 سجلات المراجعة - المستوى المؤسسي")
        st.subheader("📊 تتبع شامل لعمليات التقييم والامتثال")
    else:
        st.header("📋 Enterprise Audit Logs")
        st.subheader("📊 Comprehensive Compliance Evaluation Tracking")
    
    # Audit controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if language == "العربية":
            limit = st.selectbox("عدد السجلات", [10, 25, 50, 100], index=2)
        else:
            limit = st.selectbox("Records per page", [10, 25, 50, 100], index=2)
    
    with col2:
        if language == "العربية":
            refresh_btn = st.button("🔄 تحديث السجلات")
        else:
            refresh_btn = st.button("🔄 Refresh Logs")
    
    with col3:
        if language == "العربية":
            export_logs_btn = st.button("📥 تصدير السجلات")
        else:
            export_logs_btn = st.button("📥 Export Logs")
    
    # Get audit logs
    audit_data = make_api_request(f"/audit?limit={limit}")
    if audit_data:
        logs = audit_data.get("logs", [])
        total = audit_data.get("total", 0)
        
        if logs:
            # Summary statistics
            if language == "العربية":
                st.subheader("📈 إحصائيات السجلات")
            else:
                st.subheader("📈 Audit Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("إجمالي السجلات / Total Records", total)
            
            with col2:
                compliant_logs = len([log for log in logs if log.get('status') == 'COMPLIANT'])
                st.metric("متوافق / Compliant", compliant_logs)
            
            with col3:
                gap_logs = len([log for log in logs if log.get('status') == 'GAPS'])
                st.metric("فجوات / Gaps", gap_logs)
            
            with col4:
                avg_coverage = sum([log.get('evaluation_summary', {}).get('coverage_percentage', 0) for log in logs]) / len(logs) if logs else 0
                st.metric("متوسط التغطية / Avg Coverage", f"{avg_coverage:.1f}%")
            
            # Detailed logs display
            if language == "العربية":
                st.subheader(f"📋 السجلات التفصيلية ({len(logs)} من {total})")
            else:
                st.subheader(f"📋 Detailed Logs ({len(logs)} of {total})")
            
            for i, log in enumerate(logs):
                timestamp = log.get('timestamp', 'N/A')
                mapping_name = log.get('mapping_name', 'N/A')
                status = log.get('status', 'UNKNOWN')
                policy_ref = log.get('policy_ref', 'N/A')
                summary = log.get('evaluation_summary', {})
                
                # Status color coding
                status_colors = {
                    "COMPLIANT": "🟢",
                    "GAPS": "🟡", 
                    "NON_COMPLIANT": "🔴"
                }
                status_icon = status_colors.get(status, "⚪")
                
                with st.expander(f"{status_icon} {timestamp[:19]} - {mapping_name} - {status}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if language == "العربية":
                            st.write(f"**المقترح:** {mapping_name}")
                            st.write(f"**السياسة:** {policy_ref}")
                            st.write(f"**الحالة:** {status}")
                            st.write(f"**التوقيت:** {timestamp}")
                        else:
                            st.write(f"**Mapping:** {mapping_name}")
                            st.write(f"**Policy:** {policy_ref}")
                            st.write(f"**Status:** {status}")
                            st.write(f"**Timestamp:** {timestamp}")
                    
                    with col2:
                        if language == "العربية":
                            st.write(f"**إجمالي المتطلبات:** {summary.get('total_controls', 0)}")
                            st.write(f"**المتطلبات المغطاة:** {summary.get('covered_controls', 0)}")
                            st.write(f"**نسبة التغطية:** {summary.get('coverage_percentage', 0):.1f}%")
                        else:
                            st.write(f"**Total Controls:** {summary.get('total_controls', 0)}")
                            st.write(f"**Covered Controls:** {summary.get('covered_controls', 0)}")
                            st.write(f"**Coverage:** {summary.get('coverage_percentage', 0):.1f}%")
                    
                    # Progress bar for coverage
                    coverage = summary.get('coverage_percentage', 0)
                    st.progress(coverage / 100)
            
            # Export functionality
            if export_logs_btn:
                export_audit_logs(logs, language)
        else:
            if language == "العربية":
                st.info("📝 لا توجد سجلات مراجعة متاحة. سيتم إنشاء السجلات عند تشغيل تقييمات الامتثال.")
            else:
                st.info("📝 No audit logs available. Logs will be created when compliance evaluations are performed.")
    else:
        if language == "العربية":
            st.error("❌ فشل في تحميل سجلات المراجعة")
        else:
            st.error("❌ Failed to load audit logs")

def export_report(data: dict, language: str):
    """Export compliance report"""
    try:
        report = {
            "timestamp": datetime.now().isoformat(),
            "mapping": data.get("mapping_name"),
            "status": data.get("status"),
            "summary": data.get("summary"),
            "details": data.get("details")
        }
        
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="⬇️ تحميل التقرير / Download Report",
            data=report_json,
            file_name=f"compliance_report_{data.get('mapping_name', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
    except Exception as e:
        if language == "العربية":
            st.error(f"خطأ في تصدير التقرير: {str(e)}")
        else:
            st.error(f"Export error: {str(e)}")

def export_audit_logs(logs: list, language: str):
    """Export audit logs for enterprise compliance"""
    try:
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "export_type": "audit_logs",
            "record_count": len(logs),
            "logs": logs
        }
        
        export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="⬇️ تحميل سجلات المراجعة / Download Audit Logs",
            data=export_json,
            file_name=f"audit_logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        if language == "العربية":
            st.success("✅ تم تصدير سجلات المراجعة بنجاح")
        else:
            st.success("✅ Audit logs exported successfully")
        
    except Exception as e:
        if language == "العربية":
            st.error(f"خطأ في تصدير السجلات: {str(e)}")
        else:
            st.error(f"Export error: {str(e)}")

if __name__ == "__main__":
    main()
