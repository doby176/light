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
    public class OrderBlockTradingRobot3 : Strategy
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
        private bool waitingForRedDotExit = false;
        private bool waitingForShortEntry = false;
        private bool justEntered = false; // Flag to prevent immediate exit

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Long on Green Dots, Stop on Opposite Signals";
                Name = "Order Block Trading FINAL";
                Calculate = Calculate.OnPriceChange; // Changed to OnPriceChange for real-time exit
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
                    greenDotSignal[0] = true; // Signal for stop loss
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

            // Trading Logic - Entry and Exit
            if (State == State.Realtime || State == State.Historical)
            {
                // Entry Logic: Go short on red dot signal (only on bar close)
                if (redDotSignal[0] && !shortPositionOpen && !longPositionOpen && IsFirstTickOfBar)
                {
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Delayed short entry after long position exit
                if (waitingForShortEntry && IsFirstTickOfBar)
                {
                    EnterShort(DefaultQuantity, "Short on Red Dot (Delayed)");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    waitingForShortEntry = false;
                    justEntered = true; // Set flag to prevent immediate exit
                    Print("SHORT ENTRY: Delayed entry after long exit at " + Time[0] + " Price: " + Close[0]);
                }

                // Entry Logic: Go long when stopped out on green dot (real-time)
                if (greenDotSignal[0] && shortPositionOpen && waitingForGreenDotExit && !justEntered)
                {
                    stopLossLevel = activeOrderBlockLevel[0];
                    ExitShort(DefaultQuantity, "Real-time Stop on Green Dot", "Short on Red Dot");
                    shortPositionOpen = false;
                    waitingForGreenDotExit = false;
                    Print("REAL-TIME STOP LOSS: Green dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Immediately enter long position
                    EnterLong(DefaultQuantity, "Long on Green Dot");
                    longPositionOpen = true;
                    waitingForRedDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    Print("LONG ENTRY: Green dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Exit Logic: Exit long when red dot forms in real-time
                if (longPositionOpen && waitingForRedDotExit && !justEntered && CurrentBar >= 3)
                {
                    double prevHigh = High[1];
                    double prevClose = Close[1];
                    double prevOpen = Open[1];
                    
                    // Real-time inefficiency check using current bar's low
                    bool inefficiency = Math.Abs(prevHigh - Low[0]) > Math.Abs(prevClose - prevOpen) * 1.5;

                    // Real-time break of structure using current bar's high
                    double highestHigh3 = Math.Max(Math.Max(High[1], High[2]), High[3]);
                    bool bosUp = High[0] > highestHigh3;

                    // Real-time order block detection
                    bool isOrderBlock = inefficiency && bosUp;

                    // Check if we were waiting for the next red dot (price closed above order block)
                    bool wasWaitingForRed = CurrentBar > 0 && activeOrderBlockLevel[1] != double.NaN && Close[1] > activeOrderBlockLevel[1];

                    // If red dot forms in real-time, exit immediately
                    if (isOrderBlock && wasWaitingForRed)
                    {
                        stopLossLevel = prevOpen;
                        ExitLong(DefaultQuantity, "Real-time Stop on Red Dot", "Long on Green Dot");
                        longPositionOpen = false;
                        waitingForRedDotExit = false;
                        Print("REAL-TIME STOP LOSS: Red dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                        
                        // Set flag to enter short on next bar close (not immediately)
                        waitingForShortEntry = true;
                    }
                }

                // Reset the justEntered flag after the first tick of the next bar
                if (justEntered && IsFirstTickOfBar)
                {
                    justEntered = false;
                }
            }
        }

        // OnMarketData method - kept for compatibility but exit logic moved to OnBarUpdate
        protected override void OnMarketData(MarketDataEventArgs marketDataUpdate)
        {
            // Exit logic is now handled in OnBarUpdate with Calculate.OnPriceChange
            // This method is kept for any future real-time enhancements
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