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

//This namespace holds Indicators in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Indicators
{
    public class BullishOrderBlockIndicator : Indicator
    {
        private Series<double> bullishOrderBlockLevel;
        private Series<bool> isBullishOrderBlock;
        private Series<bool> bullishUnmitigated;
        private Series<double> inefficiency;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Bullish Order Block Indicator for QQQ Shares - 1-minute chart";
                Name = "Bullish Order Block Indicator";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                IsFillLimitOnTouch = false;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;
                OrderFillResolution = OrderFillResolution.Standard;
                Slippage = 0;
                StartBehavior = StartBehavior.WaitUntilFlat;
                TimeInForce = TimeInForce.Gtc;
                TraceOrders = false;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                BarsRequiredToTrade = 20;
                // Disable this property for performance gains in Strategy Analyzer optimizations
                // See the Help Guide for additional information
                IsInstantiatedOnEachOptimizationIteration = true;
            }
            else if (State == State.Configure)
            {
                // Add plot for Bullish Order Block
                AddPlot(new Stroke(Brushes.LightGreen, 3), PlotStyle.Point, "BullishOrderBlock");
                
                // Initialize series
                bullishOrderBlockLevel = new Series<double>(this);
                isBullishOrderBlock = new Series<bool>(this);
                bullishUnmitigated = new Series<bool>(this);
                inefficiency = new Series<double>(this);
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 3) return;

            // --- 1-Minute Data ---
            double close1 = Close[0];
            double open1 = Open[0];
            double high1 = High[0];
            double low1 = Low[0];

            // --- Bullish Order Block Detection (1-Minute Chart) ---
            // Inefficiency: Shadow gap > 1.5x candle body
            double prevHigh = High[1];
            double prevLow = Low[1];
            double prevClose = Close[1];
            double prevOpen = Open[1];
            
            inefficiency[0] = Math.Abs(prevHigh - low1) > Math.Abs(prevClose - prevOpen) * 1.5;

            // Bullish Break of Structure (BOS) and Change of Character (CHOCH)
            double highestHigh3 = Math.Max(Math.Max(High[1], High[2]), High[3]);
            double lowestLow3 = Math.Min(Math.Min(Low[1], Low[2]), Low[3]);
            
            bool bosUp = high1 > highestHigh3; // Breaks recent high
            bool chochUp = low1 < lowestLow3 && high1 > highestHigh3; // Higher high, lower low

            // Bullish Order Block
            isBullishOrderBlock[0] = (inefficiency[1] && (bosUp || chochUp)) && !double.IsNaN(prevClose);

            // Track Order Block Level (Single Line at Open)
            if (isBullishOrderBlock[0])
            {
                bullishOrderBlockLevel[0] = prevOpen;
            }
            else
            {
                bullishOrderBlockLevel[0] = double.NaN;
            }

            // Track Mitigation
            if (isBullishOrderBlock[0])
            {
                bullishUnmitigated[0] = true;
            }
            else if (close1 < prevLow && isBullishOrderBlock[1])
            {
                bullishUnmitigated[0] = false;
            }
            else if (CurrentBar > 0)
            {
                bullishUnmitigated[0] = bullishUnmitigated[1];
            }

            // --- Plot Single Line on Order Block Candle ---
            if (isBullishOrderBlock[0] && bullishUnmitigated[0])
            {
                Values[0][0] = bullishOrderBlockLevel[0];
            }
            else
            {
                Values[0][0] = double.NaN;
            }

            // --- Alert for Bullish Order Block ---
            if (isBullishOrderBlock[0] && bullishUnmitigated[0])
            {
                Alert("BullishOrderBlock", Priority.High, "Bullish Order Block Detected", "Alert1.wav", 10, Brushes.LightGreen, Brushes.White);
            }
        }
    }
}