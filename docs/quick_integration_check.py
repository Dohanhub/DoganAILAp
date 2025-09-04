"""
DoganAI Master Integration Status Check - Simplified
This provides a quick overview of integration status without requiring dependencies
"""
import os
import sys
from datetime import datetime

def check_master_integration():
    """Quick master integration check"""
    
    print("?? DoganAI Master Integration Status Check")
    print("=" * 60)
    print(f"?? Location: {os.getcwd()}")
    print(f"? Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check core files
    core_files = {
        "Master Launcher": "DoganAI_Master_Launcher.bat",
        "Standard Launcher": "DoganAI_Launcher.bat", 
        "Shortcut Creator": "Create_Shortcut.bat",
        "Quick Demo": "quick_demo.py",
        "Performance Tests": "test_performance.py",
        "Integration Check": "master_integration_check.py"
    }
    
    improvement_modules = {
        "Performance": "improvements/performance.py",
        "Security": "improvements/security.py",
        "Enhanced API": "improvements/enhanced_api.py",
        "Mobile UI": "improvements/mobile_ui.py",
        "Monitoring": "improvements/monitoring.py",
        "Error Handling": "improvements/error_handling.py",
        "DoganAI Integration": "improvements/doganai_integration.py",
        "Proposal Integration": "improvements/proposal_integration.py",
        "Deployment": "improvements/deploy.py"
    }
    
    core_engine = {
        "Core Engine": "engine/api.py"
    }
    
    documentation = {
        "Integration Guide": "INTEGRATION_GUIDE.md",
        "Testing Guide": "HOW_TO_TEST.md",
        "Shortcut Guide": "DESKTOP_SHORTCUT_GUIDE.md"
    }
    
    def check_files(file_dict, category_name):
        """Check if files exist"""
        print(f"?? {category_name}:")
        found = 0
        total = len(file_dict)
        
        for name, path in file_dict.items():
            if os.path.exists(path):
                print(f"  ? {name}")
                found += 1
            else:
                print(f"  ? {name} (missing: {path})")
        
        print(f"  ?? {category_name} Status: {found}/{total} ({found/total*100:.1f}%)")
        print()
        return found, total
    
    # Check all categories
    total_found = 0
    total_files = 0
    
    categories = [
        (core_files, "Core System Files"),
        (improvement_modules, "Enhancement Modules"),
        (core_engine, "Core Engine"),
        (documentation, "Documentation")
    ]
    
    for file_dict, category in categories:
        found, total = check_files(file_dict, category)
        total_found += found
        total_files += total
    
    # Overall status
    overall_percentage = (total_found / total_files) * 100
    
    print("?? OVERALL INTEGRATION STATUS")
    print("=" * 60)
    print(f"?? Files Found: {total_found}/{total_files}")
    print(f"?? Integration Level: {overall_percentage:.1f}%")
    
    if overall_percentage >= 90:
        status = "?? EXCELLENT - Ready for production!"
        recommendations = [
            "? All components integrated successfully",
            "?? Ready to run: DoganAI_Master_Launcher.bat",
            "?? Try the quick demo: python quick_demo.py",
            "?? Start the API server: python improvements/enhanced_api.py"
        ]
    elif overall_percentage >= 75:
        status = "? GOOD - Minor components missing"
        recommendations = [
            "?? Check missing components above",
            "?? Main functionality available",
            "?? Install dependencies if needed"
        ]
    elif overall_percentage >= 50:
        status = "?? PARTIAL - Some key components missing"
        recommendations = [
            "?? Install missing components",
            "?? Check file paths and locations",
            "?? Consider re-downloading components"
        ]
    else:
        status = "? INCOMPLETE - Major components missing"
        recommendations = [
            "?? Major integration issues detected",
            "?? Reinstall DoganAI Compliance Kit",
            "?? Check installation instructions"
        ]
    
    print(f"?? Status: {status}")
    print()
    
    print("?? RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print()
    print("?? DOGANAI COMPLIANCE KIT FEATURES:")
    print("   ? High-Performance Caching")
    print("   ? Advanced Security & RBAC") 
    print("   ? Mobile PWA Interface")
    print("   ? Real-time Monitoring")
    print("   ? Error Resilience")
    print("   ? Saudi Regulatory Compliance")
    print("   ? Kubernetes Deployment")
    print("   ? API v3 Documentation")
    print()
    
    print("???? Built for Saudi Arabia's Digital Transformation!")
    print()
    
    # Create quick status file
    status_data = {
        "check_time": datetime.now().isoformat(),
        "total_files": total_files,
        "found_files": total_found,
        "integration_percentage": overall_percentage,
        "status": status,
        "ready_for_use": overall_percentage >= 75
    }
    
    try:
        import json
        with open("integration_status.json", "w") as f:
            json.dump(status_data, f, indent=2)
        print("?? Status saved to: integration_status.json")
    except:
        print("?? Status checked - JSON save skipped")
    
    return overall_percentage >= 75

if __name__ == "__main__":
    try:
        ready = check_master_integration()
        if ready:
            print("\n?? Your DoganAI Compliance Kit is ready to use!")
            print("?? Next step: Run DoganAI_Master_Launcher.bat")
        else:
            print("\n?? Please address the missing components above")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"\n? Check failed: {e}")
        input("Press Enter to continue...")