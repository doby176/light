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
    public class OrderBlockWithRedDots : Indicator
    {
        private Series<double> activeOrderBlockLevel;
        private Series<bool> waitingForNextGreen;
        private Series<bool> showGreenDot;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block with Red Dots - Shows next green dot after close below";
                Name = "Order Block with Red Dots";
                Calculate = Calculate.OnBarClose;
                IsOverlay = true;
            }
            else if (State == State.Configure)
            {
                // Green dots for order blocks
                AddPlot(new Stroke(Brushes.Lime, 8), PlotStyle.Dot, "GreenOrderBlock");
                // Red dots for close below
                AddPlot(new Stroke(Brushes.Red, 8), PlotStyle.Dot, "RedCloseBelow");
                
                // Initialize series
                activeOrderBlockLevel = new Series<double>(this);
                waitingForNextGreen = new Series<bool>(this);
                showGreenDot = new Series<bool>(this);
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

            // Check if price closed below the active order block
            bool closedBelowOrderBlock = false;
            if (CurrentBar > 0 && activeOrderBlockLevel[1] != double.NaN && Close[0] < activeOrderBlockLevel[1])
            {
                closedBelowOrderBlock = true;
                waitingForNextGreen[0] = true;
            }
            else if (CurrentBar > 0)
            {
                waitingForNextGreen[0] = waitingForNextGreen[1];
            }

            // Handle order block level tracking
            if (isOrderBlock)
            {
                activeOrderBlockLevel[0] = prevOpen;
                
                // Show green dot only if we're waiting for the next one after a close below
                if (waitingForNextGreen[0])
                {
                    showGreenDot[0] = true;
                    waitingForNextGreen[0] = false; // Reset the waiting flag
                }
                else
                {
                    showGreenDot[0] = false;
                }
            }
            else
            {
                activeOrderBlockLevel[0] = activeOrderBlockLevel[1];
                showGreenDot[0] = false;
            }

            // Plot green dots (only when showGreenDot is true)
            if (showGreenDot[0])
            {
                Values[0][0] = prevOpen;
            }
            else
            {
                Values[0][0] = double.NaN;
            }

            // Plot red dots (when price closes below order block)
            if (closedBelowOrderBlock)
            {
                Values[1][0] = activeOrderBlockLevel[1]; // Red dot at the order block level
            }
            else
            {
                Values[1][0] = double.NaN;
            }
        }
    }
}