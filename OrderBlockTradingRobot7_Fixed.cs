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
    public class OrderBlockTradingRobot7 : Strategy
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

        private bool justEntered = false; // Flag to prevent immediate exit

        // Trailing Stop Variables
        private double trailingStopPrice = 0;
        private bool trailingStopActive = false;
        private double entryPrice = 0;

        // Cooldown Variables to prevent immediate re-entry after trailing stop
        private bool cooldownActive = false;
        private int cooldownBars = 0;
        private int cooldownBarLimit = 5; // Wait 5 bars before allowing re-entry

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Long on Green Dots, Stop on Opposite Signals";
                Name = "Order Block Trading 7";
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

                // Trailing Stop Parameters
                UseTrailingStop = true;
                TrailingStopDistance = 10; // Distance in ticks/points
                TrailingStopActivationDistance = 20; // Distance to activate trailing stop
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

        [NinjaScriptProperty]
        [Display(Name = "Use Trailing Stop", Description = "Enable/disable trailing stop functionality", Order = 1, GroupName = "Trailing Stop")]
        public bool UseTrailingStop { get; set; }

        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Trailing Stop Distance", Description = "Distance for trailing stop in ticks/points", Order = 2, GroupName = "Trailing Stop")]
        public int TrailingStopDistance { get; set; }

        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Trailing Stop Activation Distance", Description = "Distance to activate trailing stop in ticks/points", Order = 3, GroupName = "Trailing Stop")]
        public int TrailingStopActivationDistance { get; set; }

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

            // Update Cooldown
            UpdateCooldown();

            // Update Trailing Stop
            UpdateTrailingStop();

            // Trading Logic - Entry and Exit
            if (State == State.Realtime || State == State.Historical)
            {
                // Entry Logic: Go short on red dot signal (only on bar close) - WITH COOLDOWN CHECK
                if (redDotSignal[0] && !shortPositionOpen && !longPositionOpen && IsFirstTickOfBar && !cooldownActive)
                {
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    entryPrice = Close[0];
                    trailingStopActive = false;
                    trailingStopPrice = 0;
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Entry Logic: Go long when stopped out on green dot (real-time)
                if (greenDotSignal[0] && shortPositionOpen && waitingForGreenDotExit && !justEntered)
                {
                    stopLossLevel = activeOrderBlockLevel[0];
                    ExitShort(DefaultQuantity, "Real-time Stop on Green Dot", "Short on Red Dot");
                    shortPositionOpen = false;
                    waitingForGreenDotExit = false;
                    trailingStopActive = false;
                    Print("REAL-TIME STOP LOSS: Green dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Immediately enter long position
                    EnterLong(DefaultQuantity, "Long on Green Dot");
                    longPositionOpen = true;
                    waitingForRedDotExit = true;
                    entryPrice = Close[0];
                    trailingStopActive = false;
                    trailingStopPrice = 0;
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
                    trailingStopActive = false;
                    Print("STOP LOSS: Red dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Immediately enter short position
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    entryPrice = Close[0];
                    trailingStopActive = false;
                    trailingStopPrice = 0;
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

        private void UpdateCooldown()
        {
            if (cooldownActive)
            {
                cooldownBars++;
                if (cooldownBars >= cooldownBarLimit)
                {
                    cooldownActive = false;
                    cooldownBars = 0;
                    Print("COOLDOWN EXPIRED: Ready for new trades at " + Time[0]);
                }
            }
        }

        private void ActivateCooldown()
        {
            cooldownActive = true;
            cooldownBars = 0;
            Print("COOLDOWN ACTIVATED: Waiting " + cooldownBarLimit + " bars before new trades at " + Time[0]);
        }

        private void UpdateTrailingStop()
        {
            if (!UseTrailingStop) return;

            // For Long Position
            if (longPositionOpen && !justEntered)
            {
                double currentPrice = Close[0];
                double profitDistance = currentPrice - entryPrice;
                
                // Convert to ticks/points based on instrument
                double tickSize = TickSize;
                double profitInTicks = profitDistance / tickSize;
                
                // Activate trailing stop if profit exceeds activation distance
                if (profitInTicks >= TrailingStopActivationDistance)
                {
                    if (!trailingStopActive)
                    {
                        trailingStopActive = true;
                        trailingStopPrice = currentPrice - (TrailingStopDistance * tickSize);
                        Print("TRAILING STOP ACTIVATED for LONG at " + Time[0] + " Price: " + trailingStopPrice);
                    }
                    else
                    {
                        // Update trailing stop if price moves higher
                        double newTrailingStop = currentPrice - (TrailingStopDistance * tickSize);
                        if (newTrailingStop > trailingStopPrice)
                        {
                            trailingStopPrice = newTrailingStop;
                            Print("TRAILING STOP UPDATED for LONG at " + Time[0] + " New Stop: " + trailingStopPrice);
                        }
                    }
                    
                    // Check if trailing stop is hit
                    if (Low[0] <= trailingStopPrice)
                    {
                        ExitLong(DefaultQuantity, "Trailing Stop Exit", "Long on Green Dot");
                        longPositionOpen = false;
                        waitingForRedDotExit = false;
                        trailingStopActive = false;
                        ActivateCooldown(); // Activate cooldown after trailing stop exit
                        Print("TRAILING STOP EXIT for LONG at " + Time[0] + " Stop Price: " + trailingStopPrice);
                    }
                }
            }
            
            // For Short Position
            if (shortPositionOpen && !justEntered)
            {
                double currentPrice = Close[0];
                double profitDistance = entryPrice - currentPrice;
                
                // Convert to ticks/points based on instrument
                double tickSize = TickSize;
                double profitInTicks = profitDistance / tickSize;
                
                // Activate trailing stop if profit exceeds activation distance
                if (profitInTicks >= TrailingStopActivationDistance)
                {
                    if (!trailingStopActive)
                    {
                        trailingStopActive = true;
                        trailingStopPrice = currentPrice + (TrailingStopDistance * tickSize);
                        Print("TRAILING STOP ACTIVATED for SHORT at " + Time[0] + " Price: " + trailingStopPrice);
                    }
                    else
                    {
                        // Update trailing stop if price moves lower
                        double newTrailingStop = currentPrice + (TrailingStopDistance * tickSize);
                        if (newTrailingStop < trailingStopPrice)
                        {
                            trailingStopPrice = newTrailingStop;
                            Print("TRAILING STOP UPDATED for SHORT at " + Time[0] + " New Stop: " + trailingStopPrice);
                        }
                    }
                    
                    // Check if trailing stop is hit
                    if (High[0] >= trailingStopPrice)
                    {
                        ExitShort(DefaultQuantity, "Trailing Stop Exit", "Short on Red Dot");
                        shortPositionOpen = false;
                        waitingForGreenDotExit = false;
                        trailingStopActive = false;
                        ActivateCooldown(); // Activate cooldown after trailing stop exit
                        Print("TRAILING STOP EXIT for SHORT at " + Time[0] + " Stop Price: " + trailingStopPrice);
                    }
                }
            }
        }

        // Real-time exit method for short position
        protected override void OnMarketData(MarketDataEventArgs marketDataUpdate)
        {
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
                    trailingStopActive = false;
                    Print("REAL-TIME STOP LOSS: Green dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Immediately enter long position
                    EnterLong(DefaultQuantity, "Long on Green Dot");
                    longPositionOpen = true;
                    waitingForRedDotExit = true;
                    entryPrice = Close[0];
                    trailingStopActive = false;
                    trailingStopPrice = 0;
                    justEntered = true; // Set flag to prevent immediate exit
                    Print("LONG ENTRY: Green dot signal at " + Time[0] + " Price: " + Close[0]);
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