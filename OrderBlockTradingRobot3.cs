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
        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Max Daily Profit", Description = "Maximum daily profit before stopping trading", Order = 1, GroupName = "Max Profit")]
        public double MaxDailyProfit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Max Profit", Description = "Enable maximum daily profit feature", Order = 2, GroupName = "Max Profit")]
        public bool EnableMaxProfit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Trailing Stop", Description = "Enable trailing stop feature", Order = 1, GroupName = "Trailing Stop")]
        public bool EnableTrailingStop { get; set; }

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

        private bool justEntered = false; // Flag to prevent immediate exit
        private bool maxProfitReached = false; // Flag to stop trading when max profit is reached
        private DateTime lastTradeDate = DateTime.MinValue; // Track the last trade date
        private double trailStopLevel = 0; // Current trailing stop level
        private bool trailStopSet = false; // Flag to track if trailing stop is active

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Long on Green Dots, Stop on Opposite Signals";
                Name = "Order Block Trading FINAL";
                Calculate = Calculate.OnPriceChange; // Keep OnPriceChange for real-time short exit
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
                
                // Max Profit Parameters
                MaxDailyProfit = 1000; // Maximum daily profit in currency units
                EnableMaxProfit = true; // Enable/disable max profit feature
                
                // Trailing Stop Parameters
                EnableTrailingStop = true; // Enable/disable trailing stop feature
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

            // Check if it's a new trading day and reset max profit flag
            if (lastTradeDate.Date != Time[0].Date)
            {
                maxProfitReached = false;
                lastTradeDate = Time[0].Date;
                Print("NEW TRADING DAY: Resetting max profit flag");
            }

            // Check if max profit has been reached and stop trading
            if (EnableMaxProfit && maxProfitReached)
            {
                return; // Stop all trading logic
            }

            // Trailing Stop Logic
            if (EnableTrailingStop && trailStopSet)
            {
                UpdateTrailingStop();
                CheckTrailingStop();
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
                    
                    // Initialize trailing stop for short position
                    if (EnableTrailingStop)
                    {
                        InitializeTrailingStop();
                    }
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

                // Exit Logic: Exit long when red dot signal appears (only on candle close)
                if (redDotSignal[0] && longPositionOpen && waitingForRedDotExit && !justEntered && IsFirstTickOfBar)
                {
                    stopLossLevel = activeOrderBlockLevel[0];
                    ExitLong(DefaultQuantity, "Stop on Red Dot", "Long on Green Dot");
                    longPositionOpen = false;
                    waitingForRedDotExit = false;
                    Print("STOP LOSS: Red dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Immediately enter short position
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
                    
                    // Initialize trailing stop for short position
                    if (EnableTrailingStop)
                    {
                        InitializeTrailingStop();
                    }
                }

                // Reset the justEntered flag after the first tick of the next bar
                if (justEntered && IsFirstTickOfBar)
                {
                    justEntered = false;
                }
            }
        }

        // Real-time exit method for short position
        protected override void OnMarketData(MarketDataEventArgs marketDataUpdate)
        {
            // Check if max profit has been reached and stop trading
            if (EnableMaxProfit && maxProfitReached)
            {
                return; // Stop all trading logic
            }

            // Check trailing stop in real-time
            if (EnableTrailingStop && trailStopSet)
            {
                CheckTrailingStop();
            }

            // Check for max profit on unrealized gains
            if (EnableMaxProfit && !maxProfitReached && Position.MarketPosition != MarketPosition.Flat)
            {
                double dailyProfit = GetDailyProfit();
                if (dailyProfit >= MaxDailyProfit)
                {
                    maxProfitReached = true;
                    Print("MAX DAILY PROFIT REACHED (UNREALIZED): " + dailyProfit + " >= " + MaxDailyProfit + " - STOPPING TRADING FOR THE DAY");
                    
                    // Close any open position
                    if (Position.MarketPosition == MarketPosition.Short)
                    {
                        ExitShort(DefaultQuantity, "Max Profit Exit", "Short on Red Dot");
                    }
                    else if (Position.MarketPosition == MarketPosition.Long)
                    {
                        ExitLong(DefaultQuantity, "Max Profit Exit", "Long on Green Dot");
                    }
                    return;
                }
            }

            // Only check for real-time exits if we have a short position
            if (shortPositionOpen && waitingForGreenDotExit && !justEntered && CurrentBar >= 3)
            {
                // Check if green dot conditions are met in real-time
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

                // If green dot forms in real-time, exit immediately
                if (isOrderBlock && waitingForNextGreen[0])
                {
                    stopLossLevel = prevOpen;
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
                    
                    // Initialize trailing stop for long position
                    if (EnableTrailingStop)
                    {
                        InitializeTrailingStop();
                    }
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
                    
                    // Check if max profit has been reached after position close
                    if (EnableMaxProfit && !maxProfitReached)
                    {
                        double dailyProfit = GetDailyProfit();
                        if (dailyProfit >= MaxDailyProfit)
                        {
                            maxProfitReached = true;
                            Print("MAX DAILY PROFIT REACHED: " + dailyProfit + " >= " + MaxDailyProfit + " - STOPPING TRADING FOR THE DAY");
                        }
                    }
                }
            }
        }

        // Method to calculate daily profit (realized + unrealized)
        private double GetDailyProfit()
        {
            double realizedProfit = 0;
            double unrealizedProfit = 0;

            // Get realized profit for today
            foreach (Trade trade in SystemPerformance.AllTrades)
            {
                if (trade.Exit.Time.Date == Time[0].Date)
                {
                    realizedProfit += trade.ProfitCurrency;
                }
            }

            // Get unrealized profit if we have an open position
            if (Position.MarketPosition != MarketPosition.Flat)
            {
                unrealizedProfit = Position.GetUnrealizedProfitLoss(PerformanceUnit.Currency);
            }

            double totalDailyProfit = realizedProfit + unrealizedProfit;
            Print("DAILY PROFIT CHECK: Realized=" + realizedProfit + ", Unrealized=" + unrealizedProfit + ", Total=" + totalDailyProfit);
            
            return totalDailyProfit;
        }

        // Method to update trailing stop based on candle patterns
        private void UpdateTrailingStop()
        {
            if (CurrentBar < 2) return;

            if (shortPositionOpen)
            {
                // For short position: trail stop on higher high of previous RED candle
                bool prevCandleIsRed = Close[1] < Open[1];
                if (prevCandleIsRed && High[0] > High[1])
                {
                    // New higher high on previous red candle - update trailing stop
                    double newTrailLevel = High[1];
                    if (newTrailLevel > trailStopLevel)
                    {
                        trailStopLevel = newTrailLevel;
                        Print("TRAILING STOP UPDATED (SHORT): New level = " + trailStopLevel + " at " + Time[0]);
                    }
                }
            }
            else if (longPositionOpen)
            {
                // For long position: trail stop on lower low of previous GREEN candle
                bool prevCandleIsGreen = Close[1] > Open[1];
                if (prevCandleIsGreen && Low[0] < Low[1])
                {
                    // New lower low on previous green candle - update trailing stop
                    double newTrailLevel = Low[1];
                    if (newTrailLevel < trailStopLevel || trailStopLevel == 0)
                    {
                        trailStopLevel = newTrailLevel;
                        Print("TRAILING STOP UPDATED (LONG): New level = " + trailStopLevel + " at " + Time[0]);
                    }
                }
            }
        }

        // Method to initialize trailing stop when position is entered
        private void InitializeTrailingStop()
        {
            if (shortPositionOpen)
            {
                // For short position: start with the high of the current bar
                trailStopLevel = High[0];
                trailStopSet = true;
                Print("TRAILING STOP INITIALIZED (SHORT): Level = " + trailStopLevel + " at " + Time[0]);
            }
            else if (longPositionOpen)
            {
                // For long position: start with the low of the current bar
                trailStopLevel = Low[0];
                trailStopSet = true;
                Print("TRAILING STOP INITIALIZED (LONG): Level = " + trailStopLevel + " at " + Time[0]);
            }
        }

        // Method to check if trailing stop has been hit
        private void CheckTrailingStop()
        {
            if (!trailStopSet) return;

            if (shortPositionOpen && High[0] >= trailStopLevel)
            {
                // Trailing stop hit for short position
                ExitShort(DefaultQuantity, "Trailing Stop Hit", "Short on Red Dot");
                shortPositionOpen = false;
                waitingForGreenDotExit = false;
                trailStopSet = false;
                Print("TRAILING STOP HIT (SHORT): Exit at " + trailStopLevel + " at " + Time[0]);
            }
            else if (longPositionOpen && Low[0] <= trailStopLevel)
            {
                // Trailing stop hit for long position
                ExitLong(DefaultQuantity, "Trailing Stop Hit", "Long on Green Dot");
                longPositionOpen = false;
                waitingForRedDotExit = false;
                trailStopSet = false;
                Print("TRAILING STOP HIT (LONG): Exit at " + trailStopLevel + " at " + Time[0]);
            }
        }
    }
}