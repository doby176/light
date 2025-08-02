#!/usr/bin/env python3
"""
Test script with realistic sample data to demonstrate the trading analysis
"""

from trading_analysis import TradingAnalyzer

def main():
    # Realistic sample data that matches ThinkorSwim format
    long_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
3;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$533.15;6/20/25 9:45 AM;;$67.00;100.0;
4;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$533.82;6/20/25 10:15 AM;$67.00;$24.00;0.0;
5;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$534.20;6/20/25 10:30 AM;;($28.00);100.0;
6;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$533.92;6/20/25 10:45 AM;($28.00);($4.00);0.0;
7;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$535.10;6/20/25 11:00 AM;;$89.00;100.0;
8;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$535.99;6/20/25 11:30 AM;$89.00;$85.00;0.0;
Total P/L: $1,326.97; Total order(s): 620;"""
    
    short_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
3;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$533.82;6/20/25 10:15 AM;;$45.00;-100.0;
4;ORDERBLOCK(Exit Short);Buy to Close;100.0;$533.37;6/20/25 10:20 AM;$45.00;$7.00;0.0;
5;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$533.92;6/20/25 10:45 AM;;($15.00);-100.0;
6;ORDERBLOCK(Exit Short);Buy to Close;100.0;$534.07;6/20/25 11:00 AM;($15.00);($8.00);0.0;
7;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$535.99;6/20/25 11:30 AM;;($22.00);-100.0;
8;ORDERBLOCK(Exit Short);Buy to Close;100.0;$536.21;6/20/25 11:45 AM;($22.00);($30.00);0.0;
Total P/L: ($843.03); Total order(s): 619;"""
    
    print("🚀 Testing ThinkorSwim Trading Analysis with Sample Data...")
    print("=" * 60)
    
    # Create analyzer
    analyzer = TradingAnalyzer()
    
    try:
        # Load sample data
        print("📊 Loading sample trading data...")
        analyzer.load_data(long_report, short_report)
        
        # Calculate all metrics
        print("📈 Calculating performance metrics...")
        metrics = analyzer.calculate_basic_metrics()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 SAMPLE TRADING PERFORMANCE SUMMARY")
        print("="*60)
        
        for strategy in ['long', 'short', 'combined']:
            print(f"\n🎯 {strategy.upper()} STRATEGY:")
            m = metrics[strategy]
            print(f"   📊 Total Trades: {m['total_trades']}")
            print(f"   ✅ Win Rate: {m['win_rate']:.2%}")
            print(f"   💰 Total P&L: ${m['total_pl']:,.2f}")
            print(f"   📈 Average Winner: ${m['average_winner']:,.2f}")
            print(f"   📉 Average Loser: ${m['average_loser']:,.2f}")
            print(f"   🔥 Profit Factor: {m['profit_factor']:.2f}")
            print(f"   📊 Max Drawdown: ${m['max_drawdown']:,.2f}")
            print(f"   📈 Sharpe Ratio: {m['sharpe_ratio']:.2f}")
            print(f"   🔥 Max Consecutive Wins: {m['max_consecutive_wins']}")
            print(f"   📉 Max Consecutive Losses: {m['max_consecutive_losses']}")
        
        # Generate visualizations
        print("\n📊 Generating comprehensive visualizations...")
        analyzer.generate_visualizations("sample_trading_analysis")
        
        # Generate detailed report
        print("\n📄 Generating detailed report...")
        analyzer.generate_report("sample_trading_report.txt")
        
        print("\n" + "="*60)
        print("✅ SAMPLE ANALYSIS COMPLETE!")
        print("="*60)
        print("📁 Generated files:")
        print("   📊 sample_trading_analysis_overview.png - Main visualizations")
        print("   📊 sample_trading_analysis_monthly.png - Monthly performance")
        print("   📄 sample_trading_report.txt - Detailed text report")
        print("\n🎉 The analysis tool is working! Now you can use it with your real data.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()