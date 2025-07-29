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
    public class OrderBlockTradingRobot4_PerTrade : Strategy
    {
        private Series<double> activeOrderBlockLevel;
        private Series<bool> waitingForNextGreen;
        private Series<bool> showGreenDot;
        private Series<bool> redDotSignal;
        private Series<bool> greenDotSignal;
        private bool shortPositionOpen = false;
        private double stopLossLevel = 0;
        private bool waitingForGreenDotExit = false;
        private bool justEntered = false; // Flag to prevent immediate exit

        // Per-Trade Profit Target Variables
        private double currentTradeUnrealizedPL = 0;
        private bool profitTargetReachedForCurrentTrade = false;
        private double lastEntryPrice = 0;
        private int lastEntryQuantity = 0;
        private DateTime lastTradeDate = DateTime.MinValue;
        
        // Strategy restart detection
        private bool isFirstRun = true;
        private DateTime strategyStartTime = DateTime.MinValue;
        private bool hasProcessedFirstBar = false;

        // Per-Trade Profit Target Properties
        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Enable Per-Trade Profit Target", Description = "Enable per-trade profit target functionality", Order = 1, GroupName = "Per-Trade Profit Target")]
        public bool EnablePerTradeProfitTarget { get; set; }

        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Per-Trade Profit Target Amount", Description = "Profit target amount per trade in currency units", Order = 2, GroupName = "Per-Trade Profit Target")]
        public double PerTradeProfitTargetAmount { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Reset Profit Target Daily", Description = "Reset profit target tracking at the start of each trading day", Order = 3, GroupName = "Per-Trade Profit Target")]
        public bool ResetProfitTargetDaily { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Auto Reset on Mid-Day Restart", Description = "Automatically reset profit target when strategy is restarted mid-day", Order = 4, GroupName = "Per-Trade Profit Target")]
        public bool AutoResetOnMidDayRestart { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Stop ONLY on Green Dots - Per-Trade Profit Target";
                Name = "Order Block Trading Per-Trade Profit Target";
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

                // Initialize Per-Trade Profit Target Properties
                EnablePerTradeProfitTarget = false;
                PerTradeProfitTargetAmount = 200; // Default to $200 per trade
                ResetProfitTargetDaily = true;
                AutoResetOnMidDayRestart = true;
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
                currentTradeUnrealizedPL = 0;
                profitTargetReachedForCurrentTrade = false;
                lastEntryPrice = 0;
                lastEntryQuantity = 0;
                lastTradeDate = DateTime.MinValue;
                isFirstRun = true;
                hasProcessedFirstBar = false;
                strategyStartTime = DateTime.Now;
                Print("*** STRATEGY INITIALIZED ***: Per-trade profit target reset. EnablePerTradeProfitTarget=" + EnablePerTradeProfitTarget + " PerTradeProfitTargetAmount=" + PerTradeProfitTargetAmount + " ResetProfitTargetDaily=" + ResetProfitTargetDaily + " AutoResetOnMidDayRestart=" + AutoResetOnMidDayRestart);
            }
            else if (State == State.Realtime)
            {
                // Enhanced mid-day restart detection
                if (EnablePerTradeProfitTarget && AutoResetOnMidDayRestart)
                {
                    // Check if this is a mid-day restart scenario
                    bool isMidDayRestart = false;
                    
                    // Scenario 1: First run of the day with zero P&L
                    if (isFirstRun && currentTradeUnrealizedPL == 0)
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 1) ***: First run with zero P&L");
                    }
                    
                    // Scenario 2: Strategy restarted during trading hours with zero P&L
                    else if (!isFirstRun && currentTradeUnrealizedPL == 0 && Time[0].TimeOfDay > new TimeSpan(9, 30, 0))
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 2) ***: Restart during trading hours with zero P&L");
                    }
                    
                    // Scenario 3: Profit target reached but P&L is zero (inconsistent state)
                    else if (profitTargetReachedForCurrentTrade && currentTradeUnrealizedPL == 0)
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 3) ***: Profit target reached but P&L is zero");
                    }
                    
                    if (isMidDayRestart)
                    {
                        // Reset profit target for mid-day restart
                        currentTradeUnrealizedPL = 0;
                        profitTargetReachedForCurrentTrade = false;
                        lastEntryPrice = 0;
                        lastEntryQuantity = 0;
                        lastTradeDate = Time[0].Date;
                        Print("*** MID-DAY RESTART RESET ***: Per-trade profit target reset for mid-day restart at " + Time[0]);
                    }
                }
                
                isFirstRun = false;
            }
        }

        protected override void OnBarUpdate()
        {
            // Debug print at the very start
            Print("OnBarUpdate Start: CurrentBar=" + CurrentBar + " Time=" + Time[0] + " ProfitTargetReached=" + profitTargetReachedForCurrentTrade + " CurrentTradeUnrealizedPL=" + currentTradeUnrealizedPL.ToString("F2") + " LastTradeDate=" + lastTradeDate.ToString("yyyy-MM-dd"));

            // Mark that we've processed the first bar
            if (!hasProcessedFirstBar)
            {
                hasProcessedFirstBar = true;
            }

            // Additional safety check: if we're on a different date than lastTradeDate, reset everything
            if (lastTradeDate != DateTime.MinValue && Time[0].Date != lastTradeDate.Date)
            {
                currentTradeUnrealizedPL = 0;
                profitTargetReachedForCurrentTrade = false;
                lastEntryPrice = 0;
                lastEntryQuantity = 0;
                lastTradeDate = Time[0].Date;
                Print("DATE CHANGE RESET: New trading day detected, resetting all profit tracking. Time: " + Time[0]);
            }

            if (CurrentBar < 3) return;

            // Check if we should reset profit target daily (for new days)
            if (ResetProfitTargetDaily && IsFirstTickOfBar && (lastTradeDate == DateTime.MinValue || Time[0].Date != lastTradeDate.Date))
            {
                currentTradeUnrealizedPL = 0;
                profitTargetReachedForCurrentTrade = false;
                lastEntryPrice = 0;
                lastEntryQuantity = 0;
                lastTradeDate = Time[0].Date;
                Print("DAILY RESET: Per-trade profit target reset for new trading day at " + Time[0] + " (Previous lastTradeDate: " + (lastTradeDate == DateTime.MinValue ? "MinValue" : lastTradeDate.ToString("yyyy-MM-dd")) + ")");
            }

            // Calculate unrealized P&L for current trade if profit target is enabled
            if (EnablePerTradeProfitTarget && Position.MarketPosition == MarketPosition.Short && lastEntryPrice > 0)
            {
                // Calculate points difference and convert to dollars
                double pointsDiff = lastEntryPrice - Close[0];
                // Use proper dollar calculation based on instrument
                if (Instrument.MasterInstrument.InstrumentType == InstrumentType.Future)
                {
                    currentTradeUnrealizedPL = pointsDiff * Position.Quantity * Instrument.MasterInstrument.PointValue;
                }
                else
                {
                    currentTradeUnrealizedPL = pointsDiff * Position.Quantity * TickSize * 100; // Convert to dollars
                }
                
                // DEBUG: Print P&L status every 10 bars
                if (CurrentBar % 10 == 0)
                {
                    Print("DEBUG PER-TRADE P&L: Unrealized=" + currentTradeUnrealizedPL.ToString("F2") + " Target=" + PerTradeProfitTargetAmount + " Reached=" + profitTargetReachedForCurrentTrade + " TickSize=" + TickSize);
                }
                
                // Check if profit target is reached for current trade (only if not already reached)
                if (!profitTargetReachedForCurrentTrade && currentTradeUnrealizedPL >= PerTradeProfitTargetAmount)
                {
                    profitTargetReachedForCurrentTrade = true;
                    Print("*** PER-TRADE PROFIT TARGET REACHED ***: Unrealized P&L " + currentTradeUnrealizedPL.ToString("F2") + " reached target " + PerTradeProfitTargetAmount + " at " + Time[0]);
                    Print("*** EXITING CURRENT TRADE ***: Closing position due to profit target");
                    
                    // Close current position due to profit target
                    ExitShort(DefaultQuantity, "Per-Trade Profit Target Exit", "Short on Red Dot");
                    shortPositionOpen = false;
                    waitingForGreenDotExit = false;
                    Print("*** PER-TRADE PROFIT TARGET EXIT ***: Closing short position at " + Close[0]);
                }
            }
            else if (Position.MarketPosition == MarketPosition.Flat)
            {
                // Reset per-trade tracking when flat
                currentTradeUnrealizedPL = 0;
                profitTargetReachedForCurrentTrade = false;
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
                if (redDotSignal[0] && !shortPositionOpen && IsFirstTickOfBar)
                {
                    // DOUBLE CHECK: Make sure we're not in a position that hit profit target
                    if (EnablePerTradeProfitTarget && profitTargetReachedForCurrentTrade)
                    {
                        Print("*** BLOCKED SHORT ENTRY ***: Previous trade hit profit target at " + Time[0]);
                        return;
                    }
                    
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    lastEntryPrice = Close[0];
                    lastEntryQuantity = DefaultQuantity;
                    // Reset per-trade tracking for new trade
                    currentTradeUnrealizedPL = 0;
                    profitTargetReachedForCurrentTrade = false;
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Exit Logic: Exit short when green dot signal appears (real-time)
                if (greenDotSignal[0] && shortPositionOpen && waitingForGreenDotExit && !justEntered)
                {
                    stopLossLevel = activeOrderBlockLevel[0];
                    ExitShort(DefaultQuantity, "Real-time Stop on Green Dot", "Short on Red Dot");
                    shortPositionOpen = false;
                    waitingForGreenDotExit = false;
                    Print("REAL-TIME STOP LOSS: Green dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
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
                else if (marketPosition == MarketPosition.Flat)
                {
                    // Calculate profit/loss when position is closed
                    if (lastEntryPrice > 0 && lastEntryQuantity > 0)
                    {
                        double profitLoss = 0;
                        if (execution.Order.OrderType == OrderType.Market && execution.Order.OrderAction == OrderAction.Buy)
                        {
                            // Short position closed
                            double pointsDiff = lastEntryPrice - price;
                            // Use proper dollar calculation based on instrument
                            if (Instrument.MasterInstrument.InstrumentType == InstrumentType.Future)
                            {
                                profitLoss = pointsDiff * lastEntryQuantity * Instrument.MasterInstrument.PointValue;
                            }
                            else
                            {
                                profitLoss = pointsDiff * lastEntryQuantity * TickSize * 100; // Convert to dollars
                            }
                        }

                        Print("POSITION CLOSED: " + quantity + " contracts at " + price + " at " + time + " | P&L: " + profitLoss.ToString("F2"));
                        
                        // Reset per-trade tracking after position is closed
                        currentTradeUnrealizedPL = 0;
                        profitTargetReachedForCurrentTrade = false;
                        lastEntryPrice = 0;
                        lastEntryQuantity = 0;
                    }
                }
            }
        }

        // Method to manually reset per-trade profit target (can be called from strategy properties)
        public void ResetPerTradeProfitTarget()
        {
            currentTradeUnrealizedPL = 0;
            profitTargetReachedForCurrentTrade = false;
            lastEntryPrice = 0;
            lastEntryQuantity = 0;
            lastTradeDate = Time[0].Date; // Set to current date
            Print("MANUAL RESET: Per-trade profit target has been reset. CurrentTradeUnrealizedPL: " + currentTradeUnrealizedPL + " Date: " + Time[0].ToString("yyyy-MM-dd"));
        }

        // Method to force reset per-trade profit target for mid-day restarts
        public void ForceResetForMidDayRestart()
        {
            currentTradeUnrealizedPL = 0;
            profitTargetReachedForCurrentTrade = false;
            lastEntryPrice = 0;
            lastEntryQuantity = 0;
            lastTradeDate = Time[0].Date;
            Print("FORCE MID-DAY RESET: Per-trade profit target forcefully reset for mid-day restart. Time: " + Time[0]);
        }

        // Method to get current per-trade unrealized P&L
        public double GetCurrentTradeUnrealizedPL()
        {
            return currentTradeUnrealizedPL;
        }

        // Method to check if profit target is reached for current trade
        public bool IsPerTradeProfitTargetReached()
        {
            return profitTargetReachedForCurrentTrade;
        }

        // Method to get current entry price
        public double GetLastEntryPrice()
        {
            return lastEntryPrice;
        }

        // Method to force enable per-trade profit target (for testing)
        public void ForceEnablePerTradeProfitTarget()
        {
            EnablePerTradeProfitTarget = true;
            Print("*** FORCE ENABLED PER-TRADE PROFIT TARGET ***");
        }

        // Method to force set per-trade profit target amount (for testing)
        public void ForceSetPerTradeProfitTarget(double amount)
        {
            PerTradeProfitTargetAmount = amount;
            Print("*** FORCE SET PER-TRADE PROFIT TARGET TO: " + amount + " ***");
        }
    }
}