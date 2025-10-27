#!/usr/bin/env python3
"""
ThinkOrSwim Script Setup and Validation Tool
Based on previous_high_low.csv data analysis

This script helps users prepare and validate ThinkOrSwim scripts
before importing them into the platform.
"""

import os
import sys
import re
from datetime import datetime

def validate_script_syntax(script_content):
    """Validate basic ThinkOrSwim script syntax"""
    errors = []
    warnings = []
    
    # Check for required declarations
    if 'declare lower;' not in script_content:
        errors.append("Missing 'declare lower;' declaration")
    
    # Check for input parameters
    if 'input ' not in script_content:
        warnings.append("No input parameters found - script may be hardcoded")
    
    # Check for plot statements
    if 'plot(' not in script_content:
        warnings.append("No plot statements found - script may not display anything")
    
    # Check for common ThinkOrSwim functions
    required_functions = ['def ', 'if ', 'else']
    for func in required_functions:
        if func not in script_content:
            warnings.append(f"Missing common ThinkOrSwim syntax: {func}")
    
    return errors, warnings

def extract_script_info(script_content):
    """Extract key information from the script"""
    info = {
        'name': 'Unknown',
        'description': 'No description found',
        'inputs': [],
        'plots': [],
        'alerts': False
    }
    
    # Extract script name from comment
    name_match = re.search(r'//\s*(.+?)\s*Script', script_content)
    if name_match:
        info['name'] = name_match.group(1).strip()
    
    # Extract description
    desc_match = re.search(r'//\s*(.+?)\n', script_content)
    if desc_match:
        info['description'] = desc_match.group(1).strip()
    
    # Extract input parameters
    input_matches = re.findall(r'input\s+(\w+)\s*=\s*([^;]+);\s*//\s*(.+)', script_content)
    for match in input_matches:
        info['inputs'].append({
            'name': match[0],
            'default': match[1].strip(),
            'description': match[2].strip()
        })
    
    # Extract plot statements
    plot_matches = re.findall(r'plot\([^,]+,\s*"([^"]+)"', script_content)
    info['plots'] = plot_matches
    
    # Check for alerts
    if 'Alert(' in script_content:
        info['alerts'] = True
    
    return info

def generate_installation_guide(script_info):
    """Generate installation guide for the script"""
    guide = f"""
=== Installation Guide for {script_info['name']} ===

1. COPY SCRIPT CONTENT:
   - Open the .ts file in a text editor
   - Copy all content (Ctrl+A, Ctrl+C)

2. IMPORT INTO THINKORSWIM:
   - Open ThinkOrSwim Desktop
   - Go to Charts → Studies → Edit Studies
   - Click "Import" button
   - Paste the script content
   - Click "OK" to save

3. APPLY TO CHART:
   - Open a chart for your symbol
   - Go to Studies → Add Study
   - Find "{script_info['name']}" in the list
   - Click "Add" to apply

4. CONFIGURE PARAMETERS:
"""
    
    for input_param in script_info['inputs']:
        guide += f"   - {input_param['name']}: {input_param['description']} (Default: {input_param['default']})\n"
    
    guide += f"""
5. VERIFY DISPLAY:
   - Check that {len(script_info['plots'])} plot(s) are visible: {', '.join(script_info['plots'])}
   - {'Alerts are enabled' if script_info['alerts'] else 'No alerts configured'}
"""
    
    return guide

def main():
    """Main function to validate and prepare scripts"""
    print("ThinkOrSwim Script Setup and Validation Tool")
    print("=" * 50)
    
    # List available scripts
    script_files = [
        'thinkorswim_previous_high_low_script.ts',
        'thinkorswim_advanced_previous_high_low.ts'
    ]
    
    print("\nAvailable scripts:")
    for i, script_file in enumerate(script_files, 1):
        print(f"{i}. {script_file}")
    
    print("\nValidating scripts...")
    
    for script_file in script_files:
        if not os.path.exists(script_file):
            print(f"\n❌ ERROR: {script_file} not found!")
            continue
        
        print(f"\n📋 Validating {script_file}...")
        
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate syntax
            errors, warnings = validate_script_syntax(content)
            
            if errors:
                print(f"❌ ERRORS found:")
                for error in errors:
                    print(f"   - {error}")
            else:
                print("✅ No syntax errors found")
            
            if warnings:
                print(f"⚠️  WARNINGS:")
                for warning in warnings:
                    print(f"   - {warning}")
            
            # Extract and display script info
            info = extract_script_info(content)
            print(f"\n📊 Script Information:")
            print(f"   Name: {info['name']}")
            print(f"   Description: {info['description']}")
            print(f"   Input Parameters: {len(info['inputs'])}")
            print(f"   Plot Elements: {len(info['plots'])}")
            print(f"   Alerts: {'Yes' if info['alerts'] else 'No'}")
            
            # Generate installation guide
            guide = generate_installation_guide(info)
            print(f"\n📖 Installation Guide:")
            print(guide)
            
        except Exception as e:
            print(f"❌ ERROR reading {script_file}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("\nNext Steps:")
    print("1. Review the validation results above")
    print("2. Follow the installation guides for each script")
    print("3. Test the scripts on a paper trading account first")
    print("4. Adjust parameters based on your trading style")
    print("\nFor support, refer to the README_ThinkOrSwim_Scripts.md file")

if __name__ == "__main__":
    main()