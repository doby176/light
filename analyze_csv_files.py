#!/usr/bin/env python3
"""
ThinkorSwim Trading Analysis Tool - CSV File Version
Reads directly from your CSV files
"""

from trading_analysis import TradingAnalyzer
import os

def main():
    print("🎯 ThinkorSwim Trading Analysis Tool - CSV Version")
    print("=" * 60)
    
    # File paths - update these to match your actual file names
    base_path = r"C:\Users\ASUS"
    long_file = os.path.join(base_path, "StrategyReports_QQQ_8225long1.csv").replace('/', '\\')
    short_file = os.path.join(base_path, "StrategyReports_QQQ_8225short.csv").replace('/', '\\')
    
    print(f"📁 Looking for files:")
    print(f"   Long strategy: {long_file}")
    print(f"   Short strategy: {short_file}")
    print("=" * 60)
    
    # Check if files exist
    if not os.path.exists(long_file):
        print(f"❌ Long strategy file not found: {long_file}")
        return
    
    if not os.path.exists(short_file):
        print(f"❌ Short strategy file not found: {short_file}")
        return
    
    print("✅ Files found! Starting analysis...")
    
    try:
        # Create analyzer and load data
        analyzer = TradingAnalyzer()
        analyzer.load_data_from_files(long_file, short_file)
        
        if analyzer.combined_data.empty:
            print("❌ No valid data loaded. Check your CSV file format.")
            return
        
        # Calculate metrics
        metrics = analyzer.calculate_metrics()
        
        # Print summary
        analyzer.print_summary_report()
        
        # Generate plots
        print("\n📈 Generating visualizations...")
        analyzer.plot_cumulative_pnl()
        analyzer.plot_time_analysis()
        analyzer.plot_trade_distribution()
        
        # Save detailed report
        analyzer.save_detailed_report()
        
        print("\n🎉 Analysis Complete!")
        print("=" * 60)
        print("📁 Generated Files:")
        print("  • trading_analysis_report.txt - Detailed text report")
        print("  • Multiple PNG charts - Visual analysis")
        print("\n📊 Key Metrics Calculated:")
        print("  • Average Winner/Loser")
        print("  • Profit Factor")
        print("  • Max Drawdown")
        print("  • Sharpe/Sortino Ratios")
        print("  • Win/Loss Rates")
        print("  • Time-based Analysis")
        print("  • Strategy Comparison")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure your CSV files are in the correct ThinkorSwim format")
        print("2. Check that the file paths are correct")
        print("3. Ensure the files have the expected column headers")
        print("4. Verify all dependencies are installed: pip install pandas numpy matplotlib")

if __name__ == "__main__":
    main()