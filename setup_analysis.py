#!/usr/bin/env python3
"""
Setup script for ThinkorSwim Trading Analysis Tool
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    
    packages = [
        'pandas>=1.3.0',
        'numpy>=1.21.0', 
        'matplotlib>=3.4.0',
        'seaborn>=0.11.0'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_files():
    """Check if the required files exist"""
    print("\n📁 Checking for your CSV files...")
    
    base_path = r"C:\Users\ASUS"
    long_file = os.path.join(base_path, "StrategyReports_QQQ_8225long1.csv").replace('/', '\\')
    short_file = os.path.join(base_path, "StrategyReports_QQQ_8225short.csv").replace('/', '\\')
    
    print(f"Looking for:")
    print(f"  • {long_file}")
    print(f"  • {short_file}")
    
    long_exists = os.path.exists(long_file)
    short_exists = os.path.exists(short_file)
    
    if long_exists:
        print("✅ Long strategy file found")
    else:
        print("❌ Long strategy file not found")
    
    if short_exists:
        print("✅ Short strategy file found")
    else:
        print("❌ Short strategy file not found")
    
    return long_exists and short_exists

def main():
    print("🎯 ThinkorSwim Trading Analysis Tool - Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed. Please install dependencies manually:")
        print("pip install pandas numpy matplotlib seaborn")
        return
    
    print("\n✅ All dependencies installed successfully!")
    
    # Check for files
    files_exist = check_files()
    
    print("\n" + "=" * 50)
    print("🚀 Setup Complete!")
    print("=" * 50)
    
    if files_exist:
        print("\n📊 To run the analysis:")
        print("python3 analyze_csv_files.py")
        print("\n📊 To run with sample data:")
        print("python3 analyze_my_trades.py")
    else:
        print("\n📁 Please place your CSV files in C:\\Users\\ASUS\\")
        print("   Expected files:")
        print("   • StrategyReports_QQQ_8225long1.csv")
        print("   • StrategyReports_QQQ_8225short.csv")
        print("\n📊 Then run:")
        print("python3 analyze_csv_files.py")
    
    print("\n📚 For more information, see README_ANALYSIS.md")

if __name__ == "__main__":
    main()