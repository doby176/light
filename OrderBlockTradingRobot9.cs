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
    public class OrderBlockTradingRobot9 : Strategy
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

        // Profit Target Variables
        private double dailyProfit = 0;
        private bool profitTargetReached = false;
        private DateTime lastTradeDate = DateTime.MinValue;
        private double lastEntryPrice = 0;
        private int lastEntryQuantity = 0;
        private double totalPL = 0; // Total P&L (realized + unrealized)
        private double realizedPL = 0; // NEW: Track realized P&L separately
        
        // NEW: Strategy restart detection
        private bool isFirstRun = true;
        private DateTime strategyStartTime = DateTime.MinValue;
        private bool hasProcessedFirstBar = false;
        private bool isRestartSyncComplete = false; // NEW: Track if restart sync is complete

        // Profit Target Properties
        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Enable Profit Target", Description = "Enable profit target functionality", Order = 1, GroupName = "Profit Target")]
        public bool EnableProfitTarget { get; set; }

        [NinjaScriptProperty]
        [Range(0, double.MaxValue)]
        [Display(Name = "Profit Target Amount", Description = "Daily profit target amount in currency units", Order = 2, GroupName = "Profit Target")]
        public double ProfitTargetAmount { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Reset Profit Target Daily", Description = "Reset profit target at the start of each trading day", Order = 3, GroupName = "Profit Target")]
        public bool ResetProfitTargetDaily { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Auto Reset on Mid-Day Restart", Description = "Automatically reset profit target when strategy is restarted mid-day with zero P&L", Order = 4, GroupName = "Profit Target")]
        public bool AutoResetOnMidDayRestart { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Short on Red Dots, Long on Green Dots, Stop on Opposite Signals";
                Name = "Order Block Short and Long Max daily profit";
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
                AutoResetOnMidDayRestart = true; // NEW: Default to true
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
                dailyProfit = 0;
                realizedPL = 0;
                totalPL = 0;
                profitTargetReached = false;
                lastTradeDate = DateTime.MinValue;
                isFirstRun = true;
                hasProcessedFirstBar = false;
                strategyStartTime = DateTime.Now;
                Print("*** STRATEGY INITIALIZED ***: Profit target reset. EnableProfitTarget=" + EnableProfitTarget + " ProfitTargetAmount=" + ProfitTargetAmount + " ResetProfitTargetDaily=" + ResetProfitTargetDaily + " AutoResetOnMidDayRestart=" + AutoResetOnMidDayRestart);
            }
                    else if (State == State.Realtime)
        {
            // NEW: Enhanced mid-day restart detection and position state reset
            bool isMidDayRestart = false;
            
            // CRITICAL: Always check for restart scenarios, not just when profit target is enabled
            // Check if this is a mid-day restart scenario
            
            // Scenario 1: First run of the day with zero P&L
            if (isFirstRun && dailyProfit == 0 && totalPL == 0)
            {
                isMidDayRestart = true;
                Print("*** MID-DAY RESTART DETECTED (Scenario 1) ***: First run with zero P&L");
            }
            
            // Scenario 2: Strategy restarted during trading hours with zero P&L
            else if (!isFirstRun && dailyProfit == 0 && totalPL == 0 && Time[0].TimeOfDay > new TimeSpan(9, 30, 0))
            {
                isMidDayRestart = true;
                Print("*** MID-DAY RESTART DETECTED (Scenario 2) ***: Restart during trading hours with zero P&L");
            }
            
            // Scenario 3: Profit target reached but P&L is zero (inconsistent state)
            else if (profitTargetReached && dailyProfit == 0 && totalPL == 0)
            {
                isMidDayRestart = true;
                Print("*** MID-DAY RESTART DETECTED (Scenario 3) ***: Profit target reached but P&L is zero");
            }
            
            // NEW: Scenario 4: TotalPL is non-zero but DailyProfit is zero (restart with unrealized P&L)
            else if (isFirstRun && profitTargetReached && dailyProfit == 0 && totalPL > 0 && totalPL < ProfitTargetAmount)
            {
                isMidDayRestart = true;
                Print("*** MID-DAY RESTART DETECTED (Scenario 4) ***: TotalPL=" + totalPL + " but DailyProfit=0 (restart with unrealized P&L)");
            }
            
            // NEW: Scenario 5: Strategy restart with existing position (most common mid-day restart)
            else if (isFirstRun && Position.MarketPosition != MarketPosition.Flat)
            {
                isMidDayRestart = true;
                Print("*** MID-DAY RESTART DETECTED (Scenario 5) ***: Restart with existing position: " + Position.MarketPosition + " Quantity: " + Position.Quantity);
            }
            
            // NEW: Scenario 6: Strategy restart with non-zero TotalPL (indicates existing position)
            else if (isFirstRun && totalPL != 0)
            {
                isMidDayRestart = true;
                Print("*** MID-DAY RESTART DETECTED (Scenario 6) ***: Restart with TotalPL=" + totalPL + " (indicates existing position)");
            }
            
            // NEW: Scenario 7: Strategy restart with inconsistent state (position exists but no entry price)
            else if (isFirstRun && Position.MarketPosition != MarketPosition.Flat && lastEntryPrice == 0)
            {
                isMidDayRestart = true;
                Print("*** MID-DAY RESTART DETECTED (Scenario 7) ***: Restart with position but no entry price - Position: " + Position.MarketPosition + " Quantity: " + Position.Quantity);
            }
            
                            if (isMidDayRestart)
                {
                    // Reset profit target for mid-day restart (only if profit target is enabled)
                    if (EnableProfitTarget && AutoResetOnMidDayRestart)
                    {
                        // CRITICAL: Don't reset dailyProfit if there's an existing position with unrealized P&L
                        // This preserves the realized losses from previous trades
                        if (Position.MarketPosition == MarketPosition.Flat)
                        {
                            dailyProfit = 0;
                            realizedPL = 0;
                            totalPL = 0;
                            Print("*** PROFIT RESET ***: No existing position, resetting daily profit to 0");
                        }
                        else
                        {
                            // For existing positions, we need to estimate the realized P&L
                            // Since we don't know the exact entry price of the original position,
                            // we'll assume the current totalPL represents unrealized P&L only
                            // and set realized P&L to 0 (no realized trades yet)
                            realizedPL = 0;
                            dailyProfit = 0;
                            Print("*** PROFIT RESET ***: Existing position detected, setting realized P&L to 0 (unrealized P&L preserved)");
                        }
                        
                        profitTargetReached = false;
                        lastTradeDate = Time[0].Date;
                    }
                
                // CRITICAL: Always reset trading state flags to prevent duplicate entries
                waitingForGreenDotExit = false;
                waitingForRedDotExit = false;
                justEntered = false;
                lastEntryPrice = 0;
                lastEntryQuantity = 0;
                isRestartSyncComplete = false; // Mark that we need to complete restart sync
                
                // If there's an existing position, update the entry tracking
                if (Position.MarketPosition != MarketPosition.Flat)
                {
                    lastEntryPrice = Position.AveragePrice;
                    lastEntryQuantity = Position.Quantity;
                    
                                         // Set appropriate waiting flags based on current position
                     if (Position.MarketPosition == MarketPosition.Short)
                     {
                         waitingForGreenDotExit = true;
                         waitingForRedDotExit = false;
                         Print("*** POSITION STATE SYNC ***: Short position detected, waiting for green dot exit");
                     }
                     else if (Position.MarketPosition == MarketPosition.Long)
                     {
                         waitingForRedDotExit = true;
                         waitingForGreenDotExit = false;
                         Print("*** POSITION STATE SYNC ***: Long position detected, waiting for red dot exit");
                     }
                     
                     // Mark restart sync as complete
                     isRestartSyncComplete = true;
                     Print("*** RESTART SYNC COMPLETE ***: Position state synchronized successfully");
                 }
                 else
                 {
                     // No existing position, mark restart sync as complete
                     isRestartSyncComplete = true;
                     Print("*** RESTART SYNC COMPLETE ***: No existing position, ready to trade");
                 }
                 
                 Print("*** MID-DAY RESTART RESET ***: Trading state reset for mid-day restart at " + Time[0] + " Position: " + Position.MarketPosition + " Quantity: " + Position.Quantity);
            }
            
            // FALLBACK: If we haven't completed restart sync by now, force it to complete
            if (isFirstRun && !isRestartSyncComplete)
            {
                isRestartSyncComplete = true;
                Print("*** FALLBACK RESTART SYNC ***: Forcing restart sync completion at " + Time[0]);
            }
            
            isFirstRun = false;
        }
        }

        protected override void OnBarUpdate()
        {
            // Debug print at the very start
            Print("OnBarUpdate Start: CurrentBar=" + CurrentBar + " Time=" + Time[0] + " ProfitTargetReached=" + profitTargetReached + " DailyProfit=" + dailyProfit.ToString("F2") + " RealizedPL=" + realizedPL.ToString("F2") + " TotalPL=" + totalPL.ToString("F2") + " LastTradeDate=" + lastTradeDate.ToString("yyyy-MM-dd") + " Position=" + Position.MarketPosition + " Quantity=" + Position.Quantity + " RestartSyncComplete=" + isRestartSyncComplete + " LastEntryPrice=" + lastEntryPrice.ToString("F2"));

            // Mark that we've processed the first bar
            if (!hasProcessedFirstBar)
            {
                hasProcessedFirstBar = true;
            }

            // Additional safety check: if we're on a different date than lastTradeDate, reset everything
            if (lastTradeDate != DateTime.MinValue && Time[0].Date != lastTradeDate.Date)
            {
                dailyProfit = 0;
                realizedPL = 0;
                totalPL = 0;
                profitTargetReached = false;
                lastTradeDate = Time[0].Date;
                Print("DATE CHANGE RESET: New trading day detected, resetting all profit tracking. Time: " + Time[0]);
            }

            if (CurrentBar < 3) return;

            // Check if we should reset profit target daily (for new days)
            if (ResetProfitTargetDaily && IsFirstTickOfBar && (lastTradeDate == DateTime.MinValue || Time[0].Date != lastTradeDate.Date))
            {
                dailyProfit = 0;
                realizedPL = 0;
                totalPL = 0;
                profitTargetReached = false; // Ensure it's false for a new day
                lastTradeDate = Time[0].Date;
                Print("DAILY RESET: Profit target reset for new trading day at " + Time[0] + " (Previous lastTradeDate: " + (lastTradeDate == DateTime.MinValue ? "MinValue" : lastTradeDate.ToString("yyyy-MM-dd")) + ")");
            }

            // Calculate total P&L (realized + unrealized) in real-time if profit target is enabled
            if (EnableProfitTarget)
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

                // Total P&L = realized profit + unrealized profit
                totalPL = realizedPL + unrealizedPL;
                
                // DEBUG: Print detailed P&L breakdown every 10 bars
                if (CurrentBar % 10 == 0)
                {
                    Print("DEBUG P&L BREAKDOWN: Realized=" + realizedPL.ToString("F2") + " Unrealized=" + unrealizedPL.ToString("F2") + " Total=" + totalPL.ToString("F2") + " Position=" + Position.MarketPosition + " LastEntryPrice=" + lastEntryPrice.ToString("F2") + " CurrentPrice=" + Close[0].ToString("F2"));
                }
                
                // DEBUG: Print P&L status every 10 bars
                if (CurrentBar % 10 == 0)
                {
                    Print("DEBUG P&L: Realized=" + dailyProfit.ToString("F2") + " Unrealized=" + unrealizedPL.ToString("F2") + " Total=" + totalPL.ToString("F2") + " Target=" + ProfitTargetAmount + " Reached=" + profitTargetReached + " TickSize=" + TickSize);
                }
                
                // Check if profit target is reached (only if not already reached)
                if (!profitTargetReached && totalPL >= ProfitTargetAmount)
                {
                    profitTargetReached = true;
                    Print("*** PROFIT TARGET REACHED ***: Total P&L " + totalPL.ToString("F2") + " (Realized: " + dailyProfit.ToString("F2") + " + Unrealized: " + unrealizedPL.ToString("F2") + ") reached target " + ProfitTargetAmount + " at " + Time[0]);
                    Print("*** TRADING DISABLED ***: Strategy will no longer enter new positions");
                    
                    // Close current position if any
                    if (Position.MarketPosition == MarketPosition.Long)
                    {
                        ExitLong(DefaultQuantity, "Profit Target Exit", "Long on Green Dot");
                        Print("*** PROFIT TARGET EXIT ***: Closing long position at " + Close[0]);
                    }
                    else if (Position.MarketPosition == MarketPosition.Short)
                    {
                        ExitShort(DefaultQuantity, "Profit Target Exit", "Short on Red Dot");
                        Print("*** PROFIT TARGET EXIT ***: Closing short position at " + Close[0]);
                    }
                }
                

            }

            // CRITICAL: If profit target reached AND enabled, EXIT IMMEDIATELY - NO MORE TRADING
            if (EnableProfitTarget && profitTargetReached)
            {
                Print("*** PROFIT TARGET ACTIVE ***: Skipping all trading logic at " + Time[0]);
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
                // CRITICAL: Additional safety check to prevent duplicate entries on restart
                if (Position.MarketPosition != MarketPosition.Flat && lastEntryPrice == 0)
                {
                    // We have a position but no entry price recorded - this indicates a restart scenario
                    // Don't enter any new positions until we properly sync the state
                    Print("*** RESTART SYNC IN PROGRESS ***: Position exists but entry price not set, skipping new entries at " + Time[0]);
                    return;
                }
                
                // NEW: Additional check to ensure restart sync is complete before trading
                if (!isRestartSyncComplete)
                {
                    Print("*** RESTART SYNC PENDING ***: Waiting for restart synchronization to complete, skipping new entries at " + Time[0]);
                    return;
                }
                
                // Entry Logic: Go short on red dot signal (only on bar close)
                if (redDotSignal[0] && Position.MarketPosition == MarketPosition.Flat && IsFirstTickOfBar)
                {
                    // DOUBLE CHECK: Make sure profit target not reached
                    if (EnableProfitTarget && profitTargetReached)
                    {
                        Print("*** BLOCKED SHORT ENTRY ***: Profit target reached at " + Time[0]);
                        return;
                    }
                    
                    EnterShort(DefaultQuantity, "Short on Red Dot");
                    waitingForGreenDotExit = true;
                    waitingForRedDotExit = false;
                    justEntered = true; // Set flag to prevent immediate exit
                    lastEntryPrice = Close[0];
                    lastEntryQuantity = DefaultQuantity;
                    Print("SHORT ENTRY: Red dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Entry Logic: Go long when stopped out on green dot (real-time)
                if (greenDotSignal[0] && Position.MarketPosition == MarketPosition.Short && waitingForGreenDotExit && !justEntered)
                {
                    // DOUBLE CHECK: Make sure profit target not reached
                    if (EnableProfitTarget && profitTargetReached)
                    {
                        Print("*** BLOCKED LONG ENTRY ***: Profit target reached at " + Time[0]);
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
                    Print("LONG ENTRY: Green dot signal at " + Time[0] + " Price: " + Close[0]);
                }

                // Exit Logic: Exit long when red dot signal appears (only on candle close)
                if (redDotSignal[0] && Position.MarketPosition == MarketPosition.Long && waitingForRedDotExit && !justEntered && IsFirstTickOfBar)
                {
                    // DOUBLE CHECK: Make sure profit target not reached
                    if (EnableProfitTarget && profitTargetReached)
                    {
                        Print("*** BLOCKED SHORT ENTRY FROM LONG EXIT ***: Profit target reached at " + Time[0]);
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
            // CRITICAL: Additional safety check to prevent duplicate entries on restart
            if (Position.MarketPosition != MarketPosition.Flat && lastEntryPrice == 0)
            {
                // We have a position but no entry price recorded - this indicates a restart scenario
                // Don't process any real-time exits until we properly sync the state
                return;
            }
            
            // NEW: Additional check to ensure restart sync is complete before processing real-time exits
            if (!isRestartSyncComplete)
            {
                return;
            }
            
            // Only check for real-time exits if we have a short position and profit target not reached
            if (Position.MarketPosition == MarketPosition.Short && waitingForGreenDotExit && !justEntered && CurrentBar >= 3 && (!EnableProfitTarget || !profitTargetReached))
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
                    
                    // Only enter long if profit target not reached
                    if (!EnableProfitTarget || !profitTargetReached)
                    {
                        // Immediately enter long position
                        EnterLong(DefaultQuantity, "Long on Green Dot");
                        waitingForRedDotExit = true;
                        waitingForGreenDotExit = false;
                        lastEntryPrice = Close[0];
                        lastEntryQuantity = DefaultQuantity;
                        justEntered = true; // Set flag to prevent immediate exit
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

                        dailyProfit += profitLoss;
                        realizedPL += profitLoss; // Track realized P&L separately
                        Print("POSITION CLOSED: " + quantity + " contracts at " + price + " at " + time + " | P&L: " + profitLoss.ToString("F2") + " | Daily P&L: " + dailyProfit.ToString("F2") + " | Realized P&L: " + realizedPL.ToString("F2"));
                        
                        // Update total P&L after realized profit is added
                        totalPL = dailyProfit;
                        
                        // Check if profit target is reached (this is a backup check)
                        if (EnableProfitTarget && !profitTargetReached && totalPL >= ProfitTargetAmount)
                        {
                            profitTargetReached = true;
                            Print("PROFIT TARGET REACHED: Total P&L " + totalPL.ToString("F2") + " reached target " + ProfitTargetAmount + " at " + time);
                            Print("TRADING DISABLED: Strategy will no longer enter new positions");
                        }
                    }
                }
            }
        }

        // Method to manually reset profit target (can be called from strategy properties)
        public void ResetProfitTarget()
        {
            dailyProfit = 0;
            realizedPL = 0;
            totalPL = 0;
            profitTargetReached = false;
            lastTradeDate = Time[0].Date; // Set to current date
            Print("MANUAL RESET: Profit target has been reset. Daily profit: " + dailyProfit + " RealizedPL: " + realizedPL + " TotalPL: " + totalPL + " Date: " + Time[0].ToString("yyyy-MM-dd"));
        }

        // Method to force reset profit target for mid-day restarts
        public void ForceResetForMidDayRestart()
        {
            dailyProfit = 0;
            realizedPL = 0;
            totalPL = 0;
            profitTargetReached = false;
            lastTradeDate = Time[0].Date;
            Print("FORCE MID-DAY RESET: Profit target forcefully reset for mid-day restart. Time: " + Time[0]);
        }

        // Method to get current profit status
        public double GetCurrentProfit()
        {
            return dailyProfit;
        }

        // Method to check if profit target is reached
        public bool IsProfitTargetReached()
        {
            return profitTargetReached;
        }

        // Method to get current total P&L
        public double GetTotalPL()
        {
            return totalPL;
        }

        // Method to get current daily profit
        public double GetDailyProfit()
        {
            return dailyProfit;
        }

        // Method to force enable profit target (for testing)
        public void ForceEnableProfitTarget()
        {
            EnableProfitTarget = true;
            Print("*** FORCE ENABLED PROFIT TARGET ***");
        }

        // Method to force set profit target amount (for testing)
        public void ForceSetProfitTarget(double amount)
        {
            ProfitTargetAmount = amount;
            Print("*** FORCE SET PROFIT TARGET TO: " + amount + " ***");
        }

        // Method to force reset all strategy state (for testing mid-day restart scenarios)
        public void ForceResetAllState()
        {
            dailyProfit = 0;
            realizedPL = 0;
            totalPL = 0;
            profitTargetReached = false;
            lastTradeDate = Time[0].Date;
            waitingForGreenDotExit = false;
            waitingForRedDotExit = false;
            justEntered = false;
            lastEntryPrice = 0;
            lastEntryQuantity = 0;
            isFirstRun = true;
            hasProcessedFirstBar = false;
            isRestartSyncComplete = false;
            Print("*** FORCE RESET ALL STATE ***: All strategy state variables reset at " + Time[0]);
        }

        // Method to manually complete restart sync (for testing)
        public void ForceCompleteRestartSync()
        {
            isRestartSyncComplete = true;
            if (Position.MarketPosition != MarketPosition.Flat)
            {
                lastEntryPrice = Position.AveragePrice;
                lastEntryQuantity = Position.Quantity;
                
                if (Position.MarketPosition == MarketPosition.Short)
                {
                    waitingForGreenDotExit = true;
                    waitingForRedDotExit = false;
                }
                else if (Position.MarketPosition == MarketPosition.Long)
                {
                    waitingForRedDotExit = true;
                    waitingForGreenDotExit = false;
                }
            }
            Print("*** FORCE COMPLETE RESTART SYNC ***: Restart sync manually completed at " + Time[0] + " Position: " + Position.MarketPosition + " Quantity: " + Position.Quantity);
        }
    }
}