#!/usr/bin/env python3
"""
Easy ThinkorSwim Data Analysis Tool
Just paste your data and run!
"""

from trading_analysis import TradingAnalyzer

def main():
    print("🎯 ThinkorSwim Trading Analysis Tool")
    print("=" * 50)
    print("📋 Instructions:")
    print("1. Copy your ThinkorSwim strategy reports below")
    print("2. Replace the sample data with your actual data")
    print("3. Run this script to get comprehensive analysis")
    print("=" * 50)
    
    # ========================================
    # 🔄 REPLACE THIS DATA WITH YOUR ACTUAL DATA
    # ========================================
    
    # Your Long Strategy Data (from ThinkorSwim)
    long_strategy_data = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
3;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.47;6/20/25 9:33 AM;;$38.00;100.0;
4;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.85;6/20/25 9:34 AM;$38.00;$38.00;0.0;
Total P/L: $1 326.97; Total order(s): 620;"""

    # Your Short Strategy Data (from ThinkorSwim)
    short_strategy_data = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
3;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.85;6/20/25 9:34 AM;;$43.00;-100.0;
4;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.42;6/20/25 9:35 AM;$43.00;$43.00;0.0;
Total P/L: ($843.03); Total order(s): 619;"""
    
    # ========================================
    # 🚀 DON'T CHANGE ANYTHING BELOW THIS LINE
    # ========================================
    
    print("\n🚀 Starting Analysis...")
    
    # Create analyzer
    analyzer = TradingAnalyzer()
    
    try:
        # Load your data
        analyzer.load_data(long_strategy_data, short_strategy_data)
        
        # Generate comprehensive report
        print("\n📊 Generating Analysis Report...")
        analyzer.generate_report("my_trading_analysis_report.txt")
        
        # Generate visualizations
        print("\n📈 Generating Visualizations...")
        analyzer.generate_plots("my_trading_analysis_plots.png")
        
        print("\n✅ Analysis Complete!")
        print("=" * 50)
        print("📁 Your Results:")
        print("  • my_trading_analysis_report.txt - Detailed metrics")
        print("  • my_trading_analysis_plots.png - Visual charts")
        print("\n📊 What You'll Get:")
        print("  • Average Winner/Loser")
        print("  • Profit Factor")
        print("  • Max Drawdown")
        print("  • Cumulative P&L")
        print("  • Time-based Analysis")
        print("  • Risk Metrics")
        print("  • Strategy Comparison")
        print("  • And much more!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure your data is in the correct ThinkorSwim format")
        print("2. Check that you have all required columns")
        print("3. Verify the data includes the header line")
        print("4. Ensure all dependencies are installed: pip install pandas numpy matplotlib seaborn")

if __name__ == "__main__":
    main()