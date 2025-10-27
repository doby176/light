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
    public class OrderBlockTradingRobot_Combined : Strategy
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

        // Daily Profit Target Variables
        private double dailyProfit = 0;
        private bool dailyProfitTargetReached = false;
        private double totalPL = 0; // Total P&L (realized + unrealized)
        
        // Per-Trade Profit Target Variables
        private double currentTradeUnrealizedPL = 0;
        private bool perTradeProfitTargetReached = false;
        
        // Common Variables
        private DateTime lastTradeDate = DateTime.MinValue;
        private double lastEntryPrice = 0;
        private int lastEntryQuantity = 0;
        
        // Strategy restart detection
        private bool isFirstRun = true;
        private DateTime strategyStartTime = DateTime.MinValue;
        private bool hasProcessedFirstBar = false;

        // Daily Profit Target Properties
        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Enable Daily Profit Target", Description = "Enable daily profit target functionality", Order = 1, GroupName = "Daily Profit Target")]
        public bool EnableDailyProfitTarget { get; set; }

        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Daily Profit Target Amount", Description = "Daily profit target amount in currency units", Order = 2, GroupName = "Daily Profit Target")]
        public double DailyProfitTargetAmount { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Reset Daily Profit Target Daily", Description = "Reset daily profit target at the start of each trading day", Order = 3, GroupName = "Daily Profit Target")]
        public bool ResetDailyProfitTargetDaily { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Auto Reset Daily on Mid-Day Restart", Description = "Automatically reset daily profit target when strategy is restarted mid-day", Order = 4, GroupName = "Daily Profit Target")]
        public bool AutoResetDailyOnMidDayRestart { get; set; }

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
        [Display(Name = "Reset Per-Trade Profit Target Daily", Description = "Reset per-trade profit target tracking at the start of each trading day", Order = 3, GroupName = "Per-Trade Profit Target")]
        public bool ResetPerTradeProfitTargetDaily { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Auto Reset Per-Trade on Mid-Day Restart", Description = "Automatically reset per-trade profit target when strategy is restarted mid-day", Order = 4, GroupName = "Per-Trade Profit Target")]
        public bool AutoResetPerTradeOnMidDayRestart { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Combined Daily and Per-Trade Profit Targets";
                Name = "Order Block Robot Combined Profit Targets";
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

                // Initialize Daily Profit Target Properties
                EnableDailyProfitTarget = false;
                DailyProfitTargetAmount = 1000;
                ResetDailyProfitTargetDaily = true;
                AutoResetDailyOnMidDayRestart = true;

                // Initialize Per-Trade Profit Target Properties
                EnablePerTradeProfitTarget = false;
                PerTradeProfitTargetAmount = 200;
                ResetPerTradeProfitTargetDaily = true;
                AutoResetPerTradeOnMidDayRestart = true;
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
                // Reset all profit tracking at start
                dailyProfit = 0;
                dailyProfitTargetReached = false;
                totalPL = 0;
                currentTradeUnrealizedPL = 0;
                perTradeProfitTargetReached = false;
                lastEntryPrice = 0;
                lastEntryQuantity = 0;
                lastTradeDate = DateTime.MinValue;
                isFirstRun = true;
                hasProcessedFirstBar = false;
                strategyStartTime = DateTime.Now;
                Print("*** STRATEGY INITIALIZED ***: Combined profit targets reset.");
                Print("Daily Profit Target: Enable=" + EnableDailyProfitTarget + " Amount=" + DailyProfitTargetAmount + " ResetDaily=" + ResetDailyProfitTargetDaily + " AutoReset=" + AutoResetDailyOnMidDayRestart);
                Print("Per-Trade Profit Target: Enable=" + EnablePerTradeProfitTarget + " Amount=" + PerTradeProfitTargetAmount + " ResetDaily=" + ResetPerTradeProfitTargetDaily + " AutoReset=" + AutoResetPerTradeOnMidDayRestart);
                Print("*** IMPORTANT: Make sure to set 'Enable Daily Profit Target' to TRUE in strategy properties if you want daily profit target enforcement ***");
            }
            else if (State == State.Realtime)
            {
                // Enhanced mid-day restart detection for both profit targets
                if (AutoResetDailyOnMidDayRestart || AutoResetPerTradeOnMidDayRestart)
                {
                    // Check if this is a mid-day restart scenario
                    bool isMidDayRestart = false;
                    
                    // Scenario 1: First run of the day with zero P&L
                    if (isFirstRun && dailyProfit == 0 && totalPL == 0 && currentTradeUnrealizedPL == 0)
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 1) ***: First run with zero P&L");
                    }
                    
                    // Scenario 2: Strategy restarted during trading hours with zero P&L
                    else if (!isFirstRun && dailyProfit == 0 && totalPL == 0 && currentTradeUnrealizedPL == 0 && Time[0].TimeOfDay > new TimeSpan(9, 30, 0))
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 2) ***: Restart during trading hours with zero P&L");
                    }
                    
                    // Scenario 3: Profit targets reached but P&L is zero (inconsistent state)
                    else if ((dailyProfitTargetReached && dailyProfit == 0 && totalPL == 0) || (perTradeProfitTargetReached && currentTradeUnrealizedPL == 0))
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 3) ***: Profit targets reached but P&L is zero");
                    }
                    
                    // Scenario 4: TotalPL is non-zero but DailyProfit is zero (restart with unrealized P&L)
                    else if (isFirstRun && dailyProfitTargetReached && dailyProfit == 0 && totalPL > 0 && totalPL < DailyProfitTargetAmount)
                    {
                        isMidDayRestart = true;
                        Print("*** MID-DAY RESTART DETECTED (Scenario 4) ***: TotalPL=" + totalPL + " but DailyProfit=0 (restart with unrealized P&L)");
                    }
                    
                    if (isMidDayRestart)
                    {
                        // Reset profit targets for mid-day restart
                        if (AutoResetDailyOnMidDayRestart)
                        {
                            dailyProfit = 0;
                            totalPL = 0;
                            dailyProfitTargetReached = false;
                        }
                        
                        if (AutoResetPerTradeOnMidDayRestart)
                        {
                            currentTradeUnrealizedPL = 0;
                            perTradeProfitTargetReached = false;
                            lastEntryPrice = 0;
                            lastEntryQuantity = 0;
                        }
                        
                        lastTradeDate = Time[0].Date;
                        Print("*** MID-DAY RESTART RESET ***: Profit targets reset for mid-day restart at " + Time[0]);
                    }
                }
                
                isFirstRun = false;
            }
        }

        protected override void OnBarUpdate()
        {
            // Debug print at the very start
            Print("OnBarUpdate Start: CurrentBar=" + CurrentBar + " Time=" + Time[0] + 
                  " DailyTargetReached=" + dailyProfitTargetReached + " DailyRealizedProfit=" + dailyProfit.ToString("F2") + " TotalPL=" + totalPL.ToString("F2") +
                  " PerTradeTargetReached=" + perTradeProfitTargetReached + " CurrentTradeUnrealizedPL=" + currentTradeUnrealizedPL.ToString("F2") +
                  " LastTradeDate=" + lastTradeDate.ToString("yyyy-MM-dd"));

            // Mark that we've processed the first bar
            if (!hasProcessedFirstBar)
            {
                hasProcessedFirstBar = true;
            }

            // Additional safety check: if we're on a different date than lastTradeDate, reset everything
            if (lastTradeDate != DateTime.MinValue && Time[0].Date != lastTradeDate.Date)
            {
                dailyProfit = 0;
                dailyProfitTargetReached = false;
                totalPL = 0;
                currentTradeUnrealizedPL = 0;
                perTradeProfitTargetReached = false;
                lastEntryPrice = 0;
                lastEntryQuantity = 0;
                lastTradeDate = Time[0].Date;
                Print("DATE CHANGE RESET: New trading day detected, resetting all profit tracking. Time: " + Time[0]);
            }

            if (CurrentBar < 3) return;

            // Check if we should reset profit targets daily (for new days)
            if (IsFirstTickOfBar && (lastTradeDate == DateTime.MinValue || Time[0].Date != lastTradeDate.Date))
            {
                if (ResetDailyProfitTargetDaily)
                {
                    dailyProfit = 0;
                    totalPL = 0;
                    dailyProfitTargetReached = false;
                }
                
                if (ResetPerTradeProfitTargetDaily)
                {
                    currentTradeUnrealizedPL = 0;
                    perTradeProfitTargetReached = false;
                    lastEntryPrice = 0;
                    lastEntryQuantity = 0;
                }
                
                lastTradeDate = Time[0].Date;
                Print("DAILY RESET: Profit targets reset for new trading day at " + Time[0]);
            }

            // Calculate P&L for both profit targets if enabled
            if (Position.MarketPosition == MarketPosition.Short && lastEntryPrice > 0)
            {
                // Calculate points difference and convert to dollars
                double pointsDiff = lastEntryPrice - Close[0];
                double dollarValue = 0;
                
                // Use proper dollar calculation based on instrument
                if (Instrument.MasterInstrument.InstrumentType == InstrumentType.Future)
                {
                    dollarValue = pointsDiff * Position.Quantity * Instrument.MasterInstrument.PointValue;
                }
                else
                {
                    dollarValue = pointsDiff * Position.Quantity * TickSize * 100; // Convert to dollars
                }

                // Update per-trade unrealized P&L
                if (EnablePerTradeProfitTarget)
                {
                    currentTradeUnrealizedPL = dollarValue;
                }

                // Update total P&L (ALWAYS track total P&L = realized + unrealized)
                totalPL = dailyProfit + dollarValue;
                
                // DEBUG: Print P&L status every 10 bars
                if (CurrentBar % 10 == 0)
                {
                    Print("DEBUG P&L: Daily Realized=" + dailyProfit.ToString("F2") + " Daily Total=" + totalPL.ToString("F2") + 
                          " PerTrade Unrealized=" + currentTradeUnrealizedPL.ToString("F2") + " TickSize=" + TickSize + 
                          " Entry=" + lastEntryPrice + " Current=" + Close[0] + " Points=" + pointsDiff.ToString("F2"));
                }
                
                // Check if daily profit target is reached (ALWAYS check, but only enforce when enabled)
                if (!dailyProfitTargetReached && totalPL >= DailyProfitTargetAmount)
                {
                    dailyProfitTargetReached = true;
                    Print("*** DAILY PROFIT TARGET REACHED ***: Total P&L " + totalPL.ToString("F2") + " reached target " + DailyProfitTargetAmount + " at " + Time[0]);
                    
                    // Only enforce the target if the feature is enabled
                    if (EnableDailyProfitTarget)
                    {
                        Print("*** TRADING DISABLED ***: Strategy will no longer enter new positions");
                        
                        // Close current position if any
                        if (Position.MarketPosition == MarketPosition.Short)
                        {
                            ExitShort(DefaultQuantity, "Daily Profit Target Exit", "Short on Red Dot");
                            Print("*** DAILY PROFIT TARGET EXIT ***: Closing short position at " + Close[0]);
                        }
                    }
                    else
                    {
                        Print("*** DAILY PROFIT TARGET REACHED BUT NOT ENFORCED ***: Feature is disabled, trading continues");
                    }
                }
                
                // Check if per-trade profit target is reached
                if (EnablePerTradeProfitTarget && !perTradeProfitTargetReached && currentTradeUnrealizedPL >= PerTradeProfitTargetAmount)
                {
                    perTradeProfitTargetReached = true;
                    Print("*** PER-TRADE PROFIT TARGET REACHED ***: Unrealized P&L " + currentTradeUnrealizedPL.ToString("F2") + " reached target " + PerTradeProfitTargetAmount + " at " + Time[0]);
                    Print("*** EXITING CURRENT TRADE ***: Closing position due to per-trade profit target");
                    
                    // Close current position due to per-trade profit target
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
                perTradeProfitTargetReached = false;
            }

            // CRITICAL: If daily profit target reached AND enabled, EXIT IMMEDIATELY - NO MORE TRADING
            if (EnableDailyProfitTarget && dailyProfitTargetReached)
            {
                Print("*** DAILY PROFIT TARGET ACTIVE ***: Skipping all trading logic at " + Time[0]);
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

            // Trading Logic - Entry and Exit
            if (State == State.Realtime || State == State.Historical)
            {
                // Entry Logic: Go short on red dot signal (only on bar close)
                if (redDotSignal[0] && !shortPositionOpen && IsFirstTickOfBar)
                {
                    // DOUBLE CHECK: Make sure daily profit target not reached
                    if (EnableDailyProfitTarget && dailyProfitTargetReached)
                    {
                        Print("*** BLOCKED SHORT ENTRY ***: Daily profit target reached at " + Time[0]);
                        return;
                    }
                    
                    // DOUBLE CHECK: Make sure we're not in a position that hit per-trade profit target
                    if (EnablePerTradeProfitTarget && perTradeProfitTargetReached)
                    {
                        Print("*** BLOCKED SHORT ENTRY ***: Previous trade hit per-trade profit target at " + Time[0]);
                        return;
                    }
                    
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    lastEntryPrice = Close[0];
                    lastEntryQuantity = DefaultQuantity;
                    
                    // Reset per-trade tracking for new trade
                    if (EnablePerTradeProfitTarget)
                    {
                        currentTradeUnrealizedPL = 0;
                        perTradeProfitTargetReached = false;
                    }
                    
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
                Print("EXECUTION UPDATE: Order=" + execution.Order.OrderType + " Action=" + execution.Order.OrderAction + 
                      " Position=" + marketPosition + " Price=" + price + " Qty=" + quantity + " Time=" + time);
                
                if (marketPosition == MarketPosition.Short)
                {
                    Print("SHORT FILLED: " + quantity + " contracts at " + price + " at " + time);
                    
                    // Update entry price and quantity with actual fill data
                    lastEntryPrice = price;
                    lastEntryQuantity = quantity;
                    Print("ENTRY UPDATED: lastEntryPrice=" + lastEntryPrice + " lastEntryQuantity=" + lastEntryQuantity);
                }
                else if (marketPosition == MarketPosition.Flat)
                {
                    // Calculate profit/loss when position is closed
                    if (lastEntryPrice > 0 && lastEntryQuantity > 0)
                    {
                        double profitLoss = 0;
                        
                        // IMPROVED: Check for ANY buy order that closes a short position
                        // This includes Market Buy, Limit Buy, Stop Market Buy, etc.
                        if (execution.Order.OrderAction == OrderAction.Buy)
                        {
                            // Short position closed - calculate profit/loss
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
                            
                            Print("P&L CALCULATION: Entry=" + lastEntryPrice + " Exit=" + price + " Points=" + pointsDiff.ToString("F2") + " Profit=" + profitLoss.ToString("F2"));
                        }
                        else
                        {
                            Print("WARNING: Position closed but not a Buy order. OrderAction=" + execution.Order.OrderAction);
                        }

                        // Update daily profit for realized trades (ALWAYS track realized P&L)
                        dailyProfit += profitLoss;
                        totalPL = dailyProfit; // Reset total PL to realized profit

                        Print("POSITION CLOSED: " + quantity + " contracts at " + price + " at " + time + " | P&L: " + profitLoss.ToString("F2"));
                        Print("Daily P&L: " + dailyProfit.ToString("F2"));
                        Print("Total P&L: " + totalPL.ToString("F2"));
                        
                        // Reset per-trade tracking after position is closed
                        if (EnablePerTradeProfitTarget)
                        {
                            currentTradeUnrealizedPL = 0;
                            perTradeProfitTargetReached = false;
                        }
                        
                        lastEntryPrice = 0;
                        lastEntryQuantity = 0;
                        
                        // Check if daily profit target is reached (this is a backup check)
                        if (!dailyProfitTargetReached && totalPL >= DailyProfitTargetAmount)
                        {
                            dailyProfitTargetReached = true;
                            Print("DAILY PROFIT TARGET REACHED: Total P&L " + totalPL.ToString("F2") + " reached target " + DailyProfitTargetAmount + " at " + time);
                            
                            if (EnableDailyProfitTarget)
                            {
                                Print("TRADING DISABLED: Strategy will no longer enter new positions");
                            }
                            else
                            {
                                Print("DAILY PROFIT TARGET REACHED BUT NOT ENFORCED: Feature is disabled, trading continues");
                            }
                        }
                    }
                    else
                    {
                        Print("WARNING: Position closed but lastEntryPrice=" + lastEntryPrice + " lastEntryQuantity=" + lastEntryQuantity);
                    }
                }
            }
        }

        // ===== PUBLIC METHODS FOR DAILY PROFIT TARGET =====

        // Method to manually reset daily profit target
        public void ResetDailyProfitTarget()
        {
            dailyProfit = 0;
            totalPL = 0;
            dailyProfitTargetReached = false;
            lastTradeDate = Time[0].Date;
            Print("MANUAL RESET: Daily profit target has been reset. Daily profit: " + dailyProfit + " TotalPL: " + totalPL + " Date: " + Time[0].ToString("yyyy-MM-dd"));
        }

        // Method to force reset daily profit target for mid-day restarts
        public void ForceResetDailyForMidDayRestart()
        {
            dailyProfit = 0;
            totalPL = 0;
            dailyProfitTargetReached = false;
            lastTradeDate = Time[0].Date;
            Print("FORCE MID-DAY RESET: Daily profit target forcefully reset for mid-day restart. Time: " + Time[0]);
        }

        // Method to get current daily profit
        public double GetCurrentDailyProfit()
        {
            return dailyProfit;
        }

        // Method to check if daily profit target is reached
        public bool IsDailyProfitTargetReached()
        {
            return dailyProfitTargetReached;
        }

        // Method to get current total P&L
        public double GetTotalPL()
        {
            return totalPL;
        }

        // Method to force enable daily profit target (for testing)
        public void ForceEnableDailyProfitTarget()
        {
            EnableDailyProfitTarget = true;
            Print("*** FORCE ENABLED DAILY PROFIT TARGET ***");
        }

        // Method to force set daily profit target amount (for testing)
        public void ForceSetDailyProfitTarget(double amount)
        {
            DailyProfitTargetAmount = amount;
            Print("*** FORCE SET DAILY PROFIT TARGET TO: " + amount + " ***");
        }

        // Method to force set daily profit for testing
        public void ForceSetDailyProfit(double profit)
        {
            dailyProfit = profit;
            totalPL = dailyProfit;
            Print("*** FORCE SET DAILY PROFIT TO: " + profit + " ***");
            Print("*** DAILY PROFIT: " + dailyProfit + " TOTAL PL: " + totalPL + " ***");
        }

        // Method to force set daily profit target reached flag for testing
        public void ForceSetDailyProfitTargetReached(bool reached)
        {
            dailyProfitTargetReached = reached;
            Print("*** FORCE SET DAILY PROFIT TARGET REACHED TO: " + reached + " ***");
        }

        // ===== PUBLIC METHODS FOR PER-TRADE PROFIT TARGET =====

        // Method to manually reset per-trade profit target
        public void ResetPerTradeProfitTarget()
        {
            currentTradeUnrealizedPL = 0;
            perTradeProfitTargetReached = false;
            lastEntryPrice = 0;
            lastEntryQuantity = 0;
            lastTradeDate = Time[0].Date;
            Print("MANUAL RESET: Per-trade profit target has been reset. CurrentTradeUnrealizedPL: " + currentTradeUnrealizedPL + " Date: " + Time[0].ToString("yyyy-MM-dd"));
        }

        // Method to force reset per-trade profit target for mid-day restarts
        public void ForceResetPerTradeForMidDayRestart()
        {
            currentTradeUnrealizedPL = 0;
            perTradeProfitTargetReached = false;
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

        // Method to check if per-trade profit target is reached
        public bool IsPerTradeProfitTargetReached()
        {
            return perTradeProfitTargetReached;
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

        // ===== COMBINED METHODS =====

        // Method to reset both profit targets
        public void ResetAllProfitTargets()
        {
            ResetDailyProfitTarget();
            ResetPerTradeProfitTarget();
            Print("ALL PROFIT TARGETS RESET: Both daily and per-trade profit targets have been reset.");
        }

        // Method to get current status of both profit targets
        public string GetProfitTargetStatus()
        {
            string status = "Profit Target Status:\n";
            status += "Daily Profit Target: " + (EnableDailyProfitTarget ? "Enabled" : "Disabled") + 
                     " | Amount: " + DailyProfitTargetAmount + 
                     " | Current: " + dailyProfit.ToString("F2") + 
                     " | TotalPL: " + totalPL.ToString("F2") + 
                     " | Reached: " + dailyProfitTargetReached + "\n";
            status += "Per-Trade Profit Target: " + (EnablePerTradeProfitTarget ? "Enabled" : "Disabled") + 
                     " | Amount: " + PerTradeProfitTargetAmount + 
                     " | Current: " + currentTradeUnrealizedPL.ToString("F2") + 
                     " | Reached: " + perTradeProfitTargetReached;
            return status;
        }
    }
}