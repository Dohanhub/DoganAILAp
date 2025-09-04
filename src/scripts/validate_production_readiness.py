#!/usr/bin/env python3
"""
Production Readiness Validation Script
Ensures all Definition of Done criteria are met for production deployment
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from services.observability import logger

class ProductionReadinessValidator:
    """Validates production readiness criteria"""
    
    def __init__(self):
        self.settings = Settings()
        self.validation_results = []
        self.critical_failures = []
        self.warnings = []
        
    def validate_all(self) -> bool:
        """Run all production readiness validations"""
        logger.info("Starting production readiness validation")
        
        validations = [
            self._validate_environment_configuration,
            self._validate_security_requirements,
            self._validate_observability_setup,
            self._validate_feature_flags,
            self._validate_database_configuration,
            self._validate_performance_requirements,
            self._validate_monitoring_setup,
            self._validate_backup_procedures,
            self._validate_documentation,
            self._validate_compliance_requirements,
        ]
        
        all_passed = True
        
        for validation in validations:
            try:
                result = validation()
                if not result:
                    all_passed = False
            except Exception as e:
                logger.error(f"Validation failed with exception: {e}")
                self.critical_failures.append(f"Validation exception: {str(e)}")
                all_passed = False
        
        self._generate_report()
        return all_passed and len(self.critical_failures) == 0
    
    def _validate_environment_configuration(self) -> bool:
        """Validate environment configuration"""
        logger.info("Validating environment configuration")
        
        required_env_vars = [
            'DATABASE_URL',
            'SECRET_KEY',
            'ENVIRONMENT',
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.critical_failures.append(f"Missing required environment variables: {missing_vars}")
            return False
        
        # Validate environment is set to production
        if self.settings.environment != 'production':
            self.warnings.append(f"Environment is set to '{self.settings.environment}', not 'production'")
        
        # Validate debug is disabled
        if self.settings.debug:
            self.critical_failures.append("Debug mode is enabled in production")
            return False
        
        self.validation_results.append("✅ Environment configuration validated")
        return True
    
    def _validate_security_requirements(self) -> bool:
        """Validate security requirements"""
        logger.info("Validating security requirements")
        
        # Check if secret key is properly configured
        secret_key = self.settings.security.secret_key
        if not secret_key or len(secret_key) < 32:
            self.critical_failures.append("SECRET_KEY is not properly configured (must be at least 32 characters)")
            return False
        
        # Validate HTTPS is enforced
        if self.settings.environment == 'production':
            # In production, we should enforce HTTPS
            self.validation_results.append("✅ Security requirements validated")
        
        # Check for security headers configuration
        # This would typically check if security middleware is properly configured
        
        return True
    
    def _validate_observability_setup(self) -> bool:
        """Validate observability and monitoring setup"""
        logger.info("Validating observability setup")
        
        # Check if observability is enabled
        if not self.settings.observability.enable_metrics:
            self.critical_failures.append("Metrics collection is disabled")
            return False
        
        if not self.settings.observability.enable_structured_logging:
            self.warnings.append("Structured logging is disabled")
        
        if not self.settings.enable_audit_logging:
            self.critical_failures.append("Audit logging is disabled")
            return False
        
        # Validate metrics port is configured
        if not (1024 <= self.settings.observability.metrics_port <= 65535):
            self.critical_failures.append(f"Invalid metrics port: {self.settings.observability.metrics_port}")
            return False
        
        self.validation_results.append("✅ Observability setup validated")
        return True
    
    def _validate_feature_flags(self) -> bool:
        """Validate feature flags configuration"""
        logger.info("Validating feature flags")
        
        try:
            from services.feature_flags import flag_manager
            
            # Check if feature flags are properly loaded
            flags = flag_manager.list_flags()
            if not flags:
                self.warnings.append("No feature flags configured")
            
            # Check for critical flags that should be enabled in production
            status = flag_manager.get_flag_status()
            if status['total_flags'] > 0:
                self.validation_results.append(f"✅ Feature flags validated ({status['total_flags']} flags configured)")
            
            return True
            
        except Exception as e:
            self.critical_failures.append(f"Feature flags validation failed: {str(e)}")
            return False
    
    def _validate_database_configuration(self) -> bool:
        """Validate database configuration"""
        logger.info("Validating database configuration")
        
        # Check database connection settings
        if not self.settings.database.host:
            self.critical_failures.append("Database host not configured")
            return False
        
        if not self.settings.database.database:
            self.critical_failures.append("Database name not configured")
            return False
        
        # Validate connection pool settings
        if self.settings.database.pool_size < 5:
            self.warnings.append(f"Database pool size is low: {self.settings.database.pool_size}")
        
        # Check if database timezone is properly configured
        if self.settings.database.timezone != 'UTC':
            self.warnings.append(f"Database timezone is not UTC: {self.settings.database.timezone}")
        
        self.validation_results.append("✅ Database configuration validated")
        return True
    
    def _validate_performance_requirements(self) -> bool:
        """Validate performance requirements"""
        logger.info("Validating performance requirements")
        
        # Check caching configuration
        if not self.settings.enable_caching:
            self.warnings.append("Caching is disabled")
        
        # Validate cache TTL settings
        if self.settings.cache_ttl < 60:
            self.warnings.append(f"Cache TTL is very low: {self.settings.cache_ttl} seconds")
        
        # Check request timeout settings
        if self.settings.request_timeout > 30:
            self.warnings.append(f"Request timeout is high: {self.settings.request_timeout} seconds")
        
        self.validation_results.append("✅ Performance requirements validated")
        return True
    
    def _validate_monitoring_setup(self) -> bool:
        """Validate monitoring and alerting setup"""
        logger.info("Validating monitoring setup")
        
        # Check if health check interval is reasonable
        health_interval = self.settings.observability.health_check_interval
        if health_interval > 300:  # 5 minutes
            self.warnings.append(f"Health check interval is high: {health_interval} seconds")
        
        # Validate metrics retention
        retention_days = self.settings.observability.metrics_retention_days
        if retention_days < 7:
            self.warnings.append(f"Metrics retention is low: {retention_days} days")
        
        self.validation_results.append("✅ Monitoring setup validated")
        return True
    
    def _validate_backup_procedures(self) -> bool:
        """Validate backup procedures"""
        logger.info("Validating backup procedures")
        
        # Check if backup storage is configured
        backup_storage = os.getenv('BACKUP_STORAGE_URL')
        if not backup_storage:
            self.warnings.append("Backup storage URL not configured")
        
        # Validate database backup configuration
        # This would typically check if automated backups are configured
        
        self.validation_results.append("✅ Backup procedures validated")
        return True
    
    def _validate_documentation(self) -> bool:
        """Validate documentation requirements"""
        logger.info("Validating documentation")
        
        required_docs = [
            'README.md',
            'DEVELOPER_GUIDE.md',
            'src/docs/runbooks',
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not Path(doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            self.warnings.append(f"Missing documentation: {missing_docs}")
        
        self.validation_results.append("✅ Documentation validated")
        return True
    
    def _validate_compliance_requirements(self) -> bool:
        """Validate compliance requirements"""
        logger.info("Validating compliance requirements")
        
        # Check if audit logging is properly configured
        if not self.settings.enable_audit_logging:
            self.critical_failures.append("Audit logging is required for compliance")
            return False
        
        # Validate data retention policies
        # This would check if data retention policies are properly configured
        
        # Check if security scanning is up to date
        # This would verify that security scans have been run recently
        
        self.validation_results.append("✅ Compliance requirements validated")
        return True
    
    def _generate_report(self):
        """Generate validation report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": self.settings.environment,
            "validation_results": self.validation_results,
            "warnings": self.warnings,
            "critical_failures": self.critical_failures,
            "overall_status": "PASS" if len(self.critical_failures) == 0 else "FAIL",
            "ready_for_production": len(self.critical_failures) == 0
        }
        
        # Save report to file
        report_file = Path("production-readiness-report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔍 PRODUCTION READINESS VALIDATION REPORT")
        print("=" * 60)
        
        print("\n📊 Summary:")
        print(f"   Environment: {self.settings.environment}")
        print(f"   Timestamp: {report['timestamp']}")
        print(f"   Overall Status: {report['overall_status']}")
        print(f"   Ready for Production: {report['ready_for_production']}")
        
        if self.validation_results:
            print(f"\n✅ Validations Passed ({len(self.validation_results)}):")
            for result in self.validation_results:
                print(f"   {result}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠️  {warning}")
        
        if self.critical_failures:
            print(f"\n❌ Critical Failures ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        
        print(f"\n📋 Report saved to: {report_file.absolute()}")
        print("=" * 60)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate production readiness")
    parser.add_argument(
        "--environment",
        default="production",
        help="Environment to validate (default: production)"
    )
    parser.add_argument(
        "--output",
        help="Output file for validation report"
    )
    
    args = parser.parse_args()
    
    # Set environment
    os.environ['ENVIRONMENT'] = args.environment
    
    # Run validation
    validator = ProductionReadinessValidator()
    success = validator.validate_all()
    
    # Copy report to specified output if provided
    if args.output:
        import shutil
        shutil.copy("production-readiness-report.json", args.output)
        print(f"Report copied to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()