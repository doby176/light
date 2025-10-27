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
    public class OrderBlockDrawings : Indicator
    {
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Detector with Drawing Objects";
                Name = "Order Block Drawings";
                Calculate = Calculate.OnBarClose;
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 3) return;

            double prevHigh = High[1];
            double prevClose = Close[1];
            double prevOpen = Open[1];
            
            // Inefficiency check
            bool inefficiency = Math.Abs(prevHigh - Low[0]) > Math.Abs(prevClose - prevOpen) * 1.5;

            // Break of structure
            double highestHigh3 = Math.Max(Math.Max(High[1], High[2]), High[3]);
            bool bosUp = High[0] > highestHigh3;

            // Order block detection
            bool isOrderBlock = inefficiency && bosUp;

            if (isOrderBlock)
            {
                // Draw a circle at the order block level
                Draw.Circle(this, "OBCircle" + CurrentBar, false, 3, prevOpen, Brushes.LightGreen, Brushes.LightGreen, 5);
                
                // Draw a horizontal line extending from the order block
                Draw.Line(this, "OBLine" + CurrentBar, false, 3, prevOpen, CurrentBar + 10, prevOpen, Brushes.LightGreen, DashStyleHelper.Solid, 2);
                
                // Add text label
                Draw.Text(this, "OBText" + CurrentBar, false, "OB", 3, prevOpen + (High[0] - Low[0]) * 0.1, Brushes.LightGreen);
            }
        }
    }
}