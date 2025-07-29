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
    public class OrderBlockTradingRobot6 : Strategy
    {
        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Max Daily Profit", Description = "Maximum daily profit before stopping trading", Order = 1, GroupName = "Max Profit")]
        public double MaxDailyProfit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Max Profit", Description = "Enable maximum daily profit feature", Order = 2, GroupName = "Max Profit")]
        public bool EnableMaxProfit { get; set; }

        // Trailing Stop Properties
        [NinjaScriptProperty]
        [Display(Name = "Enable Trailing Stop", Description = "Enable trailing stop functionality", Order = 3, GroupName = "Trailing Stop")]
        public bool EnableTrailingStop { get; set; }

        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Trailing Stop Distance", Description = "Distance in ticks for trailing stop", Order = 4, GroupName = "Trailing Stop")]
        public double TrailingStopDistance { get; set; }

        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Trailing Stop Activation", Description = "Profit in ticks before trailing stop activates", Order = 5, GroupName = "Trailing Stop")]
        public double TrailingStopActivation { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use ATR for Trailing Stop", Description = "Use ATR for dynamic trailing stop distance", Order = 6, GroupName = "Trailing Stop")]
        public bool UseATRForTrailingStop { get; set; }

        [NinjaScriptProperty]
        [Range(1, 50)]
        [Display(Name = "ATR Period", Description = "Period for ATR calculation", Order = 7, GroupName = "Trailing Stop")]
        public int ATRPeriod { get; set; }

        [NinjaScriptProperty]
        [Range(0.1, 5.0)]
        [Display(Name = "ATR Multiplier", Description = "Multiplier for ATR-based trailing stop", Order = 8, GroupName = "Trailing Stop")]
        public double ATRMultiplier { get; set; }

        private Series<double> activeOrderBlockLevel;
        private Series<bool> waitingForNextGreen;
        private Series<bool> showGreenDot;
        private Series<bool> redDotSignal;
        private Series<bool> greenDotSignal;
        private Series<double> atrSeries;

        private bool shortPositionOpen = false;
        private bool longPositionOpen = false;
        private double stopLossLevel = 0;
        private bool waitingForGreenDotExit = false;
        private bool waitingForRedDotExit = false;

        private bool justEntered = false; // Flag to prevent immediate exit
        private bool maxProfitReached = false; // Flag to stop trading when max profit is reached
        private DateTime lastTradeDate = DateTime.MinValue; // Track the last trade date

        // Trailing Stop Variables
        private double entryPrice = 0;
        private double highestPrice = 0;
        private double lowestPrice = 0;
        private bool trailingStopActivated = false;
        private double currentTrailingStopLevel = 0;
        private string trailingStopOrderId = "";

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Long on Green Dots, Stop on Opposite Signals with Trailing Stop";
                Name = "Order Block Trading FINAL with Trailing Stop";
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
                EnableTrailingStop = true;
                TrailingStopDistance = 10; // Default 10 ticks
                TrailingStopActivation = 5; // Activate after 5 ticks profit
                UseATRForTrailingStop = false;
                ATRPeriod = 14;
                ATRMultiplier = 2.0;
            }
            else if (State == State.Configure)
            {
                // Initialize series
                activeOrderBlockLevel = new Series<double>(this);
                waitingForNextGreen = new Series<bool>(this);
                showGreenDot = new Series<bool>(this);
                redDotSignal = new Series<bool>(this);
                greenDotSignal = new Series<bool>(this);
                atrSeries = new Series<double>(this);
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 3) return;

            // Calculate ATR if using ATR for trailing stop
            if (UseATRForTrailingStop && CurrentBar >= ATRPeriod)
            {
                double sum = 0;
                for (int i = 0; i < ATRPeriod; i++)
                {
                    sum += Math.Max(High[i] - Low[i], Math.Max(Math.Abs(High[i] - Close[i + 1]), Math.Abs(Low[i] - Close[i + 1])));
                }
                atrSeries[0] = sum / ATRPeriod;
            }

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
                    
                    // Initialize trailing stop variables for short position
                    if (EnableTrailingStop)
                    {
                        entryPrice = Close[0];
                        lowestPrice = Close[0];
                        highestPrice = Close[0];
                        trailingStopActivated = false;
                        currentTrailingStopLevel = 0;
                    }
                    
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
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

                    // Initialize trailing stop variables for long position
                    if (EnableTrailingStop)
                    {
                        entryPrice = Close[0];
                        highestPrice = Close[0];
                        lowestPrice = Close[0];
                        trailingStopActivated = false;
                        currentTrailingStopLevel = 0;
                    }

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
                    
                    // Initialize trailing stop variables for short position
                    if (EnableTrailingStop)
                    {
                        entryPrice = Close[0];
                        lowestPrice = Close[0];
                        highestPrice = Close[0];
                        trailingStopActivated = false;
                        currentTrailingStopLevel = 0;
                    }
                    
                    justEntered = true; // Set flag to prevent immediate exit
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
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

            // Handle trailing stop logic
            if (EnableTrailingStop && Position.MarketPosition != MarketPosition.Flat)
            {
                HandleTrailingStop();
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
                    
                    // Initialize trailing stop variables for long position
                    if (EnableTrailingStop)
                    {
                        entryPrice = Close[0];
                        highestPrice = Close[0];
                        lowestPrice = Close[0];
                        trailingStopActivated = false;
                        currentTrailingStopLevel = 0;
                    }
                    
                    Print("LONG ENTRY: Green dot signal at " + Time[0] + " Price: " + Close[0]);
                }
            }
        }

        // Handle trailing stop logic
        private void HandleTrailingStop()
        {
            if (Position.MarketPosition == MarketPosition.Long)
            {
                // Update highest price for long position
                if (Close[0] > highestPrice)
                {
                    highestPrice = Close[0];
                }

                // Check if trailing stop should be activated
                double profitTicks = (highestPrice - entryPrice) / TickSize;
                if (!trailingStopActivated && profitTicks >= TrailingStopActivation)
                {
                    trailingStopActivated = true;
                    Print("TRAILING STOP ACTIVATED for LONG position at " + Time[0] + " Profit: " + profitTicks + " ticks");
                }

                // Update trailing stop level if activated
                if (trailingStopActivated)
                {
                    double trailingDistance = UseATRForTrailingStop ? atrSeries[0] * ATRMultiplier : TrailingStopDistance * TickSize;
                    double newTrailingStopLevel = highestPrice - trailingDistance;

                    // Only update if the new level is higher (better for long position)
                    if (newTrailingStopLevel > currentTrailingStopLevel)
                    {
                        currentTrailingStopLevel = newTrailingStopLevel;
                        
                        // Cancel existing trailing stop order and place new one
                        if (!string.IsNullOrEmpty(trailingStopOrderId))
                        {
                            CancelOrder(trailingStopOrderId);
                        }
                        
                        Order trailingStopOrder = ExitLongStopMarket(DefaultQuantity, currentTrailingStopLevel, "Trailing Stop", "Long on Green Dot");
                        trailingStopOrderId = trailingStopOrder.OrderId;
                        Print("TRAILING STOP UPDATED for LONG: " + currentTrailingStopLevel + " at " + Time[0]);
                    }
                }
            }
            else if (Position.MarketPosition == MarketPosition.Short)
            {
                // Update lowest price for short position
                if (Close[0] < lowestPrice)
                {
                    lowestPrice = Close[0];
                }

                // Check if trailing stop should be activated
                double profitTicks = (entryPrice - lowestPrice) / TickSize;
                if (!trailingStopActivated && profitTicks >= TrailingStopActivation)
                {
                    trailingStopActivated = true;
                    Print("TRAILING STOP ACTIVATED for SHORT position at " + Time[0] + " Profit: " + profitTicks + " ticks");
                }

                // Update trailing stop level if activated
                if (trailingStopActivated)
                {
                    double trailingDistance = UseATRForTrailingStop ? atrSeries[0] * ATRMultiplier : TrailingStopDistance * TickSize;
                    double newTrailingStopLevel = lowestPrice + trailingDistance;

                    // Only update if the new level is lower (better for short position)
                    if (newTrailingStopLevel < currentTrailingStopLevel || currentTrailingStopLevel == 0)
                    {
                        currentTrailingStopLevel = newTrailingStopLevel;
                        
                        // Cancel existing trailing stop order and place new one
                        if (!string.IsNullOrEmpty(trailingStopOrderId))
                        {
                            CancelOrder(trailingStopOrderId);
                        }
                        
                        Order trailingStopOrder = ExitShortStopMarket(DefaultQuantity, currentTrailingStopLevel, "Trailing Stop", "Short on Red Dot");
                        trailingStopOrderId = trailingStopOrder.OrderId;
                        Print("TRAILING STOP UPDATED for SHORT: " + currentTrailingStopLevel + " at " + Time[0]);
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
                    
                    // Reset trailing stop variables when position is closed
                    if (EnableTrailingStop)
                    {
                        trailingStopActivated = false;
                        currentTrailingStopLevel = 0;
                        trailingStopOrderId = "";
                        entryPrice = 0;
                        highestPrice = 0;
                        lowestPrice = 0;
                    }
                    
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
    }
}