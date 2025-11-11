#!/usr/bin/env python3
"""
Update Android Assets - Copy updated CSV to Android app assets
This script automatically updates the Android app with the latest product data
"""

import os
import shutil
import sys
from datetime import datetime

def update_android_assets():
    """Update Android app assets with latest product data"""
    
    print("📱 UPDATING ANDROID ASSETS")
    print("=" * 40)
    
    # Paths
    source_csv = "data/products.csv"
    android_assets_path = "android_app/app/src/main/assets/products.csv"
    
    # Check if source exists
    if not os.path.exists(source_csv):
        print(f"❌ Source CSV not found: {source_csv}")
        return False
    
    # Check if Android app directory exists
    android_dir = os.path.dirname(android_assets_path)
    if not os.path.exists(android_dir):
        print(f"❌ Android assets directory not found: {android_dir}")
        print("💡 Make sure you're running from the project root directory")
        return False
    
    try:
        # Create backup of existing Android CSV if it exists
        if os.path.exists(android_assets_path):
            backup_path = f"{android_assets_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(android_assets_path, backup_path)
            print(f"💾 Backup created: {backup_path}")
        
        # Copy updated CSV to Android assets
        shutil.copy2(source_csv, android_assets_path)
        print(f"✅ Updated Android assets: {android_assets_path}")
        
        # Get file sizes for verification
        source_size = os.path.getsize(source_csv)
        android_size = os.path.getsize(android_assets_path)
        
        print(f"📊 File size: {source_size:,} bytes")
        print(f"🔍 Verification: {'✅ Match' if source_size == android_size else '❌ Size mismatch'}")
        
        print(f"\n🎉 ANDROID ASSETS UPDATED SUCCESSFULLY!")
        print("📱 Android app now has the latest product data")
        print("🚀 Ready for build and deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Android assets: {e}")
        return False

if __name__ == "__main__":
    success = update_android_assets()
    sys.exit(0 if success else 1)