"""
Setup Script for CyberTool
Automated installation and configuration
"""

import sys
import subprocess
import os
from pathlib import Path


def print_header():
    """Print setup header."""
    print("=" * 60)
    print("  CyberTool - Modular Red/Blue Team Platform")
    print("  Setup and Installation Script")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version meets requirements."""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_dependencies():
    """Install required Python packages."""
    print("\nInstalling dependencies...")
    print("-" * 60)
    
    dependencies = [
        "PyQt6>=6.4.0",
        "psutil>=5.9.0"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", dep],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {dep}")
            return False
    
    return True


def verify_installation():
    """Verify all required packages are installed."""
    print("\nVerifying installation...")
    print("-" * 60)
    
    packages = {
        "PyQt6": "PyQt6",
        "psutil": "psutil"
    }
    
    all_installed = True
    
    for name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {name} is available")
        except ImportError:
            print(f"❌ {name} is not available")
            all_installed = False
    
    return all_installed


def create_directory_structure():
    """Create necessary directories."""
    print("\nCreating directory structure...")
    print("-" * 60)
    
    directories = [
        "ui",
        "exports",
        "backups"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True)
            print(f"✅ Created: {directory}/")
        else:
            print(f"ℹ️  Exists: {directory}/")
    
    return True


def create_ui_init():
    """Create __init__.py for ui package."""
    ui_init = Path("ui") / "__init__.py"
    
    if not ui_init.exists():
        ui_init.write_text('"""UI package for CyberTool"""')
        print("✅ Created: ui/__init__.py")
    
    return True


def check_required_files():
    """Check if all required files exist."""
    print("\nChecking required files...")
    print("-" * 60)
    
    required_files = [
        "main.py",
        "red_team.py",
        "blue_team.py",
        "database.py",
        "logger.py",
        "config.py",
        "ui/styles.py"
    ]
    
    all_present = True
    
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            all_present = False
    
    return all_present


def run_initial_test():
    """Run a quick test to ensure the application can start."""
    print("\nRunning initial test...")
    print("-" * 60)
    
    try:
        # Try to import main modules
        import main
        import red_team
        import blue_team
        import database
        import logger
        
        print("✅ All modules can be imported")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("   1. Review QUICKSTART.md for usage guide")
    print("   2. Run the application: python main.py")
    print("   3. Try your first scan on localhost")
    print("   4. Enable Blue Team monitoring")
    print("   5. Review audit logs in the Logs tab")
    print("\n⚠️  Important Reminders:")
    print("   • Only scan systems you own or have permission to test")
    print("   • Always obtain written authorization")
    print("   • Review logs regularly for security")
    print("   • Keep sensitive data secure")
    print("\n🚀 To start the application:")
    print("   python main.py")
    print("\n📚 For detailed documentation:")
    print("   See README.md and QUICKSTART.md")
    print()


def main():
    """Main setup function."""
    print_header()
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version requirement not met")
        return 1
    
    # Step 2: Install dependencies
    print("\n" + "=" * 60)
    print("Installing dependencies...")
    print("=" * 60)
    
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        print("   Try manually: pip install -r requirements.txt")
        return 1
    
    # Step 3: Verify installation
    if not verify_installation():
        print("\n❌ Setup failed: Dependencies not properly installed")
        return 1
    
    # Step 4: Create directories
    if not create_directory_structure():
        print("\n❌ Setup failed: Could not create directories")
        return 1
    
    # Step 5: Create UI package init
    create_ui_init()
    
    # Step 6: Check required files
    if not check_required_files():
        print("\n⚠️  Warning: Some required files are missing")
        print("   The application may not work correctly")
    
    # Step 7: Run initial test
    if not run_initial_test():
        print("\n⚠️  Warning: Initial test failed")
        print("   The application may not work correctly")
    
    # Step 8: Print success and next steps
    print_next_steps()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())