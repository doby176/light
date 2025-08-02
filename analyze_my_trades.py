#!/usr/bin/env python3
"""
Simple script to analyze your ThinkorSwim trading results
"""

from trading_analysis import TradingAnalyzer

def main():
    # Your actual trading data from ThinkorSwim
    long_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0; 2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0; Total P/L: $1 326.97; Total order(s): 620;"""
    
    short_report = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position; 1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0; 2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0; Total P/L: ($843.03); Total order(s): 619;"""
    
    print("🚀 Starting ThinkorSwim Trading Analysis...")
    print("=" * 60)
    
    # Create analyzer
    analyzer = TradingAnalyzer()
    
    try:
        # Load your data
        print("📊 Loading your trading data...")
        analyzer.load_data(long_report, short_report)
        
        # Calculate all metrics
        print("📈 Calculating performance metrics...")
        metrics = analyzer.calculate_basic_metrics()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 YOUR TRADING PERFORMANCE SUMMARY")
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
        analyzer.generate_visualizations("my_trading_analysis")
        
        # Generate detailed report
        print("\n📄 Generating detailed report...")
        analyzer.generate_report("my_trading_report.txt")
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        print("📁 Generated files:")
        print("   📊 my_trading_analysis_overview.png - Main visualizations")
        print("   📊 my_trading_analysis_monthly.png - Monthly performance")
        print("   📄 my_trading_report.txt - Detailed text report")
        print("\n🎉 Check these files for your complete trading analysis!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()