#!/usr/bin/env python3
"""
Setup Batch Processing Folders and Standardized Naming
Creates organized folder structure for input/output CSV files
"""

import os
from datetime import datetime
import shutil

def setup_batch_folders():
    """Create standardized folder structure for batch processing"""
    
    print("📁 SETTING UP BATCH PROCESSING FOLDERS")
    print("=" * 50)
    
    # Create main batch folder
    batch_folder = "llm_batches"
    if not os.path.exists(batch_folder):
        os.makedirs(batch_folder)
        print(f"✅ Created main folder: {batch_folder}/")
    
    # Create subfolders
    subfolders = [
        "input",      # For input CSV files
        "output",     # For completed CSV files  
        "processed",  # For integrated files (archive)
        "templates"   # For prompt templates and guides
    ]
    
    for subfolder in subfolders:
        folder_path = os.path.join(batch_folder, subfolder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"✅ Created subfolder: {batch_folder}/{subfolder}/")
    
    return batch_folder

def create_batch_with_standard_naming(batch_size=200, batch_type="beverages"):
    """Create batch with standardized naming convention"""
    
    print(f"\n📋 CREATING STANDARDIZED BATCH")
    print("=" * 40)
    
    # Setup folders
    batch_folder = setup_batch_folders()
    
    # Generate timestamp for unique batch ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Standardized naming convention
    batch_id = f"{batch_type}_{batch_size}products_{timestamp}"
    
    input_filename = f"input_{batch_id}.csv"
    output_filename = f"output_{batch_id}.csv"
    
    input_path = os.path.join(batch_folder, "input", input_filename)
    output_path = os.path.join(batch_folder, "output", output_filename)
    
    print(f"🏷️  Batch ID: {batch_id}")
    print(f"📥 Input file: {input_path}")
    print(f"📤 Output file: {output_path}")
    
    # Create the batch CSV (reuse existing logic)
    from create_large_batch_csv import create_large_batch_csv
    
    # Generate batch CSV
    temp_file, count = create_large_batch_csv(batch_size=batch_size, focus_quality=True)
    
    # Move to standardized location
    shutil.move(temp_file, input_path)
    
    print(f"✅ Input CSV created: {input_path}")
    print(f"📊 Products: {count}")
    
    # Create processing instructions file
    instructions_file = os.path.join(batch_folder, "templates", f"instructions_{batch_id}.md")
    create_batch_instructions(instructions_file, batch_id, input_filename, output_filename)
    
    # Create output template
    create_output_template(output_path, input_path)
    
    return {
        'batch_id': batch_id,
        'input_file': input_path,
        'output_file': output_path,
        'instructions_file': instructions_file,
        'product_count': count
    }

def create_batch_instructions(instructions_file, batch_id, input_filename, output_filename):
    """Create batch-specific processing instructions"""
    
    instructions = f"""# Batch Processing Instructions

## 📋 Batch Details
- **Batch ID**: {batch_id}
- **Input File**: {input_filename}
- **Output File**: {output_filename}
- **Created**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 🎯 Processing Steps

### 1. Download Input File
- File location: `llm_batches/input/{input_filename}`
- Contains products with empty nutrition columns to fill

### 2. Process with LLM
- Use the prompt template in `llm_batches/templates/`
- Fill nutrition data for each product row
- Focus on accuracy and data quality

### 3. Upload Output File
- Save completed CSV as: `llm_batches/output/{output_filename}`
- Ensure all nutrition columns are filled
- Include confidence scores and data sources

### 4. Integration
- Share the output file location
- Integration script will process automatically
- Results will be shown with quality metrics

## 📊 Quality Requirements
- **Confidence ≥0.8**: Excellent (use official sources)
- **Confidence 0.6-0.8**: Good (reliable databases)
- **Confidence <0.6**: Skip (too uncertain)

## 🔄 File Naming Convention
- **Input**: `input_[category]_[count]products_[timestamp].csv`
- **Output**: `output_[category]_[count]products_[timestamp].csv`
- **Processed**: `processed_[category]_[count]products_[timestamp].csv`

## 📁 Folder Structure
```
llm_batches/
├── input/          # Input CSV files for processing
├── output/         # Completed CSV files from LLM
├── processed/      # Integrated files (archive)
└── templates/      # Instructions and prompt templates
```

## 🎯 Next Steps
1. Process the input CSV with your LLM
2. Save results as output CSV in the correct folder
3. Share the file path for integration
"""

    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Instructions created: {instructions_file}")

def create_output_template(output_path, input_path):
    """Create output template with proper structure"""
    
    # Read input file to get structure
    import pandas as pd
    
    try:
        input_df = pd.read_csv(input_path)
        
        # Create template with first few rows as examples
        template_df = input_df.head(3).copy()
        
        # Fill example data for first row
        if len(template_df) > 0:
            template_df.at[0, 'ingredients_list'] = "Carbonated Water, Sugar, Natural Flavors, Caramel Color"
            template_df.at[0, 'energy_kcal_per_100g'] = 42
            template_df.at[0, 'carbs_g_per_100g'] = 10.6
            template_df.at[0, 'total_sugars_g_per_100g'] = 10.6
            template_df.at[0, 'protein_g_per_100g'] = 0
            template_df.at[0, 'fat_g_per_100g'] = 0
            template_df.at[0, 'saturated_fat_g_per_100g'] = 0
            template_df.at[0, 'fiber_g_per_100g'] = 0
            template_df.at[0, 'sodium_mg_per_100g'] = 4
            template_df.at[0, 'salt_g_per_100g'] = 0.01
            template_df.at[0, 'serving_size'] = "250ml"
            template_df.at[0, 'servings_per_container'] = 3
            template_df.at[0, 'confidence_score'] = 0.85
            template_df.at[0, 'data_source'] = "Official brand website"
            template_df.at[0, 'processing_notes'] = "Indian formulation verified"
        
        # Save template (will be overwritten with actual results)
        template_path = output_path.replace('.csv', '_template.csv')
        template_df.to_csv(template_path, index=False)
        
        print(f"✅ Output template created: {template_path}")
        
    except Exception as e:
        print(f"⚠️  Could not create output template: {e}")

def copy_templates_to_batch_folder():
    """Copy prompt templates and guides to batch folder"""
    
    batch_folder = "llm_batches"
    templates_folder = os.path.join(batch_folder, "templates")
    
    # Files to copy
    template_files = [
        "external_llm_prompt_template.txt",
        "CSV_SHARING_GUIDE.md",
        "EXTERNAL_LLM_GUIDE.md"
    ]
    
    for file in template_files:
        if os.path.exists(file):
            dest_path = os.path.join(templates_folder, file)
            shutil.copy2(file, dest_path)
            print(f"✅ Copied template: {dest_path}")

def list_batch_files():
    """List all batch files in organized format"""
    
    print(f"\n📁 BATCH FILES OVERVIEW")
    print("=" * 40)
    
    batch_folder = "llm_batches"
    if not os.path.exists(batch_folder):
        print("❌ No batch folder found")
        return
    
    for subfolder in ["input", "output", "processed"]:
        folder_path = os.path.join(batch_folder, subfolder)
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
            print(f"\n📂 {subfolder.upper()} ({len(files)} files):")
            
            if files:
                for file in sorted(files):
                    file_path = os.path.join(folder_path, file)
                    size = os.path.getsize(file_path)
                    size_mb = size / (1024 * 1024)
                    print(f"   • {file} ({size_mb:.1f} MB)")
            else:
                print("   (empty)")

if __name__ == "__main__":
    print("🚀 BATCH PROCESSING SETUP")
    print("=" * 60)
    
    # Setup folder structure
    batch_info = create_batch_with_standard_naming(batch_size=200, batch_type="beverages")
    
    # Copy templates
    copy_templates_to_batch_folder()
    
    # Show overview
    list_batch_files()
    
    print(f"\n🎉 BATCH SETUP COMPLETE!")
    print("=" * 50)
    print(f"📋 Batch Details:")
    print(f"   Batch ID: {batch_info['batch_id']}")
    print(f"   Input file: {batch_info['input_file']}")
    print(f"   Output file: {batch_info['output_file']}")
    print(f"   Products: {batch_info['product_count']}")
    
    print(f"\n🔄 Next Steps:")
    print(f"   1. Process: {batch_info['input_file']}")
    print(f"   2. Save as: {batch_info['output_file']}")
    print(f"   3. Share the output file path")
    print(f"   4. Integration will happen automatically")
    
    print(f"\n📁 Folder Structure Created:")
    print(f"   llm_batches/input/     - Input CSV files")
    print(f"   llm_batches/output/    - Completed CSV files")
    print(f"   llm_batches/processed/ - Integrated files (archive)")
    print(f"   llm_batches/templates/ - Instructions and prompts")