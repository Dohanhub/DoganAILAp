#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Feature Flags Manager
Configuration-driven feature flags for gradual rollout and canary deployments
"""

import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import threading

import structlog
from observability.metrics import observability

# Configure logging
logger = structlog.get_logger("feature_flags")

# =============================================================================
# FEATURE FLAG MODELS
# =============================================================================

class RolloutStrategy(Enum):
    """Feature flag rollout strategies"""
    OFF = "off"
    CANARY = "canary"
    GRADUAL = "gradual"
    FULL = "full"
    KILL_SWITCH = "kill_switch"

class UserSegment(Enum):
    """User segments for targeting"""
    INTERNAL = "internal"
    CANARY = "canary"
    BETA = "beta"
    PRODUCTION = "production"
    ALL = "all"

@dataclass
class RolloutConfig:
    """Rollout configuration for feature flags"""
    strategy: RolloutStrategy
    percentage: float  # 0-100
    user_segments: List[UserSegment]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    conditions: Optional[Dict[str, Any]] = None

@dataclass
class FeatureFlag:
    """Feature flag definition"""
    name: str
    description: str
    enabled: bool
    rollout: RolloutConfig
    owner: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    dependencies: List[str] = None
    kill_switch: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.rollout.start_time:
            data['rollout']['start_time'] = self.rollout.start_time.isoformat()
        if self.rollout.end_time:
            data['rollout']['end_time'] = self.rollout.end_time.isoformat()
        return data

@dataclass
class EvaluationContext:
    """Context for feature flag evaluation"""
    user_id: Optional[str] = None
    user_segment: UserSegment = UserSegment.PRODUCTION
    environment: str = "production"
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None

@dataclass
class EvaluationResult:
    """Result of feature flag evaluation"""
    flag_name: str
    enabled: bool
    reason: str
    user_segment: UserSegment
    rollout_percentage: float
    evaluation_time: datetime
    context: EvaluationContext

# =============================================================================
# FEATURE FLAG MANAGER
# =============================================================================

class FeatureFlagManager:
    """Manages feature flags with configuration-driven rollouts"""
    
    def __init__(self, config_path: str = "feature_flags/flags.json"):
        self.config_path = Path(config_path)
        self.flags: Dict[str, FeatureFlag] = {}
        self.lock = threading.RLock()
        self.logger = structlog.get_logger("feature_flag_manager")
        self._load_flags()
    
    def _load_flags(self):
        """Load feature flags from configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                for flag_data in config_data.get('flags', []):
                    flag = self._parse_flag(flag_data)
                    self.flags[flag.name] = flag
                
                self.logger.info(
                    "Feature flags loaded",
                    count=len(self.flags),
                    config_path=str(self.config_path)
                )
            else:
                self.logger.warning(
                    "Feature flags config not found, using defaults",
                    config_path=str(self.config_path)
                )
                self._create_default_flags()
        
        except Exception as e:
            self.logger.error(
                "Failed to load feature flags",
                error=str(e),
                config_path=str(self.config_path),
                exc_info=True
            )
            self._create_default_flags()
    
    def _parse_flag(self, flag_data: Dict[str, Any]) -> FeatureFlag:
        """Parse feature flag from configuration data"""
        rollout_data = flag_data.get('rollout', {})
        
        rollout = RolloutConfig(
            strategy=RolloutStrategy(rollout_data.get('strategy', 'off')),
            percentage=rollout_data.get('percentage', 0.0),
            user_segments=[
                UserSegment(seg) for seg in rollout_data.get('user_segments', ['production'])
            ],
            start_time=(
                datetime.fromisoformat(rollout_data['start_time'])
                if rollout_data.get('start_time') else None
            ),
            end_time=(
                datetime.fromisoformat(rollout_data['end_time'])
                if rollout_data.get('end_time') else None
            ),
            conditions=rollout_data.get('conditions')
        )
        
        return FeatureFlag(
            name=flag_data['name'],
            description=flag_data.get('description', ''),
            enabled=flag_data.get('enabled', False),
            rollout=rollout,
            owner=flag_data.get('owner', 'unknown'),
            created_at=datetime.fromisoformat(flag_data.get('created_at', datetime.now(timezone.utc).isoformat())),
            updated_at=datetime.fromisoformat(flag_data.get('updated_at', datetime.now(timezone.utc).isoformat())),
            tags=flag_data.get('tags', []),
            dependencies=flag_data.get('dependencies', []),
            kill_switch=flag_data.get('kill_switch', False)
        )
    
    def _create_default_flags(self):
        """Create default feature flags"""
        default_flags = [
            {
                "name": "compliance_report_generator",
                "description": "Compliance Report Generator feature slice",
                "enabled": True,
                "rollout": {
                    "strategy": "canary",
                    "percentage": 10.0,
                    "user_segments": ["canary", "internal"]
                },
                "owner": "platform@dogan",
                "tags": ["compliance", "reporting", "core"]
            },
            {
                "name": "compliance_report_generator_full",
                "description": "Full rollout of Compliance Report Generator",
                "enabled": False,
                "rollout": {
                    "strategy": "full",
                    "percentage": 100.0,
                    "user_segments": ["all"]
                },
                "owner": "platform@dogan",
                "tags": ["compliance", "reporting", "core"]
            },
            {
                "name": "advanced_analytics",
                "description": "Advanced analytics and insights",
                "enabled": False,
                "rollout": {
                    "strategy": "off",
                    "percentage": 0.0,
                    "user_segments": ["internal"]
                },
                "owner": "analytics@dogan",
                "tags": ["analytics", "insights"]
            },
            {
                "name": "real_time_monitoring",
                "description": "Real-time compliance monitoring",
                "enabled": False,
                "rollout": {
                    "strategy": "gradual",
                    "percentage": 5.0,
                    "user_segments": ["beta"]
                },
                "owner": "monitoring@dogan",
                "tags": ["monitoring", "real-time"]
            }
        ]
        
        for flag_data in default_flags:
            flag_data['created_at'] = datetime.now(timezone.utc).isoformat()
            flag_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            flag = self._parse_flag(flag_data)
            self.flags[flag.name] = flag
        
        # Save default flags
        self._save_flags()
    
    def _save_flags(self):
        """Save feature flags to configuration file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "flags": [flag.to_dict() for flag in self.flags.values()]
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(
                "Feature flags saved",
                count=len(self.flags),
                config_path=str(self.config_path)
            )
        
        except Exception as e:
            self.logger.error(
                "Failed to save feature flags",
                error=str(e),
                config_path=str(self.config_path),
                exc_info=True
            )
    
    def evaluate(self, flag_name: str, context: EvaluationContext) -> EvaluationResult:
        """Evaluate a feature flag"""
        with self.lock:
            evaluation_time = datetime.now(timezone.utc)
            
            # Check if flag exists
            if flag_name not in self.flags:
                result = EvaluationResult(
                    flag_name=flag_name,
                    enabled=False,
                    reason="flag_not_found",
                    user_segment=context.user_segment,
                    rollout_percentage=0.0,
                    evaluation_time=evaluation_time,
                    context=context
                )
                
                self.logger.warning(
                    "Feature flag not found",
                    flag_name=flag_name,
                    user_id=context.user_id,
                    user_segment=context.user_segment.value
                )
                
                # Track evaluation
                observability.feature_flag_monitor.track_evaluation(
                    flag_name=flag_name,
                    result=False,
                    user_segment=context.user_segment.value,
                    user_id=context.user_id
                )
                
                return result
            
            flag = self.flags[flag_name]
            
            # Check kill switch
            if flag.kill_switch:
                result = EvaluationResult(
                    flag_name=flag_name,
                    enabled=False,
                    reason="kill_switch_activated",
                    user_segment=context.user_segment,
                    rollout_percentage=0.0,
                    evaluation_time=evaluation_time,
                    context=context
                )
                
                self.logger.warning(
                    "Feature flag kill switch activated",
                    flag_name=flag_name,
                    user_id=context.user_id
                )
                
                observability.feature_flag_monitor.track_evaluation(
                    flag_name=flag_name,
                    result=False,
                    user_segment=context.user_segment.value,
                    user_id=context.user_id
                )
                
                return result
            
            # Check if flag is globally disabled
            if not flag.enabled:
                result = EvaluationResult(
                    flag_name=flag_name,
                    enabled=False,
                    reason="flag_disabled",
                    user_segment=context.user_segment,
                    rollout_percentage=0.0,
                    evaluation_time=evaluation_time,
                    context=context
                )
                
                observability.feature_flag_monitor.track_evaluation(
                    flag_name=flag_name,
                    result=False,
                    user_segment=context.user_segment.value,
                    user_id=context.user_id
                )
                
                return result
            
            # Check time-based conditions
            if flag.rollout.start_time and evaluation_time < flag.rollout.start_time:
                result = EvaluationResult(
                    flag_name=flag_name,
                    enabled=False,
                    reason="before_start_time",
                    user_segment=context.user_segment,
                    rollout_percentage=flag.rollout.percentage,
                    evaluation_time=evaluation_time,
                    context=context
                )
                
                observability.feature_flag_monitor.track_evaluation(
                    flag_name=flag_name,
                    result=False,
                    user_segment=context.user_segment.value,
                    user_id=context.user_id
                )
                
                return result
            
            if flag.rollout.end_time and evaluation_time > flag.rollout.end_time:
                result = EvaluationResult(
                    flag_name=flag_name,
                    enabled=False,
                    reason="after_end_time",
                    user_segment=context.user_segment,
                    rollout_percentage=flag.rollout.percentage,
                    evaluation_time=evaluation_time,
                    context=context
                )
                
                observability.feature_flag_monitor.track_evaluation(
                    flag_name=flag_name,
                    result=False,
                    user_segment=context.user_segment.value,
                    user_id=context.user_id
                )
                
                return result
            
            # Check user segment targeting
            if (context.user_segment not in flag.rollout.user_segments and 
                UserSegment.ALL not in flag.rollout.user_segments):
                result = EvaluationResult(
                    flag_name=flag_name,
                    enabled=False,
                    reason="user_segment_not_targeted",
                    user_segment=context.user_segment,
                    rollout_percentage=flag.rollout.percentage,
                    evaluation_time=evaluation_time,
                    context=context
                )
                
                observability.feature_flag_monitor.track_evaluation(
                    flag_name=flag_name,
                    result=False,
                    user_segment=context.user_segment.value,
                    user_id=context.user_id
                )
                
                return result
            
            # Evaluate rollout strategy
            enabled = self._evaluate_rollout_strategy(flag, context)
            reason = self._get_evaluation_reason(flag, context, enabled)
            
            result = EvaluationResult(
                flag_name=flag_name,
                enabled=enabled,
                reason=reason,
                user_segment=context.user_segment,
                rollout_percentage=flag.rollout.percentage,
                evaluation_time=evaluation_time,
                context=context
            )
            
            # Track evaluation
            observability.feature_flag_monitor.track_evaluation(
                flag_name=flag_name,
                result=enabled,
                user_segment=context.user_segment.value,
                user_id=context.user_id
            )
            
            self.logger.debug(
                "Feature flag evaluated",
                flag_name=flag_name,
                enabled=enabled,
                reason=reason,
                user_id=context.user_id,
                user_segment=context.user_segment.value,
                rollout_percentage=flag.rollout.percentage
            )
            
            return result
    
    def _evaluate_rollout_strategy(self, flag: FeatureFlag, context: EvaluationContext) -> bool:
        """Evaluate rollout strategy"""
        strategy = flag.rollout.strategy
        
        if strategy == RolloutStrategy.OFF:
            return False
        elif strategy == RolloutStrategy.FULL:
            return True
        elif strategy == RolloutStrategy.KILL_SWITCH:
            return False
        elif strategy in [RolloutStrategy.CANARY, RolloutStrategy.GRADUAL]:
            # Use consistent hashing for percentage-based rollout
            return self._is_user_in_rollout(context.user_id or "anonymous", flag.rollout.percentage)
        
        return False
    
    def _is_user_in_rollout(self, user_id: str, percentage: float) -> bool:
        """Determine if user is in rollout based on consistent hashing"""
        if percentage >= 100.0:
            return True
        if percentage <= 0.0:
            return False
        
        # Use consistent hashing to determine rollout
        hash_input = f"{user_id}:rollout"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_percentage = (hash_value % 10000) / 100.0  # 0-99.99
        
        return user_percentage < percentage
    
    def _get_evaluation_reason(self, flag: FeatureFlag, context: EvaluationContext, enabled: bool) -> str:
        """Get reason for evaluation result"""
        if not enabled:
            if flag.rollout.strategy == RolloutStrategy.OFF:
                return "rollout_strategy_off"
            elif flag.rollout.strategy in [RolloutStrategy.CANARY, RolloutStrategy.GRADUAL]:
                return "not_in_rollout_percentage"
            else:
                return "rollout_strategy_disabled"
        else:
            if flag.rollout.strategy == RolloutStrategy.FULL:
                return "rollout_strategy_full"
            elif flag.rollout.strategy in [RolloutStrategy.CANARY, RolloutStrategy.GRADUAL]:
                return "in_rollout_percentage"
            else:
                return "rollout_strategy_enabled"
    
    def is_enabled(self, flag_name: str, context: EvaluationContext) -> bool:
        """Simple check if feature flag is enabled"""
        result = self.evaluate(flag_name, context)
        return result.enabled
    
    def update_flag(self, flag_name: str, updates: Dict[str, Any]) -> bool:
        """Update a feature flag"""
        with self.lock:
            if flag_name not in self.flags:
                self.logger.error(
                    "Cannot update non-existent flag",
                    flag_name=flag_name
                )
                return False
            
            flag = self.flags[flag_name]
            old_values = flag.to_dict()
            
            # Update flag properties
            if 'enabled' in updates:
                flag.enabled = updates['enabled']
            
            if 'rollout' in updates:
                rollout_updates = updates['rollout']
                if 'strategy' in rollout_updates:
                    flag.rollout.strategy = RolloutStrategy(rollout_updates['strategy'])
                if 'percentage' in rollout_updates:
                    flag.rollout.percentage = rollout_updates['percentage']
                if 'user_segments' in rollout_updates:
                    flag.rollout.user_segments = [
                        UserSegment(seg) for seg in rollout_updates['user_segments']
                    ]
            
            if 'kill_switch' in updates:
                flag.kill_switch = updates['kill_switch']
            
            flag.updated_at = datetime.now(timezone.utc)
            
            # Save changes
            self._save_flags()
            
            # Log audit event
            observability.audit_logger.log_event(
                event_type="feature_flag_updated",
                user="system",
                resource=flag_name,
                action="update",
                details={
                    "old_values": old_values,
                    "new_values": flag.to_dict(),
                    "updates": updates
                }
            )
            
            self.logger.info(
                "Feature flag updated",
                flag_name=flag_name,
                updates=updates
            )
            
            return True
    
    def create_flag(self, flag_data: Dict[str, Any]) -> bool:
        """Create a new feature flag"""
        with self.lock:
            flag_name = flag_data.get('name')
            if not flag_name:
                self.logger.error("Flag name is required")
                return False
            
            if flag_name in self.flags:
                self.logger.error(
                    "Flag already exists",
                    flag_name=flag_name
                )
                return False
            
            # Set timestamps
            now = datetime.now(timezone.utc)
            flag_data['created_at'] = now.isoformat()
            flag_data['updated_at'] = now.isoformat()
            
            # Create flag
            flag = self._parse_flag(flag_data)
            self.flags[flag_name] = flag
            
            # Save changes
            self._save_flags()
            
            # Log audit event
            observability.audit_logger.log_event(
                event_type="feature_flag_created",
                user="system",
                resource=flag_name,
                action="create",
                details=flag.to_dict()
            )
            
            self.logger.info(
                "Feature flag created",
                flag_name=flag_name,
                flag_data=flag.to_dict()
            )
            
            return True
    
    def delete_flag(self, flag_name: str) -> bool:
        """Delete a feature flag"""
        with self.lock:
            if flag_name not in self.flags:
                self.logger.error(
                    "Cannot delete non-existent flag",
                    flag_name=flag_name
                )
                return False
            
            flag_data = self.flags[flag_name].to_dict()
            del self.flags[flag_name]
            
            # Save changes
            self._save_flags()
            
            # Log audit event
            observability.audit_logger.log_event(
                event_type="feature_flag_deleted",
                user="system",
                resource=flag_name,
                action="delete",
                details=flag_data
            )
            
            self.logger.info(
                "Feature flag deleted",
                flag_name=flag_name
            )
            
            return True
    
    def list_flags(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List all feature flags"""
        with self.lock:
            flags = []
            for flag in self.flags.values():
                if tags is None or any(tag in flag.tags for tag in tags):
                    flags.append(flag.to_dict())
            return flags
    
    def get_flag_status(self) -> Dict[str, Any]:
        """Get overall feature flag status"""
        with self.lock:
            total_flags = len(self.flags)
            enabled_flags = sum(1 for flag in self.flags.values() if flag.enabled)
            canary_flags = sum(
                1 for flag in self.flags.values() 
                if flag.rollout.strategy == RolloutStrategy.CANARY
            )
            full_flags = sum(
                1 for flag in self.flags.values() 
                if flag.rollout.strategy == RolloutStrategy.FULL
            )
            
            return {
                "total_flags": total_flags,
                "enabled_flags": enabled_flags,
                "disabled_flags": total_flags - enabled_flags,
                "canary_flags": canary_flags,
                "full_flags": full_flags,
                "config_path": str(self.config_path),
                "last_updated": max(
                    (flag.updated_at for flag in self.flags.values()),
                    default=datetime.now(timezone.utc)
                ).isoformat()
            }
    
    def reload_flags(self):
        """Reload feature flags from configuration"""
        with self.lock:
            self.logger.info("Reloading feature flags")
            self._load_flags()

# =============================================================================
# FEATURE FLAG DECORATORS
# =============================================================================

def feature_flag(flag_name: str, default: bool = False):
    """Decorator to enable/disable features based on feature flags"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract context from kwargs or create default
            context = kwargs.pop('feature_flag_context', EvaluationContext())
            
            # Evaluate feature flag
            if flag_manager.is_enabled(flag_name, context):
                return func(*args, **kwargs)
            else:
                if default:
                    # Return default behavior
                    return None
                else:
                    # Raise exception or return error
                    raise ValueError(f"Feature '{flag_name}' is not enabled")
        
        return wrapper
    return decorator

def require_feature_flag(flag_name: str):
    """Decorator that requires a feature flag to be enabled"""
    return feature_flag(flag_name, default=False)

def optional_feature_flag(flag_name: str):
    """Decorator that gracefully handles disabled features"""
    return feature_flag(flag_name, default=True)

# =============================================================================
# GLOBAL FEATURE FLAG MANAGER
# =============================================================================

# Global feature flag manager instance
flag_manager = FeatureFlagManager()

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example usage
    
    # Create evaluation context
    context = EvaluationContext(
        user_id="user123",
        user_segment=UserSegment.CANARY,
        environment="staging"
    )
    
    # Evaluate feature flag
    result = flag_manager.evaluate("compliance_report_generator", context)
    print(f"Feature enabled: {result.enabled}, Reason: {result.reason}")
    
    # Update flag for full rollout
    flag_manager.update_flag("compliance_report_generator", {
        "rollout": {
            "strategy": "full",
            "percentage": 100.0,
            "user_segments": ["all"]
        }
    })
    
    # Check status
    status = flag_manager.get_flag_status()
    print(f"Flag status: {status}")
    
    # Example decorator usage
    @require_feature_flag("compliance_report_generator")
    def generate_compliance_report():
        return "Report generated!"
    
    try:
        report = generate_compliance_report()
        print(report)
    except ValueError as e:
        print(f"Feature not available: {e}")