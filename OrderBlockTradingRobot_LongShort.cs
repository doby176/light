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

namespace NinjaTrader.NinjaScript.Strategies
{
    public class OrderBlockTradingRobot : Strategy
    {
        private Series<double> activeOrderBlockLevel;
        private Series<bool> waitingForNextGreen;
        private Series<bool> showGreenDot;
        private Series<bool> redDotSignal;
        private Series<bool> greenDotSignal;
        private bool shortPositionOpen = false;
        private bool longPositionOpen = false;
        private double stopLossLevel = 0;
        private bool waitingForGreenDotExit = false;
        private bool justEntered = false; // Flag to prevent immediate exit
        private bool entryProcessed = false; // Flag to prevent multiple entries

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Long/Short Cycle";
                Name = "Order Block Trading Robot";
                Calculate = Calculate.OnBarClose; // Candle close calculation
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
                IsInstantiatedOnEachOptimizationIteration = true;
            }
            else if (State == State.Configure)
            {
                // Initialize series
                activeOrderBlockLevel = new Series<double>(this);
                waitingForNextGreen = new Series<bool>(this);
                showGreenDot = new Series<bool>(this);
                redDotSignal = new Series<bool>(this);
                greenDotSignal = new Series<bool>(this);
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 3) return;

            // Reset entry flag on new bar
            if (CurrentBar > 0)
            {
                entryProcessed = false; // Reset entry flag on new bar
            }

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

            // Check if price closed below the active order block (for short entry)
            bool closedBelowOrderBlock = false;
            if (CurrentBar > 0 && activeOrderBlockLevel[1] != double.NaN && Close[0] < activeOrderBlockLevel[1] && !longPositionOpen)
            {
                closedBelowOrderBlock = true;
                waitingForNextGreen[0] = true;
                redDotSignal[0] = true; // Signal for short entry
            }
            else
            {
                redDotSignal[0] = false;
                if (CurrentBar > 0)
                {
                    waitingForNextGreen[0] = waitingForNextGreen[1];
                }
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
                    greenDotSignal[0] = true; // Signal for exit/entry
                }
                else
                {
                    showGreenDot[0] = false;
                    greenDotSignal[0] = false;
                }
            }
            else
            {
                activeOrderBlockLevel[0] = activeOrderBlockLevel[1];
                showGreenDot[0] = false;
                greenDotSignal[0] = false;
            }

            // Trading Logic
            if (State == State.Realtime || State == State.Historical)
            {
                // Entry Logic: Go short on red dot signal (first entry)
                if (redDotSignal[0] && !shortPositionOpen && !longPositionOpen && !entryProcessed)
                {
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    entryProcessed = true; // Prevent multiple entries
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Exit short and enter long when green dot signal appears
                if (greenDotSignal[0] && shortPositionOpen && waitingForGreenDotExit && !justEntered)
                {
                    stopLossLevel = activeOrderBlockLevel[0];
                    ExitShort(DefaultQuantity, "Exit Short on Green Dot", "Short on Red Dot");
                    shortPositionOpen = false;
                    waitingForGreenDotExit = false;
                    justEntered = true; // Set flag to prevent immediate exit
                    entryProcessed = true; // Prevent multiple entries
                    Print("SHORT EXIT: Green dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Enter long immediately after short exit
                    EnterLong(DefaultQuantity, "Long on Green Dot");
                    longPositionOpen = true;
                    Print("LONG ENTRY: Entering long after short exit at " + Time[0] + " Price: " + Close[0]);
                }

                // Exit long and enter short when green dot signal appears (same as short exit)
                if (greenDotSignal[0] && longPositionOpen && !justEntered)
                {
                    ExitLong(DefaultQuantity, "Exit Long on Green Dot", "Long on Green Dot");
                    longPositionOpen = false;
                    justEntered = true; // Set flag to prevent immediate exit
                    entryProcessed = true; // Prevent multiple entries
                    Print("LONG EXIT: Green dot signal at " + Time[0] + " Price: " + Close[0]);
                    
                    // Enter short immediately after long exit
                    EnterShort(DefaultQuantity, "Short on Green Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    Print("SHORT ENTRY: Entering short after long exit at " + Time[0] + " Price: " + Close[0]);
                }

                // Reset the justEntered flag after the first bar
                if (justEntered)
                {
                    justEntered = false;
                }
            }
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (execution.Order.OrderState == OrderState.Filled)
            {
                if (marketPosition == MarketPosition.Short)
                {
                    Print("SHORT FILLED: " + quantity + " contracts at " + price + " at " + time);
                }
                else if (marketPosition == MarketPosition.Long)
                {
                    Print("LONG FILLED: " + quantity + " contracts at " + price + " at " + time);
                }
                else if (marketPosition == MarketPosition.Flat)
                {
                    Print("POSITION CLOSED: " + quantity + " contracts at " + price + " at " + time);
                }
            }
        }
    }
}