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
    public class OrderBlockTradingRobot5 : Strategy
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

        // Profit Target Variables
        private double cumulativeProfit = 0;
        private bool profitTargetReached = false;
        private double lastEntryPrice = 0;
        private bool isProfitTargetEnabled = false;

        // Profit Target Properties
        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Enable Profit Target", Description = "Enable profit target functionality", Order = 1, GroupName = "Profit Target")]
        public bool EnableProfitTarget { get; set; }

        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Profit Target Amount", Description = "Profit target amount in currency units", Order = 2, GroupName = "Profit Target")]
        public double ProfitTargetAmount { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Reset Profit Target Daily", Description = "Reset profit target at the start of each trading day", Order = 3, GroupName = "Profit Target")]
        public bool ResetProfitTargetDaily { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Long on Green Dots, Stop on Opposite Signals";
                Name = "Order Block Trading FINAL FLIP TO LONG";
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

                // Initialize Profit Target Properties
                EnableProfitTarget = false;
                ProfitTargetAmount = 1000;
                ResetProfitTargetDaily = true;
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
            else if (State == State.DataLoaded)
            {
                // Reset profit tracking at start
                cumulativeProfit = 0;
                profitTargetReached = false;
                isProfitTargetEnabled = EnableProfitTarget;
            }
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 3) return;

            // Check if we should reset profit target daily
            if (ResetProfitTargetDaily && IsFirstTickOfBar && Time[0].Date != Time[1].Date)
            {
                cumulativeProfit = 0;
                profitTargetReached = false;
                Print("DAILY RESET: Profit target reset for new trading day at " + Time[0]);
            }

            // Check if profit target is reached and disable trading
            if (isProfitTargetEnabled && !profitTargetReached && cumulativeProfit >= ProfitTargetAmount)
            {
                profitTargetReached = true;
                Print("PROFIT TARGET REACHED: Cumulative profit " + cumulativeProfit + " reached target " + ProfitTargetAmount + " at " + Time[0]);
                Print("TRADING DISABLED: Strategy will no longer enter new positions");
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

            // Trading Logic - Entry and Exit (only if profit target not reached)
            if ((State == State.Realtime || State == State.Historical) && !profitTargetReached)
            {
                // Entry Logic: Go short on red dot signal (only on bar close)
                if (redDotSignal[0] && !shortPositionOpen && !longPositionOpen && IsFirstTickOfBar)
                {
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    lastEntryPrice = Close[0];
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
                    lastEntryPrice = Close[0];
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
                    lastEntryPrice = Close[0];
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
            // Only check for real-time exits if we have a short position and profit target not reached
            if (shortPositionOpen && waitingForGreenDotExit && !justEntered && CurrentBar >= 3 && !profitTargetReached)
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
                    lastEntryPrice = Close[0];
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
                    // Calculate profit/loss when position is closed
                    if (lastEntryPrice > 0)
                    {
                        double profitLoss = 0;
                        if (execution.Order.OrderType == OrderType.Market && execution.Order.OrderAction == OrderAction.Sell)
                        {
                            // Long position closed
                            profitLoss = (price - lastEntryPrice) * quantity;
                        }
                        else if (execution.Order.OrderType == OrderType.Market && execution.Order.OrderAction == OrderAction.Buy)
                        {
                            // Short position closed
                            profitLoss = (lastEntryPrice - price) * quantity;
                        }

                        cumulativeProfit += profitLoss;
                        Print("POSITION CLOSED: " + quantity + " contracts at " + price + " at " + time + " | P&L: " + profitLoss.ToString("F2") + " | Cumulative P&L: " + cumulativeProfit.ToString("F2"));
                        
                        // Check if profit target is reached
                        if (isProfitTargetEnabled && !profitTargetReached && cumulativeProfit >= ProfitTargetAmount)
                        {
                            profitTargetReached = true;
                            Print("PROFIT TARGET REACHED: Cumulative profit " + cumulativeProfit.ToString("F2") + " reached target " + ProfitTargetAmount + " at " + time);
                            Print("TRADING DISABLED: Strategy will no longer enter new positions");
                        }
                    }
                }
            }
        }

        // Method to manually reset profit target (can be called from strategy properties)
        public void ResetProfitTarget()
        {
            cumulativeProfit = 0;
            profitTargetReached = false;
            Print("MANUAL RESET: Profit target has been reset. Cumulative profit: " + cumulativeProfit);
        }

        // Method to get current profit status
        public double GetCurrentProfit()
        {
            return cumulativeProfit;
        }

        // Method to check if profit target is reached
        public bool IsProfitTargetReached()
        {
            return profitTargetReached;
        }
    }
}