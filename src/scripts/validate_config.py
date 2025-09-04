#!/usr/bin/env python3
"""
Configuration validation script for DoganAI-Compliance-Kit
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.settings import settings
from engine.compliance import get_available_mappings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_directories():
    """Validate that required directories exist"""
    errors = []
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        "mappings",
        "policies", 
        "vendors",
        "benchmarks",
        "i18n"
    ]
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            errors.append(f"Required directory missing: {dir_path}")
        elif not dir_path.is_dir():
            errors.append(f"Path exists but is not a directory: {dir_path}")
    
    return errors

def validate_files():
    """Validate that required files exist"""
    errors = []
    base_dir = Path(__file__).parent.parent
    
    required_files = [
        ".env.example",
        "requirements.txt",
        "requirements-dev.txt"
    ]
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if not file_path.exists():
            errors.append(f"Required file missing: {file_path}")
        elif not file_path.is_file():
            errors.append(f"Path exists but is not a file: {file_path}")
    
    return errors

def validate_mappings():
    """Validate mapping files"""
    errors = []
    mappings = get_available_mappings()
    
    if not mappings:
        errors.append("No mapping files found")
    else:
        logger.info(f"Found {len(mappings)} mapping files: {', '.join(mappings)}")
    
    return errors

def validate_environment():
    """Validate environment configuration"""
    errors = []
    
    # Check critical settings
    if not settings.app_name:
        errors.append("APP_NAME is empty")
    
    if not settings.cors_origins:
        errors.append("CORS_ORIGINS not configured")
    
    # Validate port ranges
    if not (1 <= settings.api_port <= 65535):
        errors.append(f"Invalid API port: {settings.api_port}")
    
    if not (1 <= settings.pg_port <= 65535):
        errors.append(f"Invalid PostgreSQL port: {settings.pg_port}")
    
    return errors

def main():
    """Main validation function"""
    logger.info("Starting configuration validation...")
    
    all_errors = []
    
    # Run all validations
    validations = [
        ("Directory structure", validate_directories),
        ("Required files", validate_files),
        ("Mapping files", validate_mappings),
        ("Environment configuration", validate_environment),
    ]
    
    for name, validation_func in validations:
        logger.info(f"Validating {name.lower()}...")
        errors = validation_func()
        if errors:
            logger.error(f"{name} validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            all_errors.extend(errors)
        else:
            logger.info(f"{name} validation passed ?")
    
    # Summary
    if all_errors:
        logger.error(f"\nValidation failed with {len(all_errors)} error(s):")
        for error in all_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    else:
        logger.info("\n? All validations passed! Configuration is valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()