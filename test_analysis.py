#!/usr/bin/env python3
"""
Test script for trading analysis with realistic sample data
"""

from trading_analysis import TradingAnalyzer

def main():
    # More realistic sample data that matches ThinkorSwim format
    long_strategy_data = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:31 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$532.52;6/20/25 9:31 AM;;($43.00);100.0;
2;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$532.09;6/20/25 9:32 AM;($43.00);($43.00);0.0;
3;ORDERBLOCK(Long on Green Dot);Buy to Open;100.0;$533.15;6/20/25 9:45 AM;;$67.00;100.0;
4;ORDERBLOCK(Exit Long);Sell to Close;-100.0;$533.82;6/20/25 10:15 AM;$67.00;$24.00;0.0;
Total P/L: $1 326.97; Total order(s): 620;"""
    
    short_strategy_data = """Strategy report Symbol: QQQ Work Time: 6/20/25 9:32 AM - 8/1/25 3:59 PM
Id;Strategy;Side;Amount;Price;Date/Time;Trade P/L;P/L;Position;
1;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$532.09;6/20/25 9:32 AM;;($38.00);-100.0;
2;ORDERBLOCK(Exit Short);Buy to Close;100.0;$532.47;6/20/25 9:33 AM;($38.00);($38.00);0.0;
3;ORDERBLOCK(Short on Red Dot);Sell to Open;-100.0;$531.80;6/20/25 9:50 AM;;$45.00;-100.0;
4;ORDERBLOCK(Exit Short);Buy to Close;100.0;$531.35;6/20/25 10:20 AM;$45.00;$7.00;0.0;
Total P/L: ($843.03); Total order(s): 619;"""
    
    print("🧪 Testing Trading Analysis with Sample Data...")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = TradingAnalyzer()
    
    try:
        # Load data
        analyzer.load_data(long_strategy_data, short_strategy_data)
        
        # Generate comprehensive report
        analyzer.print_comprehensive_report()
        
        # Generate visualizations
        analyzer.generate_visualizations('test_analysis.png')
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()