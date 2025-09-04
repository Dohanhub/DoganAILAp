import os
import json
import requests
import pandas as pd
import streamlit as st
import yaml
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DURATION = 300  # 5 minutes

def get_translation_data(lang: str) -> Dict[str, Any]:
    """Load translation data with caching"""
    try:
        path = Path(__file__).resolve().parents[1] / "i18n" / f"{lang}.yml"
        if not path.exists():
            logger.warning(f"Translation file not found: {path}")
            return {}
        return yaml.safe_load(open(path, 'r', encoding='utf-8'))
    except Exception as e:
        logger.error(f"Error loading translations for {lang}: {e}")
        return {}

def t(key: str) -> str:
    """Get translated text with fallback"""
    lang = st.session_state.get("lang", "ar")
    data = get_translation_data(lang)
    return data.get('ui', {}).get(key, key)

@st.cache_data(ttl=CACHE_DURATION)
def get_mappings_from_api(api_url: str) -> Optional[list]:
    """Get mappings from API with caching"""
    try:
        response = requests.get(f"{api_url}/mappings", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch mappings from API: {e}")
        return None

@st.cache_data(ttl=CACHE_DURATION)
def get_local_mappings() -> list:
    """Get mappings from local files with caching"""
    try:
        mp_dir = Path(__file__).resolve().parents[1] / "mappings"
        if not mp_dir.exists():
            return []
        return [p.stem for p in mp_dir.glob("*.yaml")]
    except Exception as e:
        logger.error(f"Failed to get local mappings: {e}")
        return []

@st.cache_data(ttl=CACHE_DURATION)
def get_benchmarks_from_api(api_url: str) -> Optional[dict]:
    """Get benchmarks from API with caching"""
    try:
        response = requests.get(f"{api_url}/benchmarks", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch benchmarks from API: {e}")
        return None

@st.cache_data(ttl=CACHE_DURATION)
def get_local_benchmarks() -> Optional[dict]:
    """Get benchmarks from local files with caching"""
    try:
        path = Path(__file__).resolve().parents[1] / "benchmarks" / "sector_kpis_2024_2025.json"
        if not path.exists():
            return None
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to get local benchmarks: {e}")
        return None

def evaluate_via_api(api_url: str, mapping: str) -> Optional[dict]:
    """Evaluate mapping via API"""
    try:
        response = requests.post(
            f"{api_url}/evaluate", 
            json={"mapping": mapping}, 
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error(t("api_timeout_error"))
        return None
    except requests.exceptions.ConnectionError:
        st.error(t("api_connection_error"))
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error(t("mapping_not_found"))
        else:
            st.error(f"{t('api_error')}: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"API evaluation error: {e}")
        st.error(f"{t('api_error')}: {str(e)}")
        return None

def evaluate_locally(mapping: str) -> Optional[dict]:
    """Evaluate mapping locally"""
    try:
        import sys
        sys.path.append(str(Path(__file__).resolve().parents[1]))
        from engine.compliance import evaluate as local_eval
        return local_eval(mapping)
    except Exception as e:
        logger.error(f"Local evaluation error: {e}")
        st.error(f"{t('local_eval_error')}: {str(e)}")
        return None

def display_evaluation_results(result: dict):
    """Display evaluation results in a structured way"""
    status_color = {
        "COMPLIANT": "🟢",
        "PARTIAL": "🟡", 
        "GAPS": "🔴"
    }.get(result['status'], "⚪")
    
    st.subheader(f"{status_color} {t('status')}: {result['status']}")
    
    # Metadata
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t("policy"), result["policy"])
        st.metric(t("total_controls"), len(result["required"]))
    with col2:
        st.metric(t("compliant_controls"), len(result["provided"]))
        st.metric(t("missing_controls"), len(result["missing"]))
    
    # Vendors
    if result.get("vendors"):
        st.write(f"**{t('vendors')}:**")
        vendor_names = [v.get('vendor', 'Unknown') for v in result["vendors"]]
        st.write(", ".join(vendor_names))
    
    # Detailed breakdown
    st.subheader(t("detailed_breakdown"))
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.caption(t("required"))
        if result["required"]:
            st.code("\n".join(result["required"]), language="text")
        else:
            st.info(t("no_requirements"))
    
    with c2:
        st.caption(t("provided"))
        if result["provided"]:
            st.code("\n".join(result["provided"]), language="text")
        else:
            st.info(t("no_capabilities"))
    
    with c3:
        st.caption(t("missing"))
        if result["missing"]:
            st.code("\n".join(result["missing"]), language="text")
        else:
            st.success(t("fully_compliant"))

def display_benchmarks(benchmarks: dict, selected_sectors: list = None):
    """Display benchmark charts"""
    try:
        if not benchmarks:
            st.warning(t("no_benchmarks_data"))
            return
        
        # Default to Government and Banking if no selection
        if not selected_sectors:
            selected_sectors = ["Government", "Banking"]
        
        # Filter available sectors
        available_sectors = [s for s in selected_sectors if s in benchmarks]
        
        if not available_sectors:
            st.warning(t("no_selected_sectors_data"))
            return
        
        # Create DataFrame for visualization
        df_data = {}
        for sector in available_sectors:
            sector_data = benchmarks[sector]
            if "months" in sector_data and "SLA_met_pct" in sector_data:
                df_data[f"{sector}_SLA"] = sector_data["SLA_met_pct"]
        
        if df_data and "months" in benchmarks.get(available_sectors[0], {}):
            df = pd.DataFrame(df_data)
            df.index = benchmarks[available_sectors[0]]["months"]
            st.line_chart(df)
        else:
            st.warning(t("incomplete_benchmark_data"))
            
    except Exception as e:
        logger.error(f"Error displaying benchmarks: {e}")
        st.error(t("benchmark_display_error"))

# Main application
def main():
    # Page configuration
    st.set_page_config(
        page_title=t("title"), 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title
    st.title(t("title"))
    
    # Language selection
    lang = st.sidebar.selectbox(
        "Language / اللغة", 
        ["ar", "en"], 
        index=0 if st.session_state.get("lang", "ar") == "ar" else 1
    )
    st.session_state["lang"] = lang
    
    # API configuration
    API = os.environ.get("API_URL", "http://localhost:8000")
    
    # Check API health
    api_status = "🔴 Offline"
    try:
        health_response = requests.get(f"{API}/health", timeout=2)
        if health_response.status_code == 200:
            api_status = "🟢 Online"
    except:
        pass
    
    st.sidebar.write(f"**API Status:** {api_status}")
    
    # Get mappings
    mappings = get_mappings_from_api(API)
    if not mappings:
        st.sidebar.warning(t("api_unavailable_fallback"))
        mappings = get_local_mappings()
    
    if not mappings:
        st.error(t("no_mappings_available"))
        return
    
    # Sector and mapping selection
    sector = st.sidebar.selectbox(
        t("sector"), 
        ["Government", "Banking", "Health", "Energy", "SmartCity"]
    )
    mapping = st.sidebar.selectbox(t("mapping"), mappings)
    
    # Main content
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader(t("compliance_evaluation"))
        
        if st.button(t("evaluate_button"), use_container_width=True, type="primary"):
            with st.spinner(t("evaluating")):
                # Try API first, then local fallback
                result = evaluate_via_api(API, mapping)
                if not result:
                    st.info(t("trying_local_evaluation"))
                    result = evaluate_locally(mapping)
                
                if result:
                    display_evaluation_results(result)
                    
                    # Store result in session state for export
                    st.session_state["last_evaluation"] = result
                else:
                    st.error(t("evaluation_failed"))
        
        # Export functionality
        if "last_evaluation" in st.session_state:
            st.subheader(t("export_results"))
            result = st.session_state["last_evaluation"]
            
            # JSON export
            json_data = json.dumps(result, indent=2, ensure_ascii=False)
            st.download_button(
                label=t("download_json"),
                data=json_data,
                file_name=f"compliance_result_{result['mapping']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        st.subheader(t("benchmarks_title"))
        
        # Sector selection for benchmarks
        selected_sectors = st.multiselect(
            t("select_sectors_for_benchmarks"),
            ["Government", "Banking", "Health", "Energy"],
            default=["Government", "Banking"]
        )
        
        # Get and display benchmarks
        benchmarks = get_benchmarks_from_api(API)
        if not benchmarks:
            benchmarks = get_local_benchmarks()
        
        if benchmarks:
            display_benchmarks(benchmarks, selected_sectors)
        else:
            st.warning(t("benchmarks_unavailable"))

if __name__ == "__main__":
    main()
