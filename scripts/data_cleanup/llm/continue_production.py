#!/usr/bin/env python3
"""
Continue production classification without prompts
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))
from run_production import run_production_classification

if __name__ == "__main__":
    print("\n🚀 Continuing LLM classification from where we left off...")
    print("   - Processing products with names >= 80 characters")
    print("   - Saving checkpoints every 100 products")
    print()
    
    success = run_production_classification(
        min_name_length=80,
        batch_size=100,
        delay_seconds=1.0
    )
    
    if not success:
        print("❌ Production run failed")
        sys.exit(1)
    else:
        print("✅ Production run completed successfully!")
