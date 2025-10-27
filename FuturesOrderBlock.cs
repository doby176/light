#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class FuturesOrderBlock : Indicator
    {
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Futures Order Block Detector";
                Name = "Futures Order Block";
                Calculate = Calculate.OnBarClose;
                BarsRequiredToTrade = 20;
            }
            else if (State == State.Configure)
            {
                AddPlot(new Stroke(Brushes.LightGreen, 3), PlotStyle.Point, "OrderBlock");
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 3) return;

            double prevHigh = High[1];
            double prevLow = Low[1];
            double prevClose = Close[1];
            double prevOpen = Open[1];
            
            // Inefficiency check
            bool inefficiency = Math.Abs(prevHigh - Low[0]) > Math.Abs(prevClose - prevOpen) * 1.5;

            // Break of structure
            double highestHigh3 = Math.Max(Math.Max(High[1], High[2]), High[3]);
            bool bosUp = High[0] > highestHigh3;

            // Order block detection
            bool isOrderBlock = inefficiency && bosUp && !double.IsNaN(prevClose);

            if (isOrderBlock)
            {
                Values[0][0] = prevOpen;
                Alert("FuturesOrderBlock", Priority.High, "Futures Order Block Detected", "Alert1.wav", 10, Brushes.LightGreen, Brushes.White);
            }
            else
            {
                Values[0][0] = double.NaN;
            }
        }
    }
}