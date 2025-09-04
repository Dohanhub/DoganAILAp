#!/usr/bin/env python3
"""
Template Engine for DoganAI Compliance Kit
Generates HTML dynamically from configuration files
"""

import json
from typing import Dict, Any, List
from config_manager import config_manager

class TemplateEngine:
    """Generates HTML templates dynamically from configuration"""
    
    def __init__(self):
        self.config = config_manager
    
    def generate_dashboard_html(self, language: str = "en") -> str:
        """Generate complete dashboard HTML from configuration"""
        
        # Get configuration data
        dashboard_config = self.config.get_config("dashboard_config.json")
        theme_colors = self.config.get_theme_colors()
        
        # Generate CSS variables
        css_variables = self._generate_css_variables(theme_colors)
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="{language}" dir="{'rtl' if self.config.is_rtl_language(language) else 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.get_language_text('dashboard.title', language)}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        {css_variables}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--dark-bg);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        
        .navbar {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 1rem 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .navbar-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .logo {{
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
        }}
        
        .nav-links {{
            display: flex;
            gap: 2rem;
        }}
        
        .nav-link {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            transition: background-color 0.3s;
        }}
        
        .nav-link:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 2rem;
        }}
        
        .sidebar {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            height: fit-content;
        }}
        
        .sidebar h3 {{
            color: var(--accent-color);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }}
        
        .action-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.3s;
            color: var(--text-primary);
            text-decoration: none;
        }}
        
        .action-item:hover {{
            background: var(--primary-color);
        }}
        
        .action-item i {{
            color: var(--accent-color);
            width: 20px;
        }}
        
        .main-content {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 2rem;
        }}
        
        .main-content h2 {{
            color: var(--accent-color);
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: var(--dark-bg);
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid var(--accent-color);
        }}
        
        .metric-card h3 {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .metric-card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent-color);
        }}
        
        .metric-card i {{
            font-size: 2.5rem;
            color: var(--accent-color);
            margin-bottom: 1rem;
        }}
        
        .activity-section {{
            background: var(--dark-bg);
            padding: 1.5rem;
            border-radius: 8px;
        }}
        
        .activity-section h3 {{
            color: var(--accent-color);
            margin-bottom: 1rem;
        }}
        
        .activity-item {{
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .activity-item:last-child {{
            border-bottom: none;
        }}
        
        .language-switcher {{
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .language-btn {{
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin: 0.25rem;
        }}
        
        .language-btn:hover {{
            background: var(--secondary-color);
        }}
        
        .language-btn.active {{
            background: var(--accent-color);
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">
                <i class="fas fa-shield-alt"></i> {self.config.get_language_text('dashboard.title', language)}
            </div>
            <div class="nav-links">
                <a href="#" class="nav-link">{self.config.get_language_text('dashboard.navigation.dashboard', language)}</a>
                <a href="#" class="nav-link">{self.config.get_language_text('dashboard.navigation.compliance_test', language)}</a>
                <a href="#" class="nav-link">{self.config.get_language_text('dashboard.navigation.reports', language)}</a>
                <a href="#" class="nav-link">{self.config.get_language_text('dashboard.navigation.ai_analysis', language)}</a>
            </div>
        </div>
    </nav>
    
    <!-- Language Switcher -->
    <div class="language-switcher">
        <h4>Language / اللغة</h4>
        <button class="language-btn {'active' if language == 'en' else ''}" onclick="switchLanguage('en')">English</button>
        <button class="language-btn {'active' if language == 'ar' else ''}" onclick="switchLanguage('ar')">العربية</button>
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <!-- Sidebar -->
            <div class="sidebar">
                <h3><i class="fas fa-cogs"></i> {self.config.get_language_text('dashboard.sections.quick_actions', language)}</h3>
                {self._generate_sidebar_actions(language)}
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <h2><i class="fas fa-tachometer-alt"></i> {self.config.get_language_text('dashboard.sections.overview', language)}</h2>
                
                <!-- Metrics Grid -->
                <div class="metrics-grid">
                    {self._generate_metrics_cards(language)}
                </div>
                
                <!-- Recent Activity -->
                <div class="activity-section">
                    <h3><i class="fas fa-chart-line"></i> {self.config.get_language_text('dashboard.sections.recent_activity', language)}</h3>
                    <div id="recent-activity">
                        <div class="activity-item">
                            <span>{self.config.get_language_text('dashboard.sections.recent_activity', language)}...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Dashboard functionality
        let currentLanguage = '{language}';
        
        function switchLanguage(lang) {{
            currentLanguage = lang;
            // Reload page with new language
            window.location.href = `/?lang=${{lang}}`;
        }}
        
        // Load dashboard data
        async function loadDashboardData() {{
            try {{
                console.log('🚀 Loading dashboard data...');
                
                // Load overview data
                const overviewResponse = await fetch('/api/dashboard/overview');
                if (overviewResponse.ok) {{
                    const overviewData = await overviewResponse.json();
                    console.log('📊 Overview data:', overviewData);
                    
                    // Update metrics with proper IDs
                    updateMetric('total_tests', overviewData.total_tests);
                    updateMetric('compliance_rate', overviewData.compliance_rate + '%');
                    updateMetric('active_policies', overviewData.active_policies);
                    updateMetric('ai_insights', overviewData.ai_insights);
                    
                    console.log('✅ All metrics updated successfully');
                }} else {{
                    console.error('❌ Failed to load overview data:', overviewResponse.status);
                }}
                
                // Load recent activity
                const activityResponse = await fetch('/api/dashboard/activity');
                if (activityResponse.ok) {{
                    const activityData = await activityResponse.json();
                    updateRecentActivity(activityData);
                    console.log('✅ Recent activity updated');
                }} else {{
                    console.error('❌ Failed to load activity data:', activityResponse.status);
                }}
                
            }} catch (error) {{
                console.error('❌ Error loading dashboard:', error);
            }}
        }}
        
        function updateMetric(id, value) {{
            const element = document.getElementById(id);
            if (element) {{
                element.textContent = value;
                console.log('✅ Updated metric ' + id + ': ' + value);
            }} else {{
                console.warn('⚠️ Element with id \'' + id + '\' not found');
            }}
        }}
        
        function updateRecentActivity(activities) {{
            const container = document.getElementById('recent-activity');
            if (!container) return;
            
            const activityHtml = activities.map(activity => `
                <div class="activity-item">
                    <div>
                        <div><strong>${{activity.action}}</strong></div>
                        <div style="font-size: 0.9rem; color: var(--text-secondary);">${{activity.description}}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">${{new Date(activity.timestamp).toLocaleString()}}</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">Status: ${{activity.status}}</div>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = activityHtml;
        }}
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            loadDashboardData();
            
            // Auto-refresh every 30 seconds
            setInterval(loadDashboardData, 30000);
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    def _generate_css_variables(self, theme_colors: Dict[str, str]) -> str:
        """Generate CSS variables from theme configuration"""
        css_vars = []
        for key, value in theme_colors.items():
            css_vars.append(f"        --{key.replace('_', '-')}: {value};")
        
        return f"""
        :root {{
{chr(10).join(css_vars)}
        }}"""
    
    def _generate_sidebar_actions(self, language: str) -> str:
        """Generate sidebar action items from configuration"""
        actions = self.config.get_config("dashboard_config.json", "dashboard.actions")
        
        if not actions:
            return "<p>No actions configured</p>"
        
        action_html = []
        for action in actions:
            action_html.append(f"""
                <a href="#" class="action-item" onclick="handleAction('{action['id']}')">
                    <i class="{action['icon']}"></i>
                    <span>{action[language] if language in action else action.get('en', action['id'])}</span>
                </a>
            """)
        
        return chr(10).join(action_html)
    
    def _generate_metrics_cards(self, language: str) -> str:
        """Generate metric cards from configuration"""
        metrics = self.config.get_config("dashboard_config.json", "dashboard.metrics")
        
        if not metrics:
            return "<p>No metrics configured</p>"
        
        metric_html = []
        for metric_id, metric_config in metrics.items():
            metric_html.append(f"""
                <div class="metric-card">
                    <i class="{metric_config['icon']}"></i>
                    <h3>{metric_config[language] if language in metric_config else metric_config.get('en', metric_id)}</h3>
                    <div class="value" id="{metric_id}">0</div>
                </div>
            """)
        
        return chr(10).join(metric_html)

# Global template engine instance
template_engine = TemplateEngine()
