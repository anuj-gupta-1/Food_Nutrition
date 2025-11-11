#!/usr/bin/env python3
"""
Display LLM classification results in readable format
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from llm_classifier import run_llm_trial_classification


def display_product_result(result, index, total):
    """Display a single product's LLM classification result"""
    
    print(f"\n{'='*80}")
    print(f"PRODUCT {index}/{total} | Confidence: {result['confidence_score']:.2f} | "
          f"{'✅ HIGH' if result['confidence_score'] >= 0.7 else '⚠️ MEDIUM' if result['confidence_score'] >= 0.5 else '❌ LOW'}")
    print(f"{'='*80}")
    
    # Original fields
    print(f"\n📋 ORIGINAL:")
    print(f"  Category: {result['original_category']}")
    print(f"  Subcategory: {result['original_subcategory']}")
    print(f"  Brand: {result['original_brand']}")
    print(f"  Product Name: {result['original_name']}")
    
    # New/Extracted fields
    print(f"\n✨ LLM EXTRACTED:")
    
    # Show clean name
    if result['clean_product_name'] and result['clean_product_name'] != result['original_name']:
        print(f"  Clean Name: {result['clean_product_name']}")
        print(f"    └─ Confidence: {result['confidence_score']:.2f}")
    else:
        print(f"  Clean Name: (unchanged or not extracted)")
    
    # Show new subcategory if changed
    if result['new_subcategory'] != result['original_subcategory']:
        print(f"  New Subcategory: {result['original_subcategory']} → {result['new_subcategory']}")
        print(f"    └─ Method: {result['classification_method']}")
    else:
        print(f"  Subcategory: {result['new_subcategory']} (unchanged)")
    
    # Show review flag
    if result['needs_manual_review']:
        print(f"\n⚠️  NEEDS MANUAL REVIEW")
    
    print(f"\n📝 Notes: {result['processing_notes']}")


def display_results_by_confidence(results_df, high_conf, medium_conf, low_conf):
    """Display results grouped by confidence level"""
    
    print("\n" + "="*80)
    print("DISPLAYING LLM RESULTS BY CONFIDENCE LEVEL")
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
    avg_confidence = results_df['confidence_score'].mean()
    print(f"Average Confidence: {avg_confidence:.2f}")
    
    if avg_confidence >= 0.75:
        print("✅ Recommendation: LLM classification is working well")
    elif avg_confidence >= 0.65:
        print("⚠️  Recommendation: Results are acceptable, may need prompt tuning")
    else:
        print("❌ Recommendation: LLM needs prompt improvement or different model")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Run LLM trial classification
    print("Starting LLM-based classification trial...")
    print("This will take a few minutes due to API rate limits...\n")
    
    results_df, high_conf, medium_conf, low_conf = run_llm_trial_classification(
        batch_size=10,
        min_name_length=80
    )
    
    # Display results
    display_results_by_confidence(results_df, high_conf, medium_conf, low_conf)
