"""
Data Completion Analysis for Master Product File
Analyzes field completeness, data quality, and useful metrics
"""

import pandas as pd
import json
import numpy as np
from collections import Counter
from datetime import datetime

print("📦 Imports successful")

def load_master_data():
    """Load the master product file with proper parsing"""
    try:
        print("🔄 Loading master product file...")
        # Read with custom separator and handle parsing issues
        df = pd.read_csv('data/products.csv', sep='||', engine='python', on_bad_lines='skip')
        print(f"✅ Loaded {len(df)} products from master file")
        print(f"📋 Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_field_completeness(df):
    """Analyze completeness of each field"""
    print("\n" + "="*60)
    print("📊 FIELD COMPLETENESS ANALYSIS")
    print("="*60)
    
    total_products = len(df)
    completeness_stats = {}
    
    for column in df.columns:
        # Count non-null, non-empty values
        non_null = df[column].notna().sum()
        non_empty = df[column].fillna('').astype(str).str.strip().ne('').sum()
        
        # Calculate percentages
        null_pct = ((total_products - non_null) / total_products) * 100
        empty_pct = ((total_products - non_empty) / total_products) * 100
        complete_pct = (non_empty / total_products) * 100
        
        completeness_stats[column] = {
            'total_products': total_products,
            'non_null': non_null,
            'non_empty': non_empty,
            'null_pct': null_pct,
            'empty_pct': empty_pct,
            'complete_pct': complete_pct
        }
        
        # Categorize completeness
        if complete_pct >= 90:
            status = "🟢 EXCELLENT"
        elif complete_pct >= 70:
            status = "🟡 GOOD"
        elif complete_pct >= 50:
            status = "🟠 FAIR"
        else:
            status = "🔴 POOR"
        
        print(f"{column:20} | {complete_pct:6.1f}% complete | {status}")
    
    return completeness_stats

def analyze_nutrition_data_quality(df):
    """Analyze the quality of nutrition_data field specifically"""
    print("\n" + "="*60)
    print("🥗 NUTRITION DATA QUALITY ANALYSIS")
    print("="*60)
    
    nutrition_stats = {
        'total_products': len(df),
        'has_nutrition_field': 0,
        'has_valid_json': 0,
        'has_any_nutrition_values': 0,
        'nutrition_fields_populated': {},
        'empty_nutrition': 0,
        'null_nutrition': 0
    }
    
    # Standard nutrition fields we expect
    expected_nutrition_fields = [
        'energy_kcal', 'fat_g', 'saturated_fat_g', 'carbs_g', 
        'sugars_g', 'protein_g', 'salt_g', 'fiber_g', 'sodium_mg'
    ]
    
    for field in expected_nutrition_fields:
        nutrition_stats['nutrition_fields_populated'][field] = 0
    
    for idx, row in df.iterrows():
        nutrition_data = row.get('nutrition_data', '')
        
        # Check if field exists and is not null
        if pd.notna(nutrition_data) and nutrition_data.strip():
            nutrition_stats['has_nutrition_field'] += 1
            
            try:
                # Try to parse JSON
                nutrition_json = json.loads(nutrition_data)
                nutrition_stats['has_valid_json'] += 1
                
                # Check if any nutrition values are present (not null)
                has_values = False
                for field in expected_nutrition_fields:
                    if field in nutrition_json and nutrition_json[field] is not None:
                        nutrition_stats['nutrition_fields_populated'][field] += 1
                        has_values = True
                
                if has_values:
                    nutrition_stats['has_any_nutrition_values'] += 1
                    
            except (json.JSONDecodeError, TypeError):
                # Invalid JSON
                pass
        else:
            if pd.isna(nutrition_data):
                nutrition_stats['null_nutrition'] += 1
            else:
                nutrition_stats['empty_nutrition'] += 1
    
    # Print nutrition analysis
    total = nutrition_stats['total_products']
    print(f"Total products: {total}")
    print(f"Has nutrition field: {nutrition_stats['has_nutrition_field']} ({nutrition_stats['has_nutrition_field']/total*100:.1f}%)")
    print(f"Valid JSON format: {nutrition_stats['has_valid_json']} ({nutrition_stats['has_valid_json']/total*100:.1f}%)")
    print(f"Has actual nutrition values: {nutrition_stats['has_any_nutrition_values']} ({nutrition_stats['has_any_nutrition_values']/total*100:.1f}%)")
    print(f"Empty nutrition data: {nutrition_stats['empty_nutrition']} ({nutrition_stats['empty_nutrition']/total*100:.1f}%)")
    print(f"Null nutrition data: {nutrition_stats['null_nutrition']} ({nutrition_stats['null_nutrition']/total*100:.1f}%)")
    
    print(f"\n📋 Individual Nutrition Fields:")
    for field, count in nutrition_stats['nutrition_fields_populated'].items():
        pct = (count / total) * 100
        print(f"  {field:15} | {count:5} products ({pct:5.1f}%)")
    
    return nutrition_stats

def analyze_data_sources(df):
    """Analyze data by source"""
    print("\n" + "="*60)
    print("📡 DATA SOURCE ANALYSIS")
    print("="*60)
    
    source_stats = df['source'].value_counts()
    total = len(df)
    
    print(f"Total products: {total}")
    print(f"Number of sources: {len(source_stats)}")
    print(f"\nBreakdown by source:")
    
    for source, count in source_stats.items():
        pct = (count / total) * 100
        print(f"  {source:15} | {count:6} products ({pct:5.1f}%)")
    
    return source_stats

def analyze_categories(df):
    """Analyze product categories"""
    print("\n" + "="*60)
    print("🏷️  CATEGORY ANALYSIS")
    print("="*60)
    
    category_stats = df['category'].value_counts()
    total = len(df)
    
    print(f"Total products: {total}")
    print(f"Number of categories: {len(category_stats)}")
    print(f"\nBreakdown by category:")
    
    for category, count in category_stats.items():
        pct = (count / total) * 100
        print(f"  {category:15} | {count:6} products ({pct:5.1f}%)")
    
    # Analyze subcategories
    subcategory_stats = df['subcategory'].value_counts()
    print(f"\nSubcategories: {len(subcategory_stats)} unique")
    print(f"Top 10 subcategories:")
    for subcat, count in subcategory_stats.head(10).items():
        pct = (count / total) * 100
        print(f"  {subcat:20} | {count:5} products ({pct:4.1f}%)")
    
    return category_stats, subcategory_stats

def analyze_data_quality_scores(df):
    """Analyze data quality scores"""
    print("\n" + "="*60)
    print("⭐ DATA QUALITY SCORE ANALYSIS")
    print("="*60)
    
    if 'data_quality_score' in df.columns:
        scores = df['data_quality_score'].dropna()
        
        print(f"Products with quality scores: {len(scores)}")
        print(f"Average quality score: {scores.mean():.1f}")
        print(f"Median quality score: {scores.median():.1f}")
        print(f"Min quality score: {scores.min()}")
        print(f"Max quality score: {scores.max()}")
        print(f"Standard deviation: {scores.std():.1f}")
        
        # Quality score distribution
        print(f"\nQuality Score Distribution:")
        print(f"  90-100 (Excellent): {len(scores[scores >= 90])} ({len(scores[scores >= 90])/len(scores)*100:.1f}%)")
        print(f"  80-89  (Good):      {len(scores[(scores >= 80) & (scores < 90)])} ({len(scores[(scores >= 80) & (scores < 90)])/len(scores)*100:.1f}%)")
        print(f"  70-79  (Fair):      {len(scores[(scores >= 70) & (scores < 80)])} ({len(scores[(scores >= 70) & (scores < 80)])/len(scores)*100:.1f}%)")
        print(f"  60-69  (Poor):      {len(scores[(scores >= 60) & (scores < 70)])} ({len(scores[(scores >= 60) & (scores < 70)])/len(scores)*100:.1f}%)")
        print(f"  <60    (Very Poor): {len(scores[scores < 60])} ({len(scores[scores < 60])/len(scores)*100:.1f}%)")
        
        return scores
    else:
        print("❌ No data_quality_score field found")
        return None

def analyze_missing_critical_data(df):
    """Identify products missing critical data"""
    print("\n" + "="*60)
    print("🚨 MISSING CRITICAL DATA ANALYSIS")
    print("="*60)
    
    critical_fields = ['product_name', 'brand', 'category', 'source']
    
    missing_stats = {}
    total = len(df)
    
    for field in critical_fields:
        if field in df.columns:
            missing = df[field].isna() | (df[field].astype(str).str.strip() == '')
            missing_count = missing.sum()
            missing_pct = (missing_count / total) * 100
            missing_stats[field] = {
                'count': missing_count,
                'percentage': missing_pct
            }
            
            status = "🔴 CRITICAL" if missing_pct > 5 else "🟡 MINOR" if missing_pct > 1 else "🟢 GOOD"
            print(f"{field:15} | {missing_count:5} missing ({missing_pct:5.1f}%) | {status}")
    
    # Find products missing multiple critical fields
    products_missing_multiple = 0
    for idx, row in df.iterrows():
        missing_count = 0
        for field in critical_fields:
            if field in df.columns:
                if pd.isna(row[field]) or str(row[field]).strip() == '':
                    missing_count += 1
        if missing_count >= 2:
            products_missing_multiple += 1
    
    print(f"\nProducts missing 2+ critical fields: {products_missing_multiple} ({products_missing_multiple/total*100:.1f}%)")
    
    return missing_stats

def analyze_llm_enhancement_potential(df):
    """Analyze potential for LLM enhancement"""
    print("\n" + "="*60)
    print("🤖 LLM ENHANCEMENT POTENTIAL")
    print("="*60)
    
    total = len(df)
    
    # Products that could benefit from LLM enhancement
    needs_nutrition = 0
    needs_ingredients = 0
    needs_enhancement = 0
    already_enhanced = 0
    
    for idx, row in df.iterrows():
        # Check if already LLM enhanced
        if row.get('llm_fallback_used', False):
            already_enhanced += 1
            continue
        
        # Check nutrition data
        nutrition_data = row.get('nutrition_data', '')
        has_nutrition = False
        if pd.notna(nutrition_data) and nutrition_data.strip():
            try:
                nutrition_json = json.loads(nutrition_data)
                # Check if any nutrition values are not null
                for key, value in nutrition_json.items():
                    if value is not None and key != 'confidence':
                        has_nutrition = True
                        break
            except:
                pass
        
        if not has_nutrition:
            needs_nutrition += 1
        
        # Check ingredients
        ingredients = row.get('ingredients', '')
        if pd.isna(ingredients) or str(ingredients).strip() == '':
            needs_ingredients += 1
        
        # Overall enhancement potential
        if not has_nutrition or pd.isna(ingredients) or str(ingredients).strip() == '':
            needs_enhancement += 1
    
    print(f"Total products: {total}")
    print(f"Already LLM enhanced: {already_enhanced} ({already_enhanced/total*100:.1f}%)")
    print(f"Need nutrition data: {needs_nutrition} ({needs_nutrition/total*100:.1f}%)")
    print(f"Need ingredients: {needs_ingredients} ({needs_ingredients/total*100:.1f}%)")
    print(f"Could benefit from LLM: {needs_enhancement} ({needs_enhancement/total*100:.1f}%)")
    
    # Estimate LLM workload
    print(f"\n📊 LLM Enhancement Workload:")
    print(f"  High priority (no nutrition): {needs_nutrition} products")
    print(f"  Medium priority (no ingredients): {needs_ingredients - needs_nutrition} products")
    print(f"  Estimated API calls needed: {needs_enhancement}")
    
    return {
        'total': total,
        'already_enhanced': already_enhanced,
        'needs_nutrition': needs_nutrition,
        'needs_ingredients': needs_ingredients,
        'needs_enhancement': needs_enhancement
    }

def generate_summary_report(df, completeness_stats, nutrition_stats, source_stats, category_stats, quality_scores, missing_stats, llm_stats):
    """Generate comprehensive summary report"""
    print("\n" + "="*60)
    print("📋 COMPREHENSIVE DATA COMPLETION SUMMARY")
    print("="*60)
    
    total_products = len(df)
    
    # Overall completeness score
    field_completeness = [stats['complete_pct'] for stats in completeness_stats.values()]
    avg_completeness = np.mean(field_completeness)
    
    # Critical field completeness
    critical_fields = ['product_name', 'brand', 'category', 'source']
    critical_completeness = np.mean([completeness_stats[field]['complete_pct'] 
                                   for field in critical_fields if field in completeness_stats])
    
    print(f"📊 OVERALL METRICS:")
    print(f"  Total products: {total_products:,}")
    print(f"  Data sources: {len(source_stats)}")
    print(f"  Categories: {len(category_stats)}")
    print(f"  Average field completeness: {avg_completeness:.1f}%")
    print(f"  Critical field completeness: {critical_completeness:.1f}%")
    
    if quality_scores is not None:
        print(f"  Average quality score: {quality_scores.mean():.1f}/100")
    
    print(f"\n🎯 KEY FINDINGS:")
    
    # Best completed fields
    best_fields = sorted(completeness_stats.items(), key=lambda x: x[1]['complete_pct'], reverse=True)[:3]
    print(f"  Best completed fields:")
    for field, stats in best_fields:
        print(f"    • {field}: {stats['complete_pct']:.1f}% complete")
    
    # Worst completed fields
    worst_fields = sorted(completeness_stats.items(), key=lambda x: x[1]['complete_pct'])[:3]
    print(f"  Fields needing improvement:")
    for field, stats in worst_fields:
        print(f"    • {field}: {stats['complete_pct']:.1f}% complete")
    
    # Nutrition data status
    nutrition_completeness = (nutrition_stats['has_any_nutrition_values'] / total_products) * 100
    print(f"  Nutrition data completeness: {nutrition_completeness:.1f}%")
    
    # LLM enhancement potential
    llm_potential = (llm_stats['needs_enhancement'] / total_products) * 100
    print(f"  Products needing LLM enhancement: {llm_potential:.1f}%")
    
    print(f"\n🚀 RECOMMENDATIONS:")
    
    if nutrition_completeness < 10:
        print(f"  🔴 URGENT: Implement LLM nutrition enhancement ({llm_stats['needs_nutrition']} products)")
    
    if any(stats['complete_pct'] < 50 for stats in completeness_stats.values()):
        poor_fields = [field for field, stats in completeness_stats.items() if stats['complete_pct'] < 50]
        print(f"  🟡 Improve data collection for: {', '.join(poor_fields)}")
    
    if len(source_stats) < 3:
        print(f"  🟡 Add more data sources for better coverage")
    
    print(f"  🟢 Prioritize LLM enhancement for {llm_stats['needs_nutrition']} products missing nutrition")
    
    # Save summary to file
    summary = {
        'analysis_date': datetime.now().isoformat(),
        'total_products': total_products,
        'data_sources': len(source_stats),
        'categories': len(category_stats),
        'avg_completeness': avg_completeness,
        'critical_completeness': critical_completeness,
        'nutrition_completeness': nutrition_completeness,
        'llm_enhancement_potential': llm_potential,
        'field_completeness': completeness_stats,
        'nutrition_stats': nutrition_stats,
        'llm_stats': llm_stats
    }
    
    with open('data_completion_report.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n✅ Detailed report saved to: data_completion_report.json")

def main():
    """Run comprehensive data completion analysis"""
    print("🔍 FOOD NUTRITION DATA COMPLETION ANALYSIS")
    print("=" * 60)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    df = load_master_data()
    if df is None:
        return
    
    # Run all analyses
    completeness_stats = analyze_field_completeness(df)
    nutrition_stats = analyze_nutrition_data_quality(df)
    source_stats = analyze_data_sources(df)
    category_stats, subcategory_stats = analyze_categories(df)
    quality_scores = analyze_data_quality_scores(df)
    missing_stats = analyze_missing_critical_data(df)
    llm_stats = analyze_llm_enhancement_potential(df)
    
    # Generate summary
    generate_summary_report(df, completeness_stats, nutrition_stats, source_stats, 
                          category_stats, quality_scores, missing_stats, llm_stats)
    
    print(f"\n🎉 Analysis complete!")

if __name__ == "__main__":
    main()