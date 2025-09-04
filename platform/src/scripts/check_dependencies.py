#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Layer Dependency Checker
Checks for circular dependencies and validates layer architecture compliance.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Define layer hierarchy (lower layers cannot import from higher layers)
LAYER_HIERARCHY = {
    'src/utils/': 0,      # Lowest layer - utilities
    'src/models/': 1,     # Data models
    'src/core/': 2,       # Core business logic
    'src/services/': 3,   # Business services
    'src/api/': 4         # Highest layer - API endpoints
}

# Define allowed dependencies between layers
ALLOWED_DEPENDENCIES = {
    'src/api/': ['src/core/', 'src/models/', 'src/services/', 'src/utils/'],
    'src/services/': ['src/core/', 'src/models/', 'src/utils/'],
    'src/core/': ['src/models/', 'src/utils/'],
    'src/models/': ['src/utils/'],
    'src/utils/': []  # Utils should be self-contained
}

class DependencyChecker:
    """Checks layer dependencies and circular imports"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.file_to_layer: Dict[str, str] = {}
        
    def check_files(self, file_paths: List[str]) -> bool:
        """Check dependencies for a list of files"""
        # First pass: build dependency graph
        for file_path in file_paths:
            self._analyze_file_dependencies(file_path)
            
        # Second pass: validate dependencies
        all_valid = True
        
        for file_path in file_paths:
            if not self._validate_file_dependencies(file_path):
                all_valid = False
                
        # Check for circular dependencies
        if not self._check_circular_dependencies():
            all_valid = False
            
        return all_valid
        
    def _analyze_file_dependencies(self, file_path: str):
        """Analyze dependencies for a single file"""
        path = Path(file_path)
        
        # Skip non-Python files or files outside src/
        if not file_path.endswith('.py') or not str(path).startswith('src/'):
            return
            
        # Determine layer for this file
        layer = self._get_file_layer(file_path)
        if layer:
            self.file_to_layer[file_path] = layer
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            return
            
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return
            
        # Extract internal imports
        imports = self._extract_internal_imports(tree)
        
        for imported_module in imports:
            # Convert module path to file path
            imported_file = self._module_to_file_path(imported_module)
            if imported_file:
                self.dependencies[file_path].add(imported_file)
                
    def _get_file_layer(self, file_path: str) -> str:
        """Determine which layer a file belongs to"""
        path_str = str(Path(file_path))
        
        for layer in LAYER_HIERARCHY.keys():
            if path_str.startswith(layer):
                return layer
                
        return ''
        
    def _extract_internal_imports(self, tree: ast.AST) -> List[str]:
        """Extract internal project imports from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('src.'):
                        imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('src.'):
                    imports.append(node.module)
                    
        return imports
        
    def _module_to_file_path(self, module: str) -> str:
        """Convert module path to file path"""
        # Convert 'src.api.endpoints' to 'src/api/endpoints.py'
        parts = module.split('.')
        if len(parts) < 2 or parts[0] != 'src':
            return ''
            
        # Try different file extensions and __init__.py
        base_path = '/'.join(parts)
        candidates = [
            f"{base_path}.py",
            f"{base_path}/__init__.py"
        ]
        
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
                
        return ''
        
    def _validate_file_dependencies(self, file_path: str) -> bool:
        """Validate dependencies for a single file"""
        file_layer = self.file_to_layer.get(file_path)
        if not file_layer:
            return True  # File not in a recognized layer
            
        all_valid = True
        
        for dependency in self.dependencies[file_path]:
            dependency_layer = self.file_to_layer.get(dependency)
            if not dependency_layer:
                continue
                
            # Check if dependency is allowed
            if not self._is_dependency_allowed(file_layer, dependency_layer):
                self.errors.append(
                    f"Invalid dependency: {file_path} ({file_layer}) "
                    f"cannot import from {dependency} ({dependency_layer})"
                )
                all_valid = False
                
            # Check layer hierarchy
            if not self._is_hierarchy_valid(file_layer, dependency_layer):
                self.errors.append(
                    f"Layer hierarchy violation: {file_path} ({file_layer}) "
                    f"cannot import from higher layer {dependency} ({dependency_layer})"
                )
                all_valid = False
                
        return all_valid
        
    def _is_dependency_allowed(self, from_layer: str, to_layer: str) -> bool:
        """Check if dependency between layers is allowed"""
        allowed = ALLOWED_DEPENDENCIES.get(from_layer, [])
        return to_layer in allowed
        
    def _is_hierarchy_valid(self, from_layer: str, to_layer: str) -> bool:
        """Check if dependency respects layer hierarchy"""
        from_level = LAYER_HIERARCHY.get(from_layer, 999)
        to_level = LAYER_HIERARCHY.get(to_layer, 999)
        
        # Higher level layers can import from lower level layers
        return from_level >= to_level
        
    def _check_circular_dependencies(self) -> bool:
        """Check for circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependencies[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
                    
            rec_stack.remove(node)
            return False
            
        # Check all files for cycles
        for file_path in self.dependencies:
            if file_path not in visited:
                if has_cycle(file_path):
                    cycle_path = self._find_cycle_path(file_path)
                    self.errors.append(
                        f"Circular dependency detected: {' -> '.join(cycle_path)}"
                    )
                    return False
                    
        return True
        
    def _find_cycle_path(self, start: str) -> List[str]:
        """Find and return the path of a circular dependency"""
        visited = set()
        path = []
        
        def dfs(node: str) -> bool:
            if node in path:
                # Found cycle, return path from cycle start
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
                
            if node in visited:
                return False
                
            visited.add(node)
            path.append(node)
            
            for neighbor in self.dependencies[node]:
                result = dfs(neighbor)
                if result:
                    return result
                    
            path.pop()
            return False
            
        result = dfs(start)
        return result if result else [start]
        
    def generate_dependency_report(self) -> str:
        """Generate a detailed dependency report"""
        report = ["\n📊 Dependency Analysis Report\n"]
        report.append("=" * 40)
        
        # Layer summary
        layer_counts = defaultdict(int)
        for file_path, layer in self.file_to_layer.items():
            layer_counts[layer] += 1
            
        report.append("\n📁 Files by Layer:")
        for layer in sorted(LAYER_HIERARCHY.keys(), key=lambda x: LAYER_HIERARCHY[x]):
            count = layer_counts[layer]
            report.append(f"  {layer}: {count} files")
            
        # Dependency summary
        report.append("\n🔗 Dependencies by Layer:")
        layer_deps = defaultdict(set)
        
        for file_path, deps in self.dependencies.items():
            file_layer = self.file_to_layer.get(file_path)
            if file_layer:
                for dep in deps:
                    dep_layer = self.file_to_layer.get(dep)
                    if dep_layer and dep_layer != file_layer:
                        layer_deps[file_layer].add(dep_layer)
                        
        for layer in sorted(LAYER_HIERARCHY.keys(), key=lambda x: LAYER_HIERARCHY[x]):
            deps = sorted(layer_deps[layer])
            if deps:
                report.append(f"  {layer} → {', '.join(deps)}")
            else:
                report.append(f"  {layer} → (no dependencies)")
                
        return "\n".join(report)
        
    def print_results(self) -> bool:
        """Print validation results"""
        if self.errors:
            print("❌ Dependency Validation Errors:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("⚠️  Dependency Validation Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            print("✅ Dependency validation passed!")
            
        # Always show dependency report for insight
        print(self.generate_dependency_report())
        
        return len(self.errors) == 0

def main():
    """Main validation function"""
    # Get file paths from command line arguments
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not file_paths:
        print("Usage: python check_dependencies.py <file1.py> [file2.py ...]")
        sys.exit(1)
        
    # Create checker
    checker = DependencyChecker()
    
    # Run validation
    checker.check_files(file_paths)
    
    # Print results and exit
    success = checker.print_results()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()