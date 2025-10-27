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
    public class OrderBlockTradingRobot9_Combined : Strategy
    {
        private Series<double> activeOrderBlockLevel;
        private Series<bool> waitingForNextGreen;
        private Series<bool> showGreenDot;
        private Series<bool> redDotSignal;
        private Series<bool> greenDotSignal;

        private double stopLossLevel = 0;
        private bool waitingForGreenDotExit = false;
        private bool waitingForRedDotExit = false;
        private bool justEntered = false; // Flag to prevent immediate exit

        // Per-Trade Profit Target Variables
        private double currentTradeUnrealizedPL = 0;
        private bool profitTargetReachedForCurrentTrade = false;
        private double lastEntryPrice = 0;
        private int lastEntryQuantity = 0;

        // Daily Total Profit Target Variables
        private double dailyProfit = 0;
        private bool dailyProfitTargetReached = false;
        private double totalPL = 0; // Total P&L (realized + unrealized)
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

        // Daily Total Profit Target Properties
        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Enable Daily Total Profit Target", Description = "Enable daily total profit target functionality", Order = 1, GroupName = "Daily Total Profit Target")]
        public bool EnableDailyTotalProfitTarget { get; set; }

        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Daily Total Profit Target Amount", Description = "Daily total profit target amount in currency units", Order = 2, GroupName = "Daily Total Profit Target")]
        public double DailyTotalProfitTargetAmount { get; set; }

        // Common Properties
        [NinjaScriptProperty]
        [Display(Name = "Reset Profit Target Daily", Description = "Reset profit target tracking at the start of each trading day", Order = 3, GroupName = "Common Settings")]
        public bool ResetProfitTargetDaily { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Auto Reset on Mid-Day Restart", Description = "Automatically reset profit target when strategy is restarted mid-day", Order = 4, GroupName = "Common Settings")]
        public bool AutoResetOnMidDayRestart { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Long on Green Dots, Stop on Opposite Signals - Combined Profit Targets";
                Name = "Order Block Short and Long Combined Profit Targets";
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

                // Initialize Per-Trade Profit Target Properties
                EnablePerTradeProfitTarget = false;
                PerTradeProfitTargetAmount = 200; // Default to $200 per trade

                // Initialize Daily Total Profit Target Properties
                EnableDailyTotalProfitTarget = false;
                DailyTotalProfitTargetAmount = 1000; // Default to $1000 daily total

                // Initialize Common Properties
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
                dailyProfit = 0;
                dailyProfitTargetReached = false;
                totalPL = 0;
                lastTradeDate = DateTime.MinValue;
                isFirstRun = true;
                hasProcessedFirstBar = false;
                strategyStartTime = DateTime.Now;
                Print("*** STRATEGY INITIALIZED ***: Combined profit targets reset.");
                Print("Per-Trade: Enable=" + EnablePerTradeProfitTarget + " Amount=" + PerTradeProfitTargetAmount);
                Print("Daily Total: Enable=" + EnableDailyTotalProfitTarget + " Amount=" + DailyTotalProfitTargetAmount);
                Print("Common: ResetDaily=" + ResetProfitTargetDaily + " AutoReset=" + AutoResetOnMidDayRestart);
            }
            else if (State == State.Realtime)
            {
                // Enhanced mid-day restart detection
                if ((EnablePerTradeProfitTarget || EnableDailyTotalProfitTarget) && AutoResetOnMidDayRestart)
                {
                    // Check if this is a mid-day restart scenario
                    bool isMidDayRestart = false;
                    
                    // Scenario 1: First run of the day with zero P&L
                    if (isFirstRun && currentTradeUnrealizedPL == 0 && dailyProfit == 0 && totalPL == 0)
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 1) ***: First run with zero P&L");
                    }
                    
                    // Scenario 2: Strategy restarted during trading hours with zero P&L
                    else if (!isFirstRun && currentTradeUnrealizedPL == 0 && dailyProfit == 0 && totalPL == 0 && Time[0].TimeOfDay > new TimeSpan(9, 30, 0))
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 2) ***: Restart during trading hours with zero P&L");
                    }
                    
                    // Scenario 3: Profit targets reached but P&L is zero (inconsistent state)
                    else if ((profitTargetReachedForCurrentTrade || dailyProfitTargetReached) && currentTradeUnrealizedPL == 0 && dailyProfit == 0 && totalPL == 0)
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 3) ***: Profit targets reached but P&L is zero");
                    }
                    
                    if (isMidDayRestart)
                    {
                        // Reset profit targets for mid-day restart
                        currentTradeUnrealizedPL = 0;
                        profitTargetReachedForCurrentTrade = false;
                        lastEntryPrice = 0;
                        lastEntryQuantity = 0;
                        dailyProfit = 0;
                        dailyProfitTargetReached = false;
                        totalPL = 0;
                        lastTradeDate = Time[0].Date;
                        Print("*** MID-DAY RESTART RESET ***: Combined profit targets reset for mid-day restart at " + Time[0]);
                    }
                }
                
                isFirstRun = false;
            }
        }

        protected override void OnBarUpdate()
        {
            // Debug print at the very start
            Print("OnBarUpdate Start: CurrentBar=" + CurrentBar + " Time=" + Time[0] + 
                  " PerTradeReached=" + profitTargetReachedForCurrentTrade + " PerTradeUnrealized=" + currentTradeUnrealizedPL.ToString("F2") + 
                  " DailyReached=" + dailyProfitTargetReached + " DailyProfit=" + dailyProfit.ToString("F2") + " TotalPL=" + totalPL.ToString("F2") + 
                  " LastTradeDate=" + lastTradeDate.ToString("yyyy-MM-dd"));

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
                dailyProfit = 0;
                dailyProfitTargetReached = false;
                totalPL = 0;
                lastTradeDate = Time[0].Date;
                Print("DATE CHANGE RESET: New trading day detected, resetting all profit tracking. Time: " + Time[0]);
            }

            if (CurrentBar < 3) return;

            // Check if we should reset profit targets daily (for new days)
            if (ResetProfitTargetDaily && IsFirstTickOfBar && (lastTradeDate == DateTime.MinValue || Time[0].Date != lastTradeDate.Date))
            {
                currentTradeUnrealizedPL = 0;
                profitTargetReachedForCurrentTrade = false;
                lastEntryPrice = 0;
                lastEntryQuantity = 0;
                dailyProfit = 0;
                dailyProfitTargetReached = false;
                totalPL = 0;
                lastTradeDate = Time[0].Date;
                Print("DAILY RESET: Combined profit targets reset for new trading day at " + Time[0] + " (Previous lastTradeDate: " + (lastTradeDate == DateTime.MinValue ? "MinValue" : lastTradeDate.ToString("yyyy-MM-dd")) + ")");
            }

            // Calculate P&L for current position if any profit target is enabled
            if ((EnablePerTradeProfitTarget || EnableDailyTotalProfitTarget) && lastEntryPrice > 0)
            {
                double unrealizedPL = 0;
                
                // Calculate unrealized P&L for current position
                if (Position.MarketPosition == MarketPosition.Long && lastEntryPrice > 0)
                {
                    // Calculate points difference and convert to dollars
                    double pointsDiff = Close[0] - lastEntryPrice;
                    // Use proper dollar calculation based on instrument
                    if (Instrument.MasterInstrument.InstrumentType == InstrumentType.Future)
                    {
                        unrealizedPL = pointsDiff * Position.Quantity * Instrument.MasterInstrument.PointValue;
                    }
                    else
                    {
                        unrealizedPL = pointsDiff * Position.Quantity * TickSize * 100; // Convert to dollars
                    }
                }
                else if (Position.MarketPosition == MarketPosition.Short && lastEntryPrice > 0)
                {
                    // Calculate points difference and convert to dollars
                    double pointsDiff = lastEntryPrice - Close[0];
                    // Use proper dollar calculation based on instrument
                    if (Instrument.MasterInstrument.InstrumentType == InstrumentType.Future)
                    {
                        unrealizedPL = pointsDiff * Position.Quantity * Instrument.MasterInstrument.PointValue;
                    }
                    else
                    {
                        unrealizedPL = pointsDiff * Position.Quantity * TickSize * 100; // Convert to dollars
                    }
                }

                // Update per-trade unrealized P&L
                if (EnablePerTradeProfitTarget)
                {
                    currentTradeUnrealizedPL = unrealizedPL;
                }

                // Update total P&L (realized + unrealized)
                if (EnableDailyTotalProfitTarget)
                {
                    totalPL = dailyProfit + unrealizedPL;
                }
                
                // DEBUG: Print P&L status every 10 bars
                if (CurrentBar % 10 == 0)
                {
                    Print("DEBUG COMBINED P&L: PerTradeUnrealized=" + currentTradeUnrealizedPL.ToString("F2") + " PerTradeTarget=" + PerTradeProfitTargetAmount + 
                          " DailyRealized=" + dailyProfit.ToString("F2") + " TotalPL=" + totalPL.ToString("F2") + " DailyTarget=" + DailyTotalProfitTargetAmount);
                }
                
                // Check per-trade profit target
                if (EnablePerTradeProfitTarget && !profitTargetReachedForCurrentTrade && currentTradeUnrealizedPL >= PerTradeProfitTargetAmount)
                {
                    profitTargetReachedForCurrentTrade = true;
                    Print("*** PER-TRADE PROFIT TARGET REACHED ***: Unrealized P&L " + currentTradeUnrealizedPL.ToString("F2") + " reached target " + PerTradeProfitTargetAmount + " at " + Time[0]);
                    Print("*** EXITING CURRENT TRADE ***: Closing position due to per-trade profit target");
                    
                    // Close current position due to per-trade profit target
                    if (Position.MarketPosition == MarketPosition.Long)
                    {
                        ExitLong(DefaultQuantity, "Per-Trade Profit Target Exit", "Long on Green Dot");
                        waitingForRedDotExit = false;
                        Print("*** PER-TRADE PROFIT TARGET EXIT ***: Closing long position at " + Close[0]);
                    }
                    else if (Position.MarketPosition == MarketPosition.Short)
                    {
                        ExitShort(DefaultQuantity, "Per-Trade Profit Target Exit", "Short on Red Dot");
                        waitingForGreenDotExit = false;
                        Print("*** PER-TRADE PROFIT TARGET EXIT ***: Closing short position at " + Close[0]);
                    }
                }
                
                // Check daily total profit target
                if (EnableDailyTotalProfitTarget && !dailyProfitTargetReached && totalPL >= DailyTotalProfitTargetAmount)
                {
                    dailyProfitTargetReached = true;
                    Print("*** DAILY TOTAL PROFIT TARGET REACHED ***: Total P&L " + totalPL.ToString("F2") + " (Realized: " + dailyProfit.ToString("F2") + " + Unrealized: " + unrealizedPL.ToString("F2") + ") reached target " + DailyTotalProfitTargetAmount + " at " + Time[0]);
                    Print("*** TRADING DISABLED ***: Strategy will no longer enter new positions for the day");
                    
                    // Close current position due to daily total profit target
                    if (Position.MarketPosition == MarketPosition.Long)
                    {
                        ExitLong(DefaultQuantity, "Daily Total Profit Target Exit", "Long on Green Dot");
                        waitingForRedDotExit = false;
                        Print("*** DAILY TOTAL PROFIT TARGET EXIT ***: Closing long position at " + Close[0]);
                    }
                    else if (Position.MarketPosition == MarketPosition.Short)
                    {
                        ExitShort(DefaultQuantity, "Daily Total Profit Target Exit", "Short on Red Dot");
                        waitingForGreenDotExit = false;
                        Print("*** DAILY TOTAL PROFIT TARGET EXIT ***: Closing short position at " + Close[0]);
                    }
                }
            }
            else if (Position.MarketPosition == MarketPosition.Flat)
            {
                // Reset per-trade tracking when flat
                currentTradeUnrealizedPL = 0;
                profitTargetReachedForCurrentTrade = false;
            }

            // CRITICAL: If daily total profit target reached AND enabled, EXIT IMMEDIATELY - NO MORE TRADING
            if (EnableDailyTotalProfitTarget && dailyProfitTargetReached)
            {
                Print("*** DAILY TOTAL PROFIT TARGET ACTIVE ***: Skipping all trading logic at " + Time[0]);
                return; // EXIT - NO MORE TRADING
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

            // Trading Logic - Entry and Exit (only if profit target not reached or not enabled)
            if (State == State.Realtime || State == State.Historical)
            {
                // Entry Logic: Go short on red dot signal (only on bar close)
                if (redDotSignal[0] && Position.MarketPosition == MarketPosition.Flat && IsFirstTickOfBar)
                {
                    // DOUBLE CHECK: Make sure daily total profit target not reached
                    if (EnableDailyTotalProfitTarget && dailyProfitTargetReached)
                    {
                        Print("*** BLOCKED SHORT ENTRY ***: Daily total profit target reached at " + Time[0]);
                        return;
                    }
                    
                    // DOUBLE CHECK: Make sure we're not in a position that hit per-trade profit target
                    if (EnablePerTradeProfitTarget && profitTargetReachedForCurrentTrade)
                    {
                        Print("*** BLOCKED SHORT ENTRY ***: Previous trade hit per-trade profit target at " + Time[0]);
                        return;
                    }
                    
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    waitingForGreenDotExit = true;
                    waitingForRedDotExit = false;
                    justEntered = true; // Set flag to prevent immediate exit
                    lastEntryPrice = Close[0];
                    lastEntryQuantity = DefaultQuantity;
                    // Reset per-trade tracking for new trade
                    currentTradeUnrealizedPL = 0;
                    profitTargetReachedForCurrentTrade = false;
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Entry Logic: Go long when stopped out on green dot (real-time)
                if (greenDotSignal[0] && Position.MarketPosition == MarketPosition.Short && waitingForGreenDotExit && !justEntered)
                {
                    // DOUBLE CHECK: Make sure daily total profit target not reached
                    if (EnableDailyTotalProfitTarget && dailyProfitTargetReached)
                    {
                        Print("*** BLOCKED LONG ENTRY ***: Daily total profit target reached at " + Time[0]);
                        return;
                    }
                    
                    // DOUBLE CHECK: Make sure we're not in a position that hit per-trade profit target
                    if (EnablePerTradeProfitTarget && profitTargetReachedForCurrentTrade)
                    {
                        Print("*** BLOCKED LONG ENTRY ***: Previous trade hit per-trade profit target at " + Time[0]);
                        return;
                    }
                    
                    stopLossLevel = activeOrderBlockLevel[0];
                    ExitShort(DefaultQuantity, "Real-time Stop on Green Dot", "Short on Red Dot");
                    waitingForGreenDotExit = false;
                    Print("REAL-TIME STOP LOSS: Green dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Immediately enter long position
                    EnterLong(DefaultQuantity, "Long on Green Dot");
                    waitingForRedDotExit = true;
                    waitingForGreenDotExit = false;
                    lastEntryPrice = Close[0];
                    lastEntryQuantity = DefaultQuantity;
                    justEntered = true; // Set flag to prevent immediate exit
                    // Reset per-trade tracking for new trade
                    currentTradeUnrealizedPL = 0;
                    profitTargetReachedForCurrentTrade = false;
                    Print("LONG ENTRY: Green dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Exit Logic: Exit long when red dot signal appears (only on candle close)
                if (redDotSignal[0] && Position.MarketPosition == MarketPosition.Long && waitingForRedDotExit && !justEntered && IsFirstTickOfBar)
                {
                    // DOUBLE CHECK: Make sure daily total profit target not reached
                    if (EnableDailyTotalProfitTarget && dailyProfitTargetReached)
                    {
                        Print("*** BLOCKED SHORT ENTRY FROM LONG EXIT ***: Daily total profit target reached at " + Time[0]);
                        return;
                    }
                    
                    // DOUBLE CHECK: Make sure we're not in a position that hit per-trade profit target
                    if (EnablePerTradeProfitTarget && profitTargetReachedForCurrentTrade)
                    {
                        Print("*** BLOCKED SHORT ENTRY FROM LONG EXIT ***: Previous trade hit per-trade profit target at " + Time[0]);
                        return;
                    }
                    
                    stopLossLevel = activeOrderBlockLevel[0];
                    ExitLong(DefaultQuantity, "Stop on Red Dot", "Long on Green Dot");
                    waitingForRedDotExit = false;
                    Print("STOP LOSS: Red dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Immediately enter short position
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    waitingForGreenDotExit = true;
                    waitingForRedDotExit = false;
                    lastEntryPrice = Close[0];
                    lastEntryQuantity = DefaultQuantity;
                    justEntered = true; // Set flag to prevent immediate exit
                    // Reset per-trade tracking for new trade
                    currentTradeUnrealizedPL = 0;
                    profitTargetReachedForCurrentTrade = false;
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
            if (Position.MarketPosition == MarketPosition.Short && waitingForGreenDotExit && !justEntered && CurrentBar >= 3 && 
                (!EnablePerTradeProfitTarget || !profitTargetReachedForCurrentTrade) && 
                (!EnableDailyTotalProfitTarget || !dailyProfitTargetReached))
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
                    waitingForGreenDotExit = false;
                    Print("REAL-TIME STOP LOSS: Green dot signal at " + Time[0] + " Stop Level: " + stopLossLevel);
                    
                    // Only enter long if profit targets not reached
                    if ((!EnablePerTradeProfitTarget || !profitTargetReachedForCurrentTrade) && 
                        (!EnableDailyTotalProfitTarget || !dailyProfitTargetReached))
                    {
                        // Immediately enter long position
                        EnterLong(DefaultQuantity, "Long on Green Dot");
                        waitingForRedDotExit = true;
                        waitingForGreenDotExit = false;
                        lastEntryPrice = Close[0];
                        lastEntryQuantity = DefaultQuantity;
                        justEntered = true; // Set flag to prevent immediate exit
                        // Reset per-trade tracking for new trade
                        currentTradeUnrealizedPL = 0;
                        profitTargetReachedForCurrentTrade = false;
                        Print("LONG ENTRY: Green dot signal at " + Time[0] + " Price: " + Close[0]);
                    }
                    else
                    {
                        Print("*** BLOCKED REAL-TIME LONG ENTRY ***: Profit target reached at " + Time[0]);
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
                    // Calculate profit/loss when position is closed
                    if (lastEntryPrice > 0 && lastEntryQuantity > 0)
                    {
                        double profitLoss = 0;
                        if (execution.Order.OrderType == OrderType.Market && execution.Order.OrderAction == OrderAction.Sell)
                        {
                            // Long position closed
                            double pointsDiff = price - lastEntryPrice;
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
                        else if (execution.Order.OrderType == OrderType.Market && execution.Order.OrderAction == OrderAction.Buy)
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

                        // Update daily profit
                        if (EnableDailyTotalProfitTarget)
                        {
                            dailyProfit += profitLoss;
                        }

                        Print("POSITION CLOSED: " + quantity + " contracts at " + price + " at " + time + " | P&L: " + profitLoss.ToString("F2"));
                        if (EnableDailyTotalProfitTarget)
                        {
                            Print("Daily P&L: " + dailyProfit.ToString("F2"));
                        }
                        
                        // Reset per-trade tracking after position is closed
                        currentTradeUnrealizedPL = 0;
                        profitTargetReachedForCurrentTrade = false;
                        lastEntryPrice = 0;
                        lastEntryQuantity = 0;
                        
                        // Update total P&L after realized profit is added
                        if (EnableDailyTotalProfitTarget)
                        {
                            totalPL = dailyProfit;
                            
                            // Check if daily total profit target is reached (this is a backup check)
                            if (!dailyProfitTargetReached && totalPL >= DailyTotalProfitTargetAmount)
                            {
                                dailyProfitTargetReached = true;
                                Print("DAILY TOTAL PROFIT TARGET REACHED: Total P&L " + totalPL.ToString("F2") + " reached target " + DailyTotalProfitTargetAmount + " at " + time);
                                Print("TRADING DISABLED: Strategy will no longer enter new positions for the day");
                            }
                        }
                    }
                }
            }
        }

        // Method to manually reset combined profit targets (can be called from strategy properties)
        public void ResetCombinedProfitTargets()
        {
            currentTradeUnrealizedPL = 0;
            profitTargetReachedForCurrentTrade = false;
            lastEntryPrice = 0;
            lastEntryQuantity = 0;
            dailyProfit = 0;
            dailyProfitTargetReached = false;
            totalPL = 0;
            lastTradeDate = Time[0].Date; // Set to current date
            Print("MANUAL RESET: Combined profit targets have been reset. Date: " + Time[0].ToString("yyyy-MM-dd"));
        }

        // Method to force reset combined profit targets for mid-day restarts
        public void ForceResetForMidDayRestart()
        {
            currentTradeUnrealizedPL = 0;
            profitTargetReachedForCurrentTrade = false;
            lastEntryPrice = 0;
            lastEntryQuantity = 0;
            dailyProfit = 0;
            dailyProfitTargetReached = false;
            totalPL = 0;
            lastTradeDate = Time[0].Date;
            Print("FORCE MID-DAY RESET: Combined profit targets forcefully reset for mid-day restart. Time: " + Time[0]);
        }

        // Method to get current per-trade unrealized P&L
        public double GetCurrentTradeUnrealizedPL()
        {
            return currentTradeUnrealizedPL;
        }

        // Method to check if per-trade profit target is reached
        public bool IsPerTradeProfitTargetReached()
        {
            return profitTargetReachedForCurrentTrade;
        }

        // Method to get current daily profit
        public double GetDailyProfit()
        {
            return dailyProfit;
        }

        // Method to check if daily total profit target is reached
        public bool IsDailyTotalProfitTargetReached()
        {
            return dailyProfitTargetReached;
        }

        // Method to get current total P&L
        public double GetTotalPL()
        {
            return totalPL;
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

        // Method to force enable daily total profit target (for testing)
        public void ForceEnableDailyTotalProfitTarget()
        {
            EnableDailyTotalProfitTarget = true;
            Print("*** FORCE ENABLED DAILY TOTAL PROFIT TARGET ***");
        }

        // Method to force set daily total profit target amount (for testing)
        public void ForceSetDailyTotalProfitTarget(double amount)
        {
            DailyTotalProfitTargetAmount = amount;
            Print("*** FORCE SET DAILY TOTAL PROFIT TARGET TO: " + amount + " ***");
        }
    }
}