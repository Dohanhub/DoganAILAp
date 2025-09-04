"""
Enhanced Mobile UI and Progressive Web App Implementation
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st
from streamlit.components.v1 import html
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class PWAConfig:
    """Progressive Web App configuration"""
    
    @staticmethod
    def get_manifest() -> Dict[str, Any]:
        """Get PWA manifest configuration"""
        return {
            "name": "DoganAI Compliance Kit",
            "short_name": "DoganAI",
            "description": "Saudi Arabia Compliance Management Platform",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0B1020",
            "theme_color": "#57D0FF",
            "orientation": "portrait-primary",
            "categories": ["business", "productivity", "utilities"],
            "lang": "ar-SA",
            "dir": "rtl",
            "icons": [
                {
                    "src": "/static/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-96x96.png", 
                    "sizes": "96x96",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-128x128.png",
                    "sizes": "128x128", 
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ],
            "screenshots": [
                {
                    "src": "/static/screenshots/desktop-screenshot.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide"
                },
                {
                    "src": "/static/screenshots/mobile-screenshot.png",
                    "sizes": "375x667", 
                    "type": "image/png",
                    "form_factor": "narrow"
                }
            ]
        }
    
    @staticmethod
    def get_service_worker_js() -> str:
        """Get service worker JavaScript code"""
        return """
        const CACHE_NAME = 'doganai-compliance-v1';
        const urlsToCache = [
            '/',
            '/static/css/app.css',
            '/static/js/app.js',
            '/static/icons/icon-192x192.png',
            '/api/health'
        ];

        self.addEventListener('install', function(event) {
            event.waitUntil(
                caches.open(CACHE_NAME)
                    .then(function(cache) {
                        return cache.addAll(urlsToCache);
                    })
            );
        });

        self.addEventListener('fetch', function(event) {
            event.respondWith(
                caches.match(event.request)
                    .then(function(response) {
                        // Return cached version or fetch from network
                        return response || fetch(event.request);
                    }
                )
            );
        });

        // Handle push notifications
        self.addEventListener('push', function(event) {
            const options = {
                body: event.data ? event.data.text() : 'New compliance alert',
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/badge-72x72.png',
                vibrate: [200, 100, 200],
                data: {
                    dateOfArrival: Date.now(),
                    primaryKey: 1
                },
                actions: [
                    {
                        action: 'explore',
                        title: 'View Details',
                        icon: '/static/icons/checkmark.png'
                    },
                    {
                        action: 'close',
                        title: 'Close',
                        icon: '/static/icons/xmark.png'
                    }
                ]
            };

            event.waitUntil(
                self.registration.showNotification('DoganAI Compliance', options)
            );
        });
        """


class ResponsiveLayout:
    """Responsive layout manager for mobile and desktop"""
    
    def __init__(self):
        self.device_type = self._detect_device_type()
        self.is_mobile = self.device_type in ['mobile', 'tablet']
        
    def _detect_device_type(self) -> str:
        """Detect device type from user agent"""
        # In a real implementation, this would use JavaScript to detect device
        # For Streamlit, we'll use a simplified approach
        return 'mobile'  # Default to mobile-first
    
    def apply_mobile_styles(self):
        """Apply mobile-specific CSS styles"""
        mobile_css = """
        <style>
        /* Mobile-first responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem;
                max-width: 100%;
            }
            
            .stButton > button {
                width: 100%;
                height: 48px;
                font-size: 16px;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            
            .stSelectbox > div > div > div {
                font-size: 16px;
                padding: 12px;
            }
            
            .stTextInput > div > div > input {
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
            }
            
            /* Touch-friendly metrics cards */
            .metric-card {
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                padding: 20px;
                border-radius: 12px;
                margin: 8px 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                min-height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            .metric-title {
                color: #e2e8f0;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 8px;
            }
            
            .metric-value {
                color: white;
                font-size: 28px;
                font-weight: 700;
                line-height: 1;
            }
            
            .metric-delta {
                color: #10b981;
                font-size: 12px;
                margin-top: 4px;
            }
            
            /* RTL support for Arabic */
            .rtl {
                direction: rtl;
                text-align: right;
            }
            
            .rtl .stButton > button {
                text-align: center;
            }
            
            /* Dark theme */
            .stApp {
                background-color: #0B1020;
                color: #E6EAF2;
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 4px;
            }
            
            ::-webkit-scrollbar-track {
                background: #1a202c;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #4a5568;
                border-radius: 2px;
            }
            
            /* Offline indicator */
            .offline-indicator {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #f56565;
                color: white;
                text-align: center;
                padding: 8px;
                z-index: 1000;
                display: none;
            }
            
            .offline-indicator.show {
                display: block;
            }
        }
        
        /* Tablet styles */
        @media (min-width: 769px) and (max-width: 1024px) {
            .main .block-container {
                padding: 2rem;
                max-width: 95%;
            }
        }
        
        /* Desktop styles */
        @media (min-width: 1025px) {
            .main .block-container {
                padding: 3rem;
                max-width: 1200px;
            }
        }
        </style>
        """
        st.markdown(mobile_css, unsafe_allow_html=True)
    
    def create_grid_layout(self, columns: List[int], gap: str = "1rem"):
        """Create responsive grid layout"""
        if self.is_mobile:
            # Stack vertically on mobile
            return st.columns(1)
        else:
            return st.columns(columns, gap=gap)


class OfflineManager:
    """Manage offline functionality"""
    
    def __init__(self):
        self.cached_data = {}
        self.sync_queue = []
    
    def cache_data(self, key: str, data: Any):
        """Cache data for offline use"""
        self.cached_data[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'expires': (datetime.now().timestamp() + 3600)  # 1 hour
        }
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Get cached data"""
        if key in self.cached_data:
            cached = self.cached_data[key]
            if datetime.now().timestamp() < cached['expires']:
                return cached['data']
            else:
                del self.cached_data[key]
        return None
    
    def add_to_sync_queue(self, operation: Dict[str, Any]):
        """Add operation to sync queue for when online"""
        operation['queued_at'] = datetime.now().isoformat()
        self.sync_queue.append(operation)
    
    def get_offline_status_component(self):
        """Get offline status indicator component"""
        return """
        <div id="offline-indicator" class="offline-indicator">
            <span>?? Offline Mode - Changes will sync when connection is restored</span>
        </div>
        
        <script>
        function updateOnlineStatus() {
            const indicator = document.getElementById('offline-indicator');
            if (navigator.onLine) {
                indicator.classList.remove('show');
            } else {
                indicator.classList.add('show');
            }
        }
        
        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);
        updateOnlineStatus();
        </script>
        """


class TouchOptimizedComponents:
    """Touch-optimized UI components for mobile"""
    
    @staticmethod
    def create_touch_button(
        label: str, 
        key: str,
        icon: Optional[str] = None,
        variant: str = "primary",
        size: str = "large"
    ):
        """Create touch-optimized button"""
        icon_html = f'<i class="{icon}"></i> ' if icon else ''
        
        button_html = f"""
        <div class="touch-button touch-button-{variant} touch-button-{size}" 
             onclick="streamlit.setComponentValue('{key}', true)">
            {icon_html}{label}
        </div>
        """
        
        return html(button_html, height=60)
    
    @staticmethod
    def create_swipe_cards(items: List[Dict[str, Any]]):
        """Create swipeable cards for mobile navigation"""
        cards_html = """
        <div class="swipe-container">
        """
        
        for i, item in enumerate(items):
            cards_html += f"""
            <div class="swipe-card" data-index="{i}">
                <h3>{item.get('title', '')}</h3>
                <p>{item.get('description', '')}</p>
                <div class="card-actions">
                    <button onclick="handleCardAction('{item.get('action', '')}', {i})">
                        {item.get('action_label', 'View')}
                    </button>
                </div>
            </div>
            """
        
        cards_html += """
        </div>
        
        <style>
        .swipe-container {
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            gap: 16px;
            padding: 16px;
        }
        
        .swipe-card {
            min-width: 280px;
            scroll-snap-align: start;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            border-radius: 12px;
            padding: 20px;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .swipe-card h3 {
            margin: 0 0 12px 0;
            font-size: 18px;
            font-weight: 600;
        }
        
        .swipe-card p {
            margin: 0 0 16px 0;
            font-size: 14px;
            opacity: 0.9;
        }
        
        .card-actions button {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
        }
        </style>
        
        <script>
        function handleCardAction(action, index) {
            // Send action to Streamlit
            window.parent.postMessage({
                type: 'card_action',
                action: action,
                index: index
            }, '*');
        }
        </script>
        """
        
        return html(cards_html, height=200)
    
    @staticmethod
    def create_pull_to_refresh():
        """Create pull-to-refresh functionality"""
        refresh_html = """
        <div id="pull-to-refresh" class="pull-to-refresh">
            <div class="refresh-indicator">
                <div class="spinner"></div>
                <span>Pull to refresh</span>
            </div>
        </div>
        
        <style>
        .pull-to-refresh {
            position: fixed;
            top: -80px;
            left: 0;
            right: 0;
            height: 80px;
            background: #1a202c;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: top 0.3s ease;
            z-index: 1000;
        }
        
        .pull-to-refresh.active {
            top: 0;
        }
        
        .refresh-indicator {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #e2e8f0;
            font-size: 14px;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #4a5568;
            border-top: 2px solid #57D0FF;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        
        <script>
        let startY = 0;
        let pullDistance = 0;
        const threshold = 80;
        
        document.addEventListener('touchstart', function(e) {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        });
        
        document.addEventListener('touchmove', function(e) {
            if (startY > 0) {
                pullDistance = e.touches[0].clientY - startY;
                const refreshEl = document.getElementById('pull-to-refresh');
                
                if (pullDistance > 0) {
                    e.preventDefault();
                    refreshEl.style.top = Math.min(pullDistance - 80, 0) + 'px';
                    
                    if (pullDistance > threshold) {
                        refreshEl.classList.add('active');
                    } else {
                        refreshEl.classList.remove('active');
                    }
                }
            }
        });
        
        document.addEventListener('touchend', function(e) {
            const refreshEl = document.getElementById('pull-to-refresh');
            
            if (pullDistance > threshold) {
                // Trigger refresh
                window.parent.postMessage({
                    type: 'refresh_requested'
                }, '*');
            }
            
            refreshEl.style.top = '-80px';
            refreshEl.classList.remove('active');
            startY = 0;
            pullDistance = 0;
        });
        </script>
        """
        
        return html(refresh_html, height=0)


class MobileOptimizedCharts:
    """Mobile-optimized chart configurations"""
    
    @staticmethod
    def create_mobile_metric_chart(
        title: str,
        value: float,
        delta: Optional[float] = None,
        format_type: str = "number"
    ):
        """Create mobile-optimized metric chart"""
        
        # Create gauge chart for mobile
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title, 'font': {'size': 16, 'color': '#E6EAF2'}},
            delta = {'reference': delta} if delta else None,
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': '#8EA3B0'},
                'bar': {'color': "#57D0FF"},
                'steps': [
                    {'range': [0, 50], 'color': "#1A2332"},
                    {'range': [50, 80], 'color': "#2A3441"},
                    {'range': [80, 100], 'color': "#3A4551"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='#0B1020',
            plot_bgcolor='#0B1020',
            font={'color': '#E6EAF2'},
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_mobile_timeline_chart(data: List[Dict[str, Any]]):
        """Create mobile-optimized timeline chart"""
        
        fig = go.Figure()
        
        # Extract data
        dates = [item['date'] for item in data]
        values = [item['value'] for item in data]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            line=dict(color='#57D0FF', width=3),
            marker=dict(size=8, color='#57D0FF'),
            fill='tonexty',
            fillcolor='rgba(87, 208, 255, 0.1)'
        ))
        
        fig.update_layout(
            paper_bgcolor='#0B1020',
            plot_bgcolor='#0B1020',
            font={'color': '#E6EAF2'},
            height=250,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#2D3748',
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#2D3748',
                showline=False,
                tickfont=dict(size=10)
            ),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_mobile_compliance_donut(compliance_data: Dict[str, int]):
        """Create mobile-optimized compliance donut chart"""
        
        labels = list(compliance_data.keys())
        values = list(compliance_data.values())
        colors = ['#10B981', '#F59E0B', '#EF4444', '#6B7280']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=10,
            textposition='outside'
        )])
        
        fig.update_layout(
            paper_bgcolor='#0B1020',
            plot_bgcolor='#0B1020',
            font={'color': '#E6EAF2'},
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            annotations=[dict(
                text=f'{sum(values)}<br>Total',
                x=0.5, y=0.5,
                font_size=16,
                font_color='#E6EAF2',
                showarrow=False
            )]
        )
        
        return fig


class NotificationManager:
    """Push notification management"""
    
    def __init__(self):
        self.vapid_public_key = "your-vapid-public-key"  # Replace with actual key
    
    def get_notification_setup_js(self) -> str:
        """Get JavaScript for setting up push notifications"""
        return f"""
        <script>
        const publicVapidKey = '{self.vapid_public_key}';
        
        // Check for service worker support
        if ('serviceWorker' in navigator && 'PushManager' in window) {{
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {{
                    console.log('Service Worker registered');
                    return registration.pushManager.getSubscription();
                }})
                .then(function(subscription) {{
                    if (subscription === null) {{
                        // User is not subscribed
                        return subscribeToPush();
                    }} else {{
                        // User is already subscribed
                        console.log('User is already subscribed');
                    }}
                }})
                .catch(function(error) {{
                    console.error('Service Worker registration failed:', error);
                }});
        }}
        
        function subscribeToPush() {{
            return navigator.serviceWorker.ready
                .then(function(registration) {{
                    const subscribeOptions = {{
                        userVisibleOnly: true,
                        applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
                    }};
                    
                    return registration.pushManager.subscribe(subscribeOptions);
                }})
                .then(function(subscription) {{
                    console.log('User subscribed:', subscription);
                    
                    // Send subscription to server
                    return fetch('/api/notifications/subscribe', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify(subscription)
                    }});
                }})
                .catch(function(error) {{
                    console.error('Failed to subscribe:', error);
                }});
        }}
        
        function urlBase64ToUint8Array(base64String) {{
            const padding = '='.repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                .replace(/-/g, '+')
                .replace(/_/g, '/');
            
            const rawData = window.atob(base64);
            const outputArray = new Uint8Array(rawData.length);
            
            for (let i = 0; i < rawData.length; ++i) {{
                outputArray[i] = rawData.charCodeAt(i);
            }}
            return outputArray;
        }}
        
        // Request notification permission
        function requestNotificationPermission() {{
            return Notification.requestPermission().then(function(permission) {{
                if (permission === 'granted') {{
                    console.log('Notification permission granted');
                    subscribeToPush();
                }} else {{
                    console.log('Notification permission denied');
                }}
            }});
        }}
        
        // Show notification button if not granted
        if (Notification.permission === 'default') {{
            const notifyButton = document.createElement('button');
            notifyButton.textContent = 'Enable Notifications';
            notifyButton.onclick = requestNotificationPermission;
            notifyButton.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #57D0FF;
                color: #001018;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                z-index: 1000;
            `;
            document.body.appendChild(notifyButton);
        }}
        </script>
        """
    
    def send_notification(self, title: str, body: str, data: Optional[Dict] = None):
        """Send push notification (server-side implementation needed)"""
        # This would typically call a server endpoint to send the notification
        notification_payload = {
            'title': title,
            'body': body,
            'icon': '/static/icons/icon-192x192.png',
            'badge': '/static/icons/badge-72x72.png',
            'data': data or {},
            'actions': [
                {'action': 'view', 'title': 'View'},
                {'action': 'dismiss', 'title': 'Dismiss'}
            ]
        }
        
        return notification_payload


def create_mobile_app_layout():
    """Create the main mobile app layout"""
    layout = ResponsiveLayout()
    layout.apply_mobile_styles()
    
    # PWA setup
    pwa_config = PWAConfig()
    manifest = pwa_config.get_manifest()
    
    # Add PWA meta tags
    pwa_html = f"""
    <link rel="manifest" href="data:application/json;base64,{json.dumps(manifest)}">
    <meta name="theme-color" content="#57D0FF">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="DoganAI">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    """
    
    st.markdown(pwa_html, unsafe_allow_html=True)
    
    # Offline functionality
    offline_manager = OfflineManager()
    st.markdown(offline_manager.get_offline_status_component(), unsafe_allow_html=True)
    
    # Pull to refresh
    touch_components = TouchOptimizedComponents()
    touch_components.create_pull_to_refresh()
    
    # Notification setup
    notification_manager = NotificationManager()
    st.markdown(notification_manager.get_notification_setup_js(), unsafe_allow_html=True)
    
    return layout, offline_manager, notification_manager