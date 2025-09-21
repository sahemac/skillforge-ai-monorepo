#!/usr/bin/env python3
"""
Check that all SQLModel models are properly defined
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_models():
    """Check all models are properly imported and defined"""
    
    print("🔍 Checking SQLModel models...")
    
    try:
        # Import base
        from app.models.base import SQLModel
        print("✅ Base SQLModel imported")
        
        # Import user models
        from app.models.user_simple import User, UserSettings, UserSession
        print("✅ User models imported:", User.__tablename__, UserSettings.__tablename__, UserSession.__tablename__)
        
        # Import company models  
        from app.models.company_simple import CompanyProfile, TeamMember, Subscription
        print("✅ Company models imported:", CompanyProfile.__tablename__, TeamMember.__tablename__, Subscription.__tablename__)
        
        # Check metadata
        print(f"\n📊 Registered tables ({len(SQLModel.metadata.tables)}):")
        for table_name, table in SQLModel.metadata.tables.items():
            print(f"  - {table_name} ({len(table.columns)} columns)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 SkillForge AI User Service - Model Check")
    
    if check_models():
        print("\n✅ All models are properly defined!")
    else:
        print("\n❌ Model check failed!")
        sys.exit(1)