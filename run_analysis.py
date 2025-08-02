#!/usr/bin/env python3
"""
Simple script to run ThinkorSwim trading analysis
"""

from trading_analysis import TradingAnalyzer

def main():
    # Your actual ThinkorSwim data (replace with your real data)
    long_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
3;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.47;6/20/25 9:33 AM;;$38.00;100.0;
4;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.85;6/20/25 9:34 AM;$38.00;$38.00;0.0;
Total P/L: $1 326.97; Total order(s): 620;"""

    short_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
3;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.85;6/20/25 9:34 AM;;$43.00;-100.0;
4;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.42;6/20/25 9:35 AM;$43.00;$43.00;0.0;
Total P/L: ($843.03); Total order(s): 619;"""

    # Create analyzer
    analyzer = TradingAnalyzer()
    
    print("🚀 Starting ThinkorSwim Trading Analysis...")
    print("=" * 60)
    
    try:
        # Load your data
        analyzer.load_data(long_report, short_report)
        
        # Generate comprehensive report
        print("\n📊 Generating Analysis Report...")
        analyzer.generate_report("trading_analysis_report.txt")
        
        # Generate visualizations
        print("\n📈 Generating Visualizations...")
        analyzer.generate_plots("trading_analysis_plots.png")
        
        print("\n✅ Analysis Complete!")
        print("=" * 60)
        print("📁 Generated Files:")
        print("  • trading_analysis_report.txt - Detailed text report")
        print("  • trading_analysis_plots.png - Comprehensive charts")
        print("\n📋 Key Metrics Calculated:")
        print("  • Average Winner/Loser")
        print("  • Profit Factor")
        print("  • Max Drawdown")
        print("  • Cumulative P&L")
        print("  • Time-based Analysis")
        print("  • Risk Metrics (Sharpe, Sortino, Calmar)")
        print("  • Win/Loss Streaks")
        print("  • Strategy Comparison")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 To use your own data:")
        print("1. Replace the long_report and short_report variables")
        print("2. Make sure your data follows the ThinkorSwim format")
        print("3. Run the script again")

if __name__ == "__main__":
    main()