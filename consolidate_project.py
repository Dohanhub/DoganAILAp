#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Project Consolidation Script
Merges duplicate directories and creates unified structure
"""

import os
import shutil
import sys
import logging
from pathlib import Path
from typing import List, Dict, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectConsolidator:
    """Handles consolidation of duplicate project directories"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / "backup_before_consolidation"
        self.src_dir = project_root / "src"
        self.platform_dir = project_root / "platform"
        self.microservices_dir = project_root / "microservices"
        
        # Files to merge/resolve conflicts
        self.conflicts_resolved = []
        self.files_moved = []
        self.directories_removed = []
    
    def analyze_structure(self) -> Dict[str, List[Path]]:
        """Analyze current project structure and identify duplicates"""
        logger.info("Analyzing project structure...")
        
        structure = {
            "duplicates": [],
            "src_files": [],
            "platform_files": [], 
            "microservices_files": [],
            "conflicts": []
        }
        
        # Find all Python files in different directories
        if self.src_dir.exists():
            structure["src_files"] = list(self.src_dir.rglob("*.py"))
        
        if self.platform_dir.exists():
            structure["platform_files"] = list(self.platform_dir.rglob("*.py"))
            
        if self.microservices_dir.exists():
            structure["microservices_files"] = list(self.microservices_dir.rglob("*.py"))
        
        # Identify potential conflicts
        src_names = {f.name for f in structure["src_files"]}
        platform_names = {f.name for f in structure["platform_files"]}
        microservices_names = {f.name for f in structure["microservices_files"]}
        
        conflicts = src_names & platform_names & microservices_names
        structure["conflicts"] = list(conflicts)
        
        logger.info(f"Found {len(structure['src_files'])} files in src/")
        logger.info(f"Found {len(structure['platform_files'])} files in platform/")
        logger.info(f"Found {len(structure['microservices_files'])} files in microservices/")
        logger.info(f"Potential conflicts: {len(conflicts)}")
        
        return structure
    
    def create_backup(self):
        """Create backup of current state"""
        logger.info("Creating backup of current project state...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup main directories
        for dir_name in ["src", "platform", "microservices", "app"]:
            source_dir = self.project_root / dir_name
            if source_dir.exists():
                backup_target = self.backup_dir / dir_name
                shutil.copytree(source_dir, backup_target)
                logger.info(f"Backed up {dir_name}/ to backup/")
        
        # Backup important files
        for file_name in ["main.py", "main_unified.py", "app.py"]:
            source_file = self.project_root / file_name
            if source_file.exists():
                shutil.copy2(source_file, self.backup_dir / file_name)
                logger.info(f"Backed up {file_name}")
    
    def consolidate_microservices(self):
        """Consolidate microservices directories"""
        logger.info("Consolidating microservices...")
        
        target_services_dir = self.src_dir / "services"
        target_services_dir.mkdir(exist_ok=True)
        
        # List of microservices to consolidate
        microservice_dirs = [
            self.platform_dir / "microservices",
            self.microservices_dir,
            self.project_root / "src" / "api" / "microservices"
        ]
        
        for ms_root in microservice_dirs:
            if not ms_root.exists():
                continue
                
            for service_dir in ms_root.iterdir():
                if not service_dir.is_dir():
                    continue
                    
                service_name = service_dir.name
                target_service = target_services_dir / f"{service_name}_service.py"
                
                # Find main Python file in service
                main_files = list(service_dir.glob("*.py"))
                if main_files:
                    # Take the largest/most recent file
                    main_file = max(main_files, key=lambda f: f.stat().st_size)
                    
                    if not target_service.exists():
                        shutil.copy2(main_file, target_service)
                        logger.info(f"Consolidated {service_name} service")
                        self.files_moved.append(f"{main_file} -> {target_service}")
    
    def merge_core_modules(self):
        """Merge core modules from platform/ into src/core/"""
        logger.info("Merging core modules...")
        
        platform_src = self.platform_dir / "src"
        if not platform_src.exists():
            return
        
        # Merge core modules
        platform_core = platform_src / "core"
        if platform_core.exists():
            target_core = self.src_dir / "core"
            target_core.mkdir(exist_ok=True)
            
            for core_file in platform_core.glob("*.py"):
                target_file = target_core / core_file.name
                
                if target_file.exists():
                    # Merge files if they exist in both locations
                    self._merge_python_files(core_file, target_file)
                else:
                    shutil.copy2(core_file, target_file)
                    logger.info(f"Moved {core_file.name} to src/core/")
                    self.files_moved.append(f"{core_file} -> {target_file}")
    
    def _merge_python_files(self, source: Path, target: Path):
        """Merge two Python files, combining the best from both"""
        logger.info(f"Merging {source.name} files...")
        
        try:
            with open(source, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            with open(target, 'r', encoding='utf-8') as f:
                target_content = f.read()
            
            # Simple merge strategy: if source is larger and newer, use it
            if len(source_content) > len(target_content):
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(source_content)
                logger.info(f"Updated {target.name} with content from {source}")
                self.conflicts_resolved.append(f"{source} -> {target}")
            
        except Exception as e:
            logger.error(f"Failed to merge {source} and {target}: {e}")
    
    def fix_merge_conflicts(self):
        """Fix Git merge conflicts in configuration files"""
        logger.info("Fixing merge conflicts...")
        
        conflict_files = [
            self.src_dir / "deploy" / "k8s" / "configmaps.yaml",
            self.src_dir / "deploy" / "k8s" / "secrets.yaml"
        ]
        
        for conflict_file in conflict_files:
            if not conflict_file.exists():
                continue
                
            try:
                with open(conflict_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove Git conflict markers
                if "<<<<<<< HEAD" in content:
                    logger.info(f"Fixing merge conflicts in {conflict_file.name}")
                    
                    # Simple resolution: take the first version (before =======)
                    lines = content.split('\n')
                    clean_lines = []
                    skip_mode = False
                    
                    for line in lines:
                        if line.startswith('<<<<<<< HEAD'):
                            skip_mode = False
                            continue
                        elif line.startswith('======='):
                            skip_mode = True
                            continue
                        elif line.startswith('>>>>>>> '):
                            skip_mode = False
                            continue
                        
                        if not skip_mode:
                            clean_lines.append(line)
                    
                    with open(conflict_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(clean_lines))
                    
                    self.conflicts_resolved.append(str(conflict_file))
                    
            except Exception as e:
                logger.error(f"Failed to fix conflicts in {conflict_file}: {e}")
    
    def cleanup_duplicates(self):
        """Remove duplicate directories after consolidation"""
        logger.info("Cleaning up duplicate directories...")
        
        dirs_to_remove = []
        
        # Remove platform directory after consolidation
        if self.platform_dir.exists():
            dirs_to_remove.append(self.platform_dir)
        
        # Remove standalone microservices directory
        if self.microservices_dir.exists():
            dirs_to_remove.append(self.microservices_dir)
        
        for dir_path in dirs_to_remove:
            try:
                shutil.rmtree(dir_path)
                logger.info(f"Removed duplicate directory: {dir_path}")
                self.directories_removed.append(str(dir_path))
            except Exception as e:
                logger.error(f"Failed to remove {dir_path}: {e}")
    
    def update_imports(self):
        """Update import statements to use new consolidated structure"""
        logger.info("Updating import statements...")
        
        # Find all Python files in src/
        python_files = list(self.src_dir.rglob("*.py"))
        
        import_mappings = {
            "from platform.": "from src.",
            "import platform.": "import src.",
            "from microservices.": "from src.services.",
            "import microservices.": "import src.services.",
        }
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                for old_import, new_import in import_mappings.items():
                    content = content.replace(old_import, new_import)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Updated imports in {py_file.name}")
                    
            except Exception as e:
                logger.error(f"Failed to update imports in {py_file}: {e}")
    
    def generate_report(self):
        """Generate consolidation report"""
        logger.info("Generating consolidation report...")
        
        report_file = self.project_root / "CONSOLIDATION_REPORT.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# DoganAI Compliance Kit - Consolidation Report\n\n")
            f.write(f"Generated on: {__import__('datetime').datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Files moved: {len(self.files_moved)}\n")
            f.write(f"- Conflicts resolved: {len(self.conflicts_resolved)}\n")
            f.write(f"- Directories removed: {len(self.directories_removed)}\n\n")
            
            f.write("## Files Moved\n\n")
            for move in self.files_moved:
                f.write(f"- {move}\n")
            
            f.write("\n## Conflicts Resolved\n\n")
            for conflict in self.conflicts_resolved:
                f.write(f"- {conflict}\n")
            
            f.write("\n## Directories Removed\n\n")
            for directory in self.directories_removed:
                f.write(f"- {directory}\n")
            
            f.write("\n## Next Steps\n\n")
            f.write("1. Review the consolidated code structure\n")
            f.write("2. Test the unified application: `python main_unified.py`\n")
            f.write("3. Update any remaining import statements\n")
            f.write("4. Run tests to ensure everything works\n")
            f.write("5. Update documentation\n\n")
            
            f.write("## Rollback\n\n")
            f.write("If issues occur, restore from backup:\n")
            f.write(f"```bash\ncp -r {self.backup_dir}/* .\n```\n")
        
        logger.info(f"Consolidation report saved to {report_file}")
    
    def run_consolidation(self):
        """Run the complete consolidation process"""
        logger.info("Starting project consolidation...")
        
        try:
            # 1. Analyze current structure
            structure = self.analyze_structure()
            
            # 2. Create backup
            self.create_backup()
            
            # 3. Ensure src directory exists
            self.src_dir.mkdir(exist_ok=True)
            
            # 4. Consolidate microservices
            self.consolidate_microservices()
            
            # 5. Merge core modules
            self.merge_core_modules()
            
            # 6. Fix merge conflicts
            self.fix_merge_conflicts()
            
            # 7. Update import statements
            self.update_imports()
            
            # 8. Clean up duplicates
            self.cleanup_duplicates()
            
            # 9. Generate report
            self.generate_report()
            
            logger.info("Project consolidation completed successfully!")
            logger.info(f"Backup created at: {self.backup_dir}")
            logger.info("Run 'python main_unified.py' to test the unified application")
            
        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            raise

def main():
    """Main entry point"""
    project_root = Path(__file__).parent
    consolidator = ProjectConsolidator(project_root)
    
    # Confirm before proceeding
    print("DoganAI Compliance Kit - Project Consolidation")
    print("=" * 50)
    print("This script will:")
    print("1. Create a backup of the current project")
    print("2. Merge duplicate directories (platform/, microservices/)")
    print("3. Fix merge conflicts in configuration files")
    print("4. Update import statements")
    print("5. Clean up duplicate code")
    print()
    
    response = input("Do you want to proceed? (y/N): ")
    if response.lower() != 'y':
        print("Consolidation cancelled.")
        return
    
    try:
        consolidator.run_consolidation()
        print("\n? Consolidation completed successfully!")
        print(f"?? Backup available at: {consolidator.backup_dir}")
        print("?? Check CONSOLIDATION_REPORT.md for details")
        print("?? Test with: python main_unified.py")
        
    except Exception as e:
        print(f"\n? Consolidation failed: {e}")
        print(f"?? Backup available at: {consolidator.backup_dir}")
        sys.exit(1)

if __name__ == "__main__":
    main()