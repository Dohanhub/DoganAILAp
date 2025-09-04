#!/usr/bin/env python3
"""
Governance Dashboard
Web interface for viewing and managing service governance information
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from governance.governance_manager import GovernanceManager, SLATier, IncidentSeverity

def load_governance_manager():
    """Load governance manager with caching"""
    if 'governance_manager' not in st.session_state:
        st.session_state.governance_manager = GovernanceManager()
    return st.session_state.governance_manager

def main():
    """Main dashboard application"""
    st.set_page_config(
        page_title="DoganAI Governance Dashboard",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏛️ DoganAI Governance Dashboard")
    st.markdown("**Service Ownership, SLA Tracking, and Compliance Management**")
    
    # Load governance manager
    manager = load_governance_manager()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        [
            "Overview",
            "Service Catalog",
            "Ownership Tracking",
            "SLA Monitoring",
            "Maintenance Schedule",
            "Compliance Dashboard",
            "Incident Response"
        ]
    )
    
    if page == "Overview":
        show_overview(manager)
    elif page == "Service Catalog":
        show_service_catalog(manager)
    elif page == "Ownership Tracking":
        show_ownership_tracking(manager)
    elif page == "SLA Monitoring":
        show_sla_monitoring(manager)
    elif page == "Maintenance Schedule":
        show_maintenance_schedule(manager)
    elif page == "Compliance Dashboard":
        show_compliance_dashboard(manager)
    elif page == "Incident Response":
        show_incident_response(manager)

def show_overview(manager):
    """Show governance overview dashboard"""
    st.header("📊 Governance Overview")
    
    # Generate governance report
    report = manager.generate_governance_report()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Services",
            report['total_services'],
            help="Total number of services in the catalog"
        )
    
    with col2:
        st.metric(
            "Ownership Coverage",
            f"{report['summary']['ownership_coverage']:.1f}%",
            help="Percentage of services with complete ownership information"
        )
    
    with col3:
        st.metric(
            "Avg Compliance Score",
            f"{report['summary']['average_compliance_score']:.1f}",
            help="Average compliance score across all services"
        )
    
    with col4:
        st.metric(
            "Maintenance Coverage",
            f"{report['summary']['maintenance_coverage']:.1f}%",
            help="Percentage of services with defined maintenance windows"
        )
    
    # SLA Tier Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("SLA Tier Distribution")
        sla_data = report['summary']['sla_tiers']
        
        if sla_data:
            fig = px.pie(
                values=list(sla_data.values()),
                names=list(sla_data.keys()),
                title="Services by SLA Tier",
                color_discrete_map={
                    'critical': '#ff4444',
                    'high': '#ff8800',
                    'medium': '#ffcc00',
                    'low': '#88cc00'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Compliance Scores")
        
        # Create compliance score distribution
        scores = [service['compliance_score'] for service in report['services'].values()]
        
        if scores:
            fig = px.histogram(
                x=scores,
                nbins=10,
                title="Compliance Score Distribution",
                labels={'x': 'Compliance Score', 'y': 'Number of Services'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent governance activities
    st.subheader("📋 Recent Activities")
    
    activities = [
        {
            "timestamp": datetime.now() - timedelta(hours=2),
            "activity": "SLA review completed for doganai-compliance-kit",
            "type": "review",
            "status": "completed"
        },
        {
            "timestamp": datetime.now() - timedelta(hours=6),
            "activity": "Ownership updated for observability-system",
            "type": "ownership",
            "status": "completed"
        },
        {
            "timestamp": datetime.now() - timedelta(days=1),
            "activity": "Maintenance window scheduled for compliance-report-generator",
            "type": "maintenance",
            "status": "scheduled"
        }
    ]
    
    for activity in activities:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(activity['activity'])
            with col2:
                st.write(activity['timestamp'].strftime('%Y-%m-%d %H:%M'))
            with col3:
                status_color = "🟢" if activity['status'] == 'completed' else "🟡"
                st.write(f"{status_color} {activity['status']}")

def show_service_catalog(manager):
    """Show service catalog with detailed information"""
    st.header("📚 Service Catalog")
    
    # Get all services
    services_data = manager.catalog_data.get('services', {})
    
    if not services_data:
        st.warning("No services found in catalog")
        return
    
    # Service selection
    selected_service = st.selectbox(
        "Select Service",
        list(services_data.keys()),
        help="Choose a service to view detailed information"
    )
    
    if selected_service:
        service_info = manager.get_service_info(selected_service)
        
        if service_info:
            # Service metadata
            st.subheader(f"📋 {service_info.name}")
            st.write(service_info.description)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Version", service_info.version)
            with col2:
                st.metric("Environment", service_info.environment)
            with col3:
                st.metric("SLA Tier", service_info.sla_targets.tier.value.title())
            
            # Ownership information
            st.subheader("👥 Ownership")
            owners = manager.get_service_owners(selected_service)
            
            for owner in owners:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**Team:** {owner.team}")
                    with col2:
                        st.write(f"**Email:** {owner.email}")
                    with col3:
                        st.write(f"**Slack:** {owner.slack or 'N/A'}")
                    with col4:
                        st.write(f"**Role:** {owner.responsibility or 'Primary'}")
            
            # SLA targets
            st.subheader("🎯 SLA Targets")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Availability", service_info.sla_targets.availability_target)
                st.metric("Response Time", service_info.sla_targets.response_time_target)
            
            with col2:
                st.metric("Error Rate", service_info.sla_targets.error_rate_target)
                st.metric("RTO", service_info.sla_targets.recovery_time_objective)
            
            with col3:
                st.metric("RPO", service_info.sla_targets.recovery_point_objective)
            
            # Dependencies
            if service_info.dependencies:
                st.subheader("🔗 Dependencies")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'upstream' in service_info.dependencies:
                        st.write("**Upstream Dependencies:**")
                        for dep in service_info.dependencies['upstream']:
                            st.write(f"- {dep}")
                
                with col2:
                    if 'downstream' in service_info.dependencies:
                        st.write("**Downstream Dependencies:**")
                        for dep in service_info.dependencies['downstream']:
                            st.write(f"- {dep}")
            
            # Compliance frameworks
            if service_info.compliance_frameworks:
                st.subheader("🛡️ Compliance Frameworks")
                for framework in service_info.compliance_frameworks:
                    st.badge(framework)

def show_ownership_tracking(manager):
    """Show ownership tracking dashboard"""
    st.header("👥 Ownership Tracking")
    
    # Team overview
    services_data = manager.catalog_data.get('services', {})
    team_services = {}
    
    for service_name in services_data:
        owners = manager.get_service_owners(service_name)
        for owner in owners:
            if owner.responsibility == 'primary' or not owner.responsibility:
                if owner.team not in team_services:
                    team_services[owner.team] = []
                team_services[owner.team].append(service_name)
                break
    
    # Team selection
    selected_team = st.selectbox(
        "Select Team",
        ['All Teams'] + list(team_services.keys()),
        help="Choose a team to view their owned services"
    )
    
    if selected_team == 'All Teams':
        # Show all teams overview
        st.subheader("📊 Team Service Ownership")
        
        team_data = []
        for team, services in team_services.items():
            team_data.append({
                'Team': team,
                'Services Count': len(services),
                'Services': ', '.join(services)
            })
        
        df = pd.DataFrame(team_data)
        st.dataframe(df, use_container_width=True)
        
        # Ownership distribution chart
        fig = px.bar(
            df,
            x='Team',
            y='Services Count',
            title="Services per Team",
            color='Services Count',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # Show specific team details
        st.subheader(f"📋 {selected_team} - Owned Services")
        
        if selected_team in team_services:
            services = team_services[selected_team]
            
            for service_name in services:
                with st.expander(f"🔧 {service_name}"):
                    service_info = manager.get_service_info(service_name)
                    if service_info:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Description:** {service_info.description}")
                            st.write(f"**SLA Tier:** {service_info.sla_targets.tier.value.title()}")
                        
                        with col2:
                            st.write(f"**Version:** {service_info.version}")
                            st.write(f"**Environment:** {service_info.environment}")
                        
                        # Show all owners
                        owners = manager.get_service_owners(service_name)
                        st.write("**All Owners:**")
                        for owner in owners:
                            st.write(f"- {owner.team} ({owner.responsibility or 'primary'}) - {owner.email}")
        else:
            st.info(f"No services found for team {selected_team}")

def show_sla_monitoring(manager):
    """Show SLA monitoring dashboard"""
    st.header("🎯 SLA Monitoring")
    
    # SLA tier filter
    tier_filter = st.selectbox(
        "Filter by SLA Tier",
        ['All Tiers'] + [tier.value.title() for tier in SLATier],
        help="Filter services by SLA tier"
    )
    
    services_data = manager.catalog_data.get('services', {})
    sla_data = []
    
    for service_name in services_data:
        service_info = manager.get_service_info(service_name)
        if service_info:
            if tier_filter == 'All Tiers' or service_info.sla_targets.tier.value.title() == tier_filter:
                sla_data.append({
                    'Service': service_name,
                    'SLA Tier': service_info.sla_targets.tier.value.title(),
                    'Availability Target': service_info.sla_targets.availability_target,
                    'Response Time Target': service_info.sla_targets.response_time_target,
                    'Error Rate Target': service_info.sla_targets.error_rate_target,
                    'RTO': service_info.sla_targets.recovery_time_objective,
                    'RPO': service_info.sla_targets.recovery_point_objective,
                    'Owner': service_info.ownership.team
                })
    
    if sla_data:
        df = pd.DataFrame(sla_data)
        st.dataframe(df, use_container_width=True)
        
        # SLA compliance simulation (in real implementation, this would come from monitoring data)
        st.subheader("📈 SLA Performance (Simulated)")
        
        # Generate mock performance data
        performance_data = []
        for service in sla_data:
            # Simulate current performance
            import random
            availability = random.uniform(99.0, 99.99)
            response_time = random.uniform(100, 800)
            error_rate = random.uniform(0.01, 0.5)
            
            performance_data.append({
                'Service': service['Service'],
                'Current Availability': f"{availability:.2f}%",
                'Current Response Time': f"{response_time:.0f}ms",
                'Current Error Rate': f"{error_rate:.2f}%",
                'Availability Status': '🟢' if availability >= 99.9 else '🟡' if availability >= 99.5 else '🔴',
                'Response Time Status': '🟢' if response_time <= 500 else '🟡' if response_time <= 1000 else '🔴',
                'Error Rate Status': '🟢' if error_rate <= 0.1 else '🟡' if error_rate <= 0.5 else '🔴'
            })
        
        perf_df = pd.DataFrame(performance_data)
        st.dataframe(perf_df, use_container_width=True)
        
    else:
        st.info("No services found for the selected SLA tier")

def show_maintenance_schedule(manager):
    """Show maintenance schedule dashboard"""
    st.header("🔧 Maintenance Schedule")
    
    services_data = manager.catalog_data.get('services', {})
    
    # Upcoming maintenance windows
    st.subheader("📅 Upcoming Maintenance Windows")
    
    maintenance_data = []
    for service_name in services_data:
        next_window = manager.get_next_maintenance_window(service_name)
        if next_window:
            service_info = manager.get_service_info(service_name)
            maintenance_data.append({
                'Service': service_name,
                'Owner': service_info.ownership.team if service_info else 'Unknown',
                'Date': next_window['date'],
                'Time': next_window['time'],
                'Duration': next_window['duration'],
                'Activities': ', '.join(next_window['activities'][:3]) + ('...' if len(next_window['activities']) > 3 else '')
            })
    
    if maintenance_data:
        df = pd.DataFrame(maintenance_data)
        df = df.sort_values('Date')
        st.dataframe(df, use_container_width=True)
        
        # Maintenance calendar view
        st.subheader("📊 Maintenance Calendar")
        
        # Create a simple calendar visualization
        fig = px.timeline(
            df,
            x_start='Date',
            x_end='Date',
            y='Service',
            color='Owner',
            title="Upcoming Maintenance Windows",
            hover_data=['Time', 'Duration', 'Activities']
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No upcoming maintenance windows scheduled")
    
    # Maintenance history (simulated)
    st.subheader("📋 Recent Maintenance History")
    
    history_data = [
        {
            'Service': 'doganai-compliance-kit',
            'Date': '2025-08-22',
            'Type': 'Weekly',
            'Duration': '2 hours',
            'Status': 'Completed',
            'Issues': 'None'
        },
        {
            'Service': 'observability-system',
            'Date': '2025-08-15',
            'Type': 'Monthly',
            'Duration': '4 hours',
            'Status': 'Completed',
            'Issues': 'Minor delay'
        }
    ]
    
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)

def show_compliance_dashboard(manager):
    """Show compliance dashboard"""
    st.header("🛡️ Compliance Dashboard")
    
    # Generate compliance report
    services_data = manager.catalog_data.get('services', {})
    compliance_data = []
    
    for service_name in services_data:
        compliance = manager.validate_service_compliance(service_name)
        service_info = manager.get_service_info(service_name)
        
        compliance_data.append({
            'Service': service_name,
            'Owner': service_info.ownership.team if service_info else 'Unknown',
            'Compliance Score': compliance['compliance_score'],
            'Errors': len(compliance['errors']),
            'Warnings': len(compliance['warnings']),
            'Status': '🟢' if compliance['compliance_score'] >= 90 else '🟡' if compliance['compliance_score'] >= 70 else '🔴',
            'Frameworks': ', '.join(service_info.compliance_frameworks) if service_info and service_info.compliance_frameworks else 'None'
        })
    
    if compliance_data:
        df = pd.DataFrame(compliance_data)
        
        # Overall compliance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_score = df['Compliance Score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}")
        
        with col2:
            compliant_services = len(df[df['Compliance Score'] >= 90])
            st.metric("Compliant Services", f"{compliant_services}/{len(df)}")
        
        with col3:
            total_errors = df['Errors'].sum()
            st.metric("Total Errors", total_errors)
        
        with col4:
            total_warnings = df['Warnings'].sum()
            st.metric("Total Warnings", total_warnings)
        
        # Compliance table
        st.subheader("📊 Service Compliance Status")
        st.dataframe(df, use_container_width=True)
        
        # Compliance score distribution
        fig = px.histogram(
            df,
            x='Compliance Score',
            nbins=10,
            title="Compliance Score Distribution",
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Services with issues
        issues_df = df[(df['Errors'] > 0) | (df['Warnings'] > 0)]
        if not issues_df.empty:
            st.subheader("⚠️ Services Requiring Attention")
            st.dataframe(issues_df, use_container_width=True)
            
            # Show detailed issues for selected service
            if st.button("Show Detailed Issues"):
                for _, row in issues_df.iterrows():
                    with st.expander(f"🔍 {row['Service']} - Issues"):
                        compliance = manager.validate_service_compliance(row['Service'])
                        
                        if compliance['errors']:
                            st.error("**Errors:**")
                            for error in compliance['errors']:
                                st.write(f"- {error}")
                        
                        if compliance['warnings']:
                            st.warning("**Warnings:**")
                            for warning in compliance['warnings']:
                                st.write(f"- {warning}")
    
    else:
        st.info("No compliance data available")

def show_incident_response(manager):
    """Show incident response dashboard"""
    st.header("🚨 Incident Response")
    
    # Service selection for incident response info
    services_data = manager.catalog_data.get('services', {})
    selected_service = st.selectbox(
        "Select Service",
        list(services_data.keys()),
        help="Choose a service to view incident response requirements"
    )
    
    # Severity selection
    severity = st.selectbox(
        "Incident Severity",
        [s.value.upper() for s in IncidentSeverity],
        help="Select incident severity level"
    )
    
    if selected_service and severity:
        severity_enum = IncidentSeverity(severity.lower())
        requirements = manager.get_incident_response_requirements(selected_service, severity_enum)
        
        st.subheader(f"📋 Incident Response for {selected_service} ({severity})")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Response Time", requirements.get('response_time', 'N/A'))
        
        with col2:
            st.metric("Escalation Policy", requirements.get('escalation_policy', 'N/A'))
        
        with col3:
            on_call = "Yes" if requirements.get('on_call_required', False) else "No"
            st.metric("On-Call Required", on_call)
        
        # Show service owners for contact
        st.subheader("👥 Contact Information")
        owners = manager.get_service_owners(selected_service)
        
        for owner in owners:
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{owner.team}**")
                with col2:
                    st.write(f"📧 {owner.email}")
                with col3:
                    st.write(f"💬 {owner.slack or 'N/A'}")
    
    # Incident response playbook
    st.subheader("📖 Incident Response Playbook")
    
    with st.expander("🚨 P0/P1 Incident Response (0-15 minutes)"):
        st.code("""
# Immediate assessment
curl -f https://doganai-compliance.com/health || echo "Service DOWN"
curl -s https://doganai-compliance.com/metrics | grep error_rate

# Check recent deployments
gh run list --limit 5
kubectl rollout history deployment/compliance-kit

# Review critical metrics
curl -s https://doganai-compliance.com/observability/status
        """, language="bash")
    
    with st.expander("🔄 Emergency Rollback Procedures"):
        st.code("""
# Feature flag rollback (30 seconds)
curl -X PUT "https://doganai-compliance.com/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false, "rollout": {"strategy": "off", "percentage": 0.0}}'

# Application rollback (2-5 minutes)
kubectl rollout undo deployment/compliance-kit
kubectl rollout status deployment/compliance-kit --timeout=300s
        """, language="bash")
    
    # Recent incidents (simulated)
    st.subheader("📊 Recent Incidents")
    
    incident_data = [
        {
            'Date': '2025-08-28',
            'Service': 'doganai-compliance-kit',
            'Severity': 'P1',
            'Duration': '45 minutes',
            'Root Cause': 'Database connection pool exhaustion',
            'Status': 'Resolved'
        },
        {
            'Date': '2025-08-25',
            'Service': 'feature-flag-system',
            'Severity': 'P2',
            'Duration': '2 hours',
            'Root Cause': 'Configuration syntax error',
            'Status': 'Resolved'
        }
    ]
    
    incident_df = pd.DataFrame(incident_data)
    st.dataframe(incident_df, use_container_width=True)

if __name__ == "__main__":
    main()