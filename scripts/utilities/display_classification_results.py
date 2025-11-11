#!/usr/bin/env python3
"""
Display classification results in readable format
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from product_classification_engine import run_trial_classification


def display_product_result(result, index, total):
    """Display a single product's classification result"""
    
    print(f"\n{'='*80}")
    print(f"PRODUCT {index}/{total} | Confidence: {result['overall_confidence']} | "
          f"{'✅ HIGH' if result['overall_confidence'] >= 0.7 else '⚠️ MEDIUM' if result['overall_confidence'] >= 0.5 else '❌ LOW'}")
    print(f"{'='*80}")
    
    # Original fields
    print(f"\n📋 ORIGINAL:")
    print(f"  Category: {result['original_category']}")
    print(f"  Subcategory: {result['original_subcategory']}")
    print(f"  Brand: {result['original_brand']}")
    print(f"  Product Name: {result['original_name']}")
    
    # New/Extracted fields
    print(f"\n✨ EXTRACTED/NEW:")
    
    # Show clean name
    if result['clean_product_name'] != result['original_name']:
        print(f"  Clean Name: {result['clean_product_name']}")
        print(f"    └─ Confidence: {result['name_parsing_confidence']}")
    
    # Show new subcategory if changed
    if result['new_subcategory'] != result['original_subcategory']:
        print(f"  New Subcategory: {result['original_subcategory']} → {result['new_subcategory']}")
        print(f"    └─ Confidence: {result['category_confidence']} ({result['classification_method']})")
    else:
        print(f"  Subcategory: {result['new_subcategory']} (unchanged)")
    
    # Show extracted brand if different
    if result['extracted_brand'] != result['original_brand']:
        print(f"  Extracted Brand: {result['extracted_brand']}")
        print(f"    └─ Confidence: {result['brand_confidence']}")
    
    # Show size info if extracted
    if result['size_info']:
        print(f"  Size Info: {result['size_info']}")
    
    # Show pack info if extracted
    if result['pack_info']:
        print(f"  Pack Info: {result['pack_info']}")
    
    # Show special features if extracted
    if result['special_features']:
        print(f"  Special Features: {result['special_features']}")
    
    # Show review flag
    if result['needs_manual_review']:
        print(f"\n⚠️  NEEDS MANUAL REVIEW")
    
    print(f"\n📝 Notes: {result['processing_notes']}")


def display_results_by_confidence(results_df, high_conf, medium_conf, low_conf):
    """Display results grouped by confidence level"""
    
    print("\n" + "="*80)
    print("DISPLAYING RESULTS BY CONFIDENCE LEVEL")
    print("="*80)
    
    # Display HIGH confidence results
    if len(high_conf) > 0:
        print(f"\n\n{'#'*80}")
        print(f"HIGH CONFIDENCE RESULTS (>= 0.7) - {len(high_conf)} products")
        print(f"{'#'*80}")
        
        for idx, (_, result) in enumerate(high_conf.iterrows(), 1):
            display_product_result(result, idx, len(high_conf))
    
    # Display MEDIUM confidence results
    if len(medium_conf) > 0:
        print(f"\n\n{'#'*80}")
        print(f"MEDIUM CONFIDENCE RESULTS (0.5-0.7) - {len(medium_conf)} products")
        print(f"{'#'*80}")
        
        for idx, (_, result) in enumerate(medium_conf.iterrows(), 1):
            display_product_result(result, idx, len(medium_conf))
    
    # Display LOW confidence results
    if len(low_conf) > 0:
        print(f"\n\n{'#'*80}")
        print(f"LOW CONFIDENCE RESULTS (< 0.5) - {len(low_conf)} products")
        print(f"{'#'*80}")
        
        for idx, (_, result) in enumerate(low_conf.iterrows(), 1):
            display_product_result(result, idx, len(low_conf))
    
    # Final summary
    print(f"\n\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"Total Products Processed: {len(results_df)}")
    print(f"High Confidence (>= 0.7): {len(high_conf)} ({len(high_conf)/len(results_df)*100:.1f}%)")
    print(f"Medium Confidence (0.5-0.7): {len(medium_conf)} ({len(medium_conf)/len(results_df)*100:.1f}%)")
    print(f"Low Confidence (< 0.5): {len(low_conf)} ({len(low_conf)/len(results_df)*100:.1f}%)")
    print()
    
    # Confidence threshold recommendation
    avg_confidence = results_df['overall_confidence'].mean()
    print(f"Average Confidence: {avg_confidence:.2f}")
    
    if avg_confidence >= 0.75:
        print("✅ Recommendation: Current threshold of 0.7 is appropriate")
    elif avg_confidence >= 0.65:
        print("⚠️  Recommendation: Consider lowering threshold to 0.65")
    else:
        print("❌ Recommendation: Results need improvement, consider LLM fallback")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Run trial classification
    results_df, high_conf, medium_conf, low_conf = run_trial_classification(
        batch_size=50,
        min_name_length=80
    )
    
    # Display results
    display_results_by_confidence(results_df, high_conf, medium_conf, low_conf)
