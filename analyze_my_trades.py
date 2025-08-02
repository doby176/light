#!/usr/bin/env python3
"""
ThinkorSwim Trading Analysis Tool
Just paste your data and run!
"""

from trading_analysis import TradingAnalyzer

def main():
    print("🎯 ThinkorSwim Trading Analysis Tool")
    print("=" * 60)
    print("📋 Instructions:")
    print("1. Replace the sample data below with your actual ThinkorSwim reports")
    print("2. Run this script to get comprehensive analysis")
    print("3. Check the generated charts and metrics")
    print("=" * 60)
    
    # ========================================
    # 🔄 REPLACE THIS DATA WITH YOUR ACTUAL DATA
    # ========================================
    
    # Your Long Strategy Data (from ThinkorSwim)
    long_report = """
Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
3;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.47;6/20/25 9:33 AM;;$38.00;100.0;
4;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.85;6/20/25 9:34 AM;$38.00;$38.00;0.0;
Total P/L: $1 326.97; Total order(s): 620;
"""

    # Your Short Strategy Data (from ThinkorSwim)
    short_report = """
Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
3;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.85;6/20/25 9:34 AM;;$43.00;-100.0;
4;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.42;6/20/25 9:35 AM;$43.00;$43.00;0.0;
Total P/L: ($843.03); Total order(s): 619;
"""
    
    # ========================================
    # 🚀 DON'T CHANGE ANYTHING BELOW THIS LINE
    # ========================================
    
    try:
        print("\n📊 Parsing trading data...")
        analyzer = TradingAnalyzer()
        analyzer.load_data(long_report, short_report)
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
        print("1. Make sure your data is in the correct ThinkorSwim format")
        print("2. Check that you have all required columns")
        print("3. Verify the data includes the header line")
        print("4. Ensure all dependencies are installed: pip install pandas numpy matplotlib")

if __name__ == "__main__":
    main()