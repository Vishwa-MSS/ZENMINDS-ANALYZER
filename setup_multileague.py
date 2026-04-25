"""
Setup Script for Multi-League Cricket Analytics
Run this once to configure the application for multi-league support
"""

import json
import bcrypt
import shutil
import os
from pathlib import Path

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_user_files():
    """Create user JSON files for both leagues"""
    
    print("🔐 Creating user files...")
    
    # Default admin user (same for both leagues)
    admin_user = {
        "admin": {
            "name": "Administrator",
            "password": hash_password("admin123"),
            "team": "ALL",
            "role": "admin"
        }
    }
    
    # Create APL users file
    with open('users_apl.json', 'w') as f:
        json.dump(admin_user, f, indent=4)
    print("✅ Created users_apl.json")
    
    # Create MPL users file
    with open('users_mpl.json', 'w') as f:
        json.dump(admin_user, f, indent=4)
    print("✅ Created users_mpl.json")

def backup_old_files():
    """Backup original files"""
    
    print("\n📦 Backing up original files...")
    
    backups = [
        ('app.py', 'app_old.py'),
        ('auth.py', 'auth_old.py')
    ]
    
    for original, backup in backups:
        if os.path.exists(original):
            if not os.path.exists(backup):
                shutil.copy2(original, backup)
                print(f"✅ Backed up {original} → {backup}")
            else:
                print(f"⚠️  Backup already exists: {backup}")
        else:
            print(f"⚠️  Original not found: {original}")

def activate_new_files():
    """Rename new files to active names"""
    
    print("\n🔄 Activating new files...")
    
    renames = [
        ('app_new.py', 'app.py'),
        ('auth_multi.py', 'auth.py')
    ]
    
    for new_name, active_name in renames:
        if os.path.exists(new_name):
            # Remove old active file if exists
            if os.path.exists(active_name) and not os.path.exists(active_name.replace('.py', '_old.py')):
                shutil.move(active_name, active_name.replace('.py', '_old.py'))
            
            # Rename new file to active
            shutil.copy2(new_name, active_name)
            print(f"✅ Activated {new_name} → {active_name}")
        else:
            print(f"❌ File not found: {new_name}")

def verify_data_files():
    """Verify that data files exist"""
    
    print("\n📊 Verifying data files...")
    
    data_files = [
        'APL_2025_LeagueData.csv',
        'maharaja_bbb_final.csv'
    ]
    
    all_present = True
    for data_file in data_files:
        if os.path.exists(data_file):
            print(f"✅ Found {data_file}")
        else:
            print(f"❌ Missing {data_file}")
            all_present = False
    
    return all_present

def verify_modules():
    """Verify that all modules exist"""
    
    print("\n🔧 Verifying modules...")
    
    modules = [
        'modules/batting_module.py',
        'modules/bowling_module.py',
        'modules/partnerships_module.py',
        'modules/extras_module.py',
        'modules/wides_module.py'
    ]
    
    all_present = True
    for module in modules:
        if os.path.exists(module):
            print(f"✅ Found {module}")
        else:
            print(f"❌ Missing {module}")
            all_present = False
    
    return all_present

def main():
    """Main setup function"""
    
    print("=" * 60)
    print("🏏 MULTI-LEAGUE CRICKET ANALYTICS - SETUP")
    print("=" * 60)
    
    # Step 1: Create user files
    create_user_files()
    
    # Step 2: Backup original files
    backup_old_files()
    
    # Step 3: Activate new files
    activate_new_files()
    
    # Step 4: Verify data files
    data_ok = verify_data_files()
    
    # Step 5: Verify modules
    modules_ok = verify_modules()
    
    # Final status
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    if data_ok and modules_ok:
        print("✅ Setup completed successfully!")
        print("\n🚀 Next Steps:")
        print("1. Run: streamlit run app.py")
        print("2. Select APL or MPL from landing page")
        print("3. Enter league password:")
        print("   - APL: APL@#zenminds")
        print("   - MPL: MPL@#zenminds")
        print("4. Login with admin/admin123")
        print("\n🎉 Your multi-league analyzer is ready!")
    else:
        print("⚠️  Setup completed with warnings")
        print("Please check missing files above")
    
    print("=" * 60)

if __name__ == "__main__":
    main()