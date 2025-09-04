#!/usr/bin/env python3
"""
Real-time Alerting System for DoganAI Compliance Kit
Implements comprehensive alerting with multiple notification channels
"""

import asyncio
import aiohttp
import smtplib
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """Alert notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"
    CONSOLE = "console"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

class AlertManager:
    """Comprehensive alert management system"""
    
    def __init__(self):
        self.alerts = []
        self.max_alerts = 1000
        self.alert_handlers = {}
        self.alert_rules = []
        self.notification_channels = {}
        
        # Initialize default channels
        self._setup_default_channels()
        
        # Alert rules
        self._setup_default_rules()
    
    def _setup_default_channels(self):
        """Setup default notification channels"""
        self.notification_channels = {
            AlertChannel.LOG: self._log_alert,
            AlertChannel.CONSOLE: self._console_alert
        }
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        self.alert_rules = [
            {
                'name': 'high_cpu_usage',
                'condition': lambda metrics: metrics.get('cpu_percent', 0) > 90,
                'severity': AlertSeverity.WARNING,
                'title': 'High CPU Usage',
                'message': 'CPU usage is above 90%'
            },
            {
                'name': 'high_memory_usage',
                'condition': lambda metrics: metrics.get('memory_percent', 0) > 90,
                'severity': AlertSeverity.WARNING,
                'title': 'High Memory Usage',
                'message': 'Memory usage is above 90%'
            },
            {
                'name': 'service_unhealthy',
                'condition': lambda health: health.get('status') == 'unhealthy',
                'severity': AlertSeverity.CRITICAL,
                'title': 'Service Unhealthy',
                'message': 'Critical service is unhealthy'
            },
            {
                'name': 'database_connection_failed',
                'condition': lambda health: any(
                    check.get('status') == 'unhealthy' and 'database' in check.get('component', '').lower()
                    for check in health.get('checks', {}).values()
                ),
                'severity': AlertSeverity.CRITICAL,
                'title': 'Database Connection Failed',
                'message': 'Database connection is unhealthy'
            },
            {
                'name': 'high_error_rate',
                'condition': lambda metrics: metrics.get('error_rate', 0) > 0.05,
                'severity': AlertSeverity.ERROR,
                'title': 'High Error Rate',
                'message': 'Error rate is above 5%'
            }
        ]
    
    def add_notification_channel(self, channel: AlertChannel, handler: Callable):
        """Add a notification channel"""
        self.notification_channels[channel] = handler
        logger.info(f"Added notification channel: {channel.value}")
    
    def setup_email_channel(self, smtp_server: str, smtp_port: int, username: str, password: str, recipients: List[str]):
        """Setup email notification channel"""
        def email_handler(alert: Alert):
            try:
                msg = f"Subject: {alert.title}\n\n{alert.message}\n\nSeverity: {alert.severity.value}\nSource: {alert.source}\nTimestamp: {alert.timestamp}"
                
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(username, password)
                    for recipient in recipients:
                        server.sendmail(username, recipient, msg)
                
                logger.info(f"Email alert sent to {recipients}")
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        self.add_notification_channel(AlertChannel.EMAIL, email_handler)
    
    def setup_slack_channel(self, webhook_url: str, channel: str = "#alerts"):
        """Setup Slack notification channel"""
        def slack_handler(alert: Alert):
            try:
                color_map = {
                    AlertSeverity.INFO: "#36a64f",
                    AlertSeverity.WARNING: "#ffa500",
                    AlertSeverity.ERROR: "#ff0000",
                    AlertSeverity.CRITICAL: "#8b0000"
                }
                
                payload = {
                    "channel": channel,
                    "attachments": [{
                        "color": color_map.get(alert.severity, "#000000"),
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {"title": "Severity", "value": alert.severity.value, "short": True},
                            {"title": "Source", "value": alert.source, "short": True},
                            {"title": "Timestamp", "value": alert.timestamp.isoformat(), "short": True}
                        ],
                        "footer": "DoganAI Compliance Kit"
                    }]
                }
                
                asyncio.create_task(self._send_webhook(webhook_url, payload))
                logger.info(f"Slack alert sent to {channel}")
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")
        
        self.add_notification_channel(AlertChannel.SLACK, slack_handler)
    
    def setup_webhook_channel(self, webhook_url: str):
        """Setup webhook notification channel"""
        def webhook_handler(alert: Alert):
            try:
                payload = {
                    "alert_id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity.value,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "metadata": alert.metadata
                }
                
                asyncio.create_task(self._send_webhook(webhook_url, payload))
                logger.info(f"Webhook alert sent to {webhook_url}")
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {e}")
        
        self.add_notification_channel(AlertChannel.WEBHOOK, webhook_handler)
    
    async def _send_webhook(self, url: str, payload: Dict[str, Any]):
        """Send webhook notification"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Webhook returned status {response.status}")
        except Exception as e:
            logger.error(f"Webhook request failed: {e}")
    
    def _log_alert(self, alert: Alert):
        """Log alert to file"""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        logger.log(log_level, f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.message}")
    
    def _console_alert(self, alert: Alert):
        """Print alert to console"""
        severity_colors = {
            AlertSeverity.INFO: "\033[32m",      # Green
            AlertSeverity.WARNING: "\033[33m",   # Yellow
            AlertSeverity.ERROR: "\033[31m",     # Red
            AlertSeverity.CRITICAL: "\033[35m"   # Magenta
        }
        
        color = severity_colors.get(alert.severity, "\033[0m")
        reset = "\033[0m"
        
        print(f"{color}[{alert.severity.value.upper()}] {alert.title}{reset}")
        print(f"  {alert.message}")
        print(f"  Source: {alert.source}")
        print(f"  Time: {alert.timestamp}")
        print()
    
    def create_alert(self, title: str, message: str, severity: AlertSeverity, source: str, metadata: Dict[str, Any] = None) -> Alert:
        """Create a new alert"""
        alert_id = f"{source}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            severity=severity,
            source=source,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Trim old alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # Send notifications
        self._send_notifications(alert)
        
        logger.info(f"Created alert: {alert_id} - {title}")
        return alert
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        for channel, handler in self.notification_channels.items():
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.value}: {e}")
    
    def check_alert_rules(self, metrics: Dict[str, Any], health_status: Dict[str, Any]):
        """Check alert rules and create alerts if conditions are met"""
        for rule in self.alert_rules:
            try:
                # Check if rule condition is met
                if rule['condition'](metrics) or rule['condition'](health_status):
                    # Check if similar alert already exists (within last 5 minutes)
                    recent_alerts = [
                        a for a in self.alerts[-10:]
                        if a.title == rule['title'] and 
                        (datetime.now(timezone.utc) - a.timestamp).seconds < 300
                    ]
                    
                    if not recent_alerts:
                        self.create_alert(
                            title=rule['title'],
                            message=rule['message'],
                            severity=rule['severity'],
                            source='alert_rules',
                            metadata={'rule_name': rule['name']}
                        )
            except Exception as e:
                logger.error(f"Error checking alert rule {rule['name']}: {e}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """Get active (unresolved) alerts"""
        alerts = [a for a in self.alerts if not a.resolved]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        active_alerts = self.get_active_alerts()
        
        return {
            'total_alerts': len(self.alerts),
            'active_alerts': len(active_alerts),
            'acknowledged_alerts': len([a for a in active_alerts if a.acknowledged]),
            'unacknowledged_alerts': len([a for a in active_alerts if not a.acknowledged]),
            'by_severity': {
                severity.value: len([a for a in active_alerts if a.severity == severity])
                for severity in AlertSeverity
            }
        }
    
    def clear_old_alerts(self, days: int = 30):
        """Clear alerts older than specified days"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        old_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        new_count = len(self.alerts)
        logger.info(f"Cleared {old_count - new_count} old alerts")

# Global alert manager instance
alert_manager = AlertManager()

def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance"""
    return alert_manager
