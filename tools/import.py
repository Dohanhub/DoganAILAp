"""
Data Import Module for DoganAI Compliance Kit

This module provides functionality to import compliance data from various sources
including JSON, YAML, and database dumps into the compliance platform.
"""
import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataImporter:
    """
    Handles importing of compliance data from various sources into the system.
    """
    
    SUPPORTED_FORMATS = ['.json', '.yaml', '.yml']
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the data importer with optional configuration."""
        self.config = config or {}
        self.import_stats = {
            'total_files': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'start_time': None,
            'end_time': None
        }
    
    def import_file(self, file_path: Union[str, Path]) -> bool:
        """
        Import data from a single file.
        
        Args:
            file_path: Path to the file to import
            
        Returns:
            bool: True if import was successful, False otherwise
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
            
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported file format: {file_path.suffix}")
            return False
            
        try:
            # Read file based on extension
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:  # .yaml or .yml
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            
            # Process the data based on its type/structure
            return self._process_import_data(data, file_path)
            
        except Exception as e:
            logger.error(f"Error importing {file_path}: {str(e)}", exc_info=True)
            self.import_stats['failed_imports'] += 1
            return False
    
    def import_directory(self, dir_path: Union[str, Path]) -> Dict[str, int]:
        """
        Import all supported files from a directory recursively.
        
        Args:
            dir_path: Path to the directory to import from
            
        Returns:
            Dict with import statistics
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            logger.error(f"Directory not found: {dir_path}")
            return self.import_stats
            
        self.import_stats['start_time'] = datetime.utcnow().isoformat()
        
        # Walk through directory and import all supported files
        for root, _, files in os.walk(dir_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in self.SUPPORTED_FORMATS):
                    file_path = Path(root) / file
                    self.import_stats['total_files'] += 1
                    if self.import_file(file_path):
                        self.import_stats['successful_imports'] += 1
                    else:
                        self.import_stats['failed_imports'] += 1
        
        self.import_stats['end_time'] = datetime.utcnow().isoformat()
        return self.import_stats
    
    def _process_import_data(self, data: Any, source_path: Path) -> bool:
        """
        Process imported data based on its structure and type.
        
        Args:
            data: The parsed data to process
            source_path: Path to the source file
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Determine data type and process accordingly
            if isinstance(data, dict):
                if 'type' in data:
                    # Handle based on data type
                    if data['type'] == 'policy':
                        return self._import_policy(data, source_path)
                    elif data['type'] == 'vendor':
                        return self._import_vendor(data, source_path)
                    elif data['type'] == 'mapping':
                        return self._import_mapping(data, source_path)
            
            # Default processing for arrays or unknown formats
            if isinstance(data, list):
                success = True
                for item in data:
                    if not self._process_import_data(item, source_path):
                        success = False
                return success
                
            logger.warning(f"Unrecognized data format in {source_path}")
            return False
            
        except Exception as e:
            logger.error(f"Error processing {source_path}: {str(e)}", exc_info=True)
            return False
    
    def _import_policy(self, policy_data: Dict[str, Any], source_path: Path) -> bool:
        """Import a policy document."""
        # TODO: Implement actual policy import logic
        logger.info(f"Importing policy: {policy_data.get('name', 'Unnamed')} from {source_path}")
        return True
    
    def _import_vendor(self, vendor_data: Dict[str, Any], source_path: Path) -> bool:
        """Import vendor information."""
        # TODO: Implement actual vendor import logic
        logger.info(f"Importing vendor: {vendor_data.get('name', 'Unnamed')} from {source_path}")
        return True
    
    def _import_mapping(self, mapping_data: Dict[str, Any], source_path: Path) -> bool:
        """Import a compliance mapping."""
        # TODO: Implement actual mapping import logic
        logger.info(f"Importing mapping: {mapping_data.get('name', 'Unnamed')} from {source_path}")
        return True

def main():
    """Command-line interface for the data importer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import compliance data into DoganAI Compliance Kit')
    parser.add_argument('source', help='File or directory to import')
    parser.add_argument('--format', choices=['auto', 'json', 'yaml'], default='auto',
                       help='Input format (default: auto-detect from file extension)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    importer = DataImporter()
    source_path = Path(args.source)
    
    if source_path.is_file():
        print(f"Importing file: {source_path}")
        success = importer.import_file(source_path)
        print(f"Import {'succeeded' if success else 'failed'}")
    elif source_path.is_dir():
        print(f"Importing from directory: {source_path}")
        stats = importer.import_directory(source_path)
        print("\nImport completed with the following statistics:")
        print(f"- Total files processed: {stats['total_files']}")
        print(f"- Successful imports: {stats['successful_imports']}")
        print(f"- Failed imports: {stats['failed_imports']}")
        print(f"- Duration: {stats['end_time']} - {stats['start_time']}")
    else:
        print(f"Error: Source not found: {source_path}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
