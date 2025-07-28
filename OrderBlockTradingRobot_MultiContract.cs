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
        private double stopLossLevel = 0;
        private bool waitingForGreenDotExit = false;
        private bool justEntered = false; // Flag to prevent immediate exit
        private bool entryProcessed = false; // Flag to prevent multiple entries
        private double entryPrice = 0;
        private double trailingStopLevel = 0;
        private bool trailingStopSet = false;
        private int remainingContracts = 0;

        [Range(1, int.MaxValue), NinjaScriptProperty]
        [Display(ResourceType = typeof(Custom.Resource), Name = "Number of Contracts", GroupName = "Parameters", Order = 0)]
        public int NumberOfContracts { get; set; }

        [Range(0, int.MaxValue), NinjaScriptProperty]
        [Display(ResourceType = typeof(Custom.Resource), Name = "Contracts to Trail", GroupName = "Parameters", Order = 1)]
        public int ContractsToTrail { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Order Block Trading Robot - Multi Contract Short Only";
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
                
                // Set default number of contracts
                NumberOfContracts = 1;
                ContractsToTrail = 0;
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

            // Trading Logic
            if (State == State.Realtime || State == State.Historical)
            {
                // Entry Logic: Go short on red dot signal
                if (redDotSignal[0] && !shortPositionOpen && !entryProcessed)
                {
                    EnterShort(NumberOfContracts, "Short on Red Dot");
                    shortPositionOpen = true;
                    waitingForGreenDotExit = true;
                    justEntered = true; // Set flag to prevent immediate exit
                    entryProcessed = true; // Prevent multiple entries
                    entryPrice = Close[0];
                    trailingStopSet = false;
                    remainingContracts = NumberOfContracts;
                    Print("SHORT ENTRY: " + NumberOfContracts + " contracts at " + Time[0] + " Price: " + Close[0]);
                }

                // Trailing Stop Logic: Only if we have contracts to trail and remaining contracts
                if (shortPositionOpen && !justEntered && ContractsToTrail > 0 && remainingContracts > ContractsToTrail)
                {
                    // Check if current candle is red (close < open)
                    if (Close[0] < Open[0])
                    {
                        // Update trailing stop level based on higher high
                        if (!trailingStopSet || High[0] > trailingStopLevel)
                        {
                            trailingStopLevel = High[0];
                            trailingStopSet = true;
                            Print("TRAILING STOP UPDATED: New level at " + trailingStopLevel);
                        }
                    }
                    
                    // Check if trailing stop is hit
                    if (trailingStopSet && High[0] >= trailingStopLevel)
                    {
                        ExitShort(ContractsToTrail, "Trailing Stop", "Short on Red Dot");
                        remainingContracts -= ContractsToTrail;
                        Print("TRAILING STOP HIT: " + ContractsToTrail + " contracts at " + Time[0] + " Level: " + trailingStopLevel + " Remaining: " + remainingContracts);
                        trailingStopSet = false;
                    }
                }

                // Stop Loss Logic: Exit remaining contracts when green dot signal appears
                if (greenDotSignal[0] && shortPositionOpen && waitingForGreenDotExit && !justEntered)
                {
                    stopLossLevel = activeOrderBlockLevel[0];
                    
                    if (remainingContracts > 0)
                    {
                        ExitShort(remainingContracts, "Stop on Green Dot", "Short on Red Dot");
                        Print("STOP LOSS: " + remainingContracts + " contracts at " + Time[0] + " Stop Level: " + stopLossLevel);
                    }
                    
                    shortPositionOpen = false;
                    waitingForGreenDotExit = false;
                    trailingStopSet = false;
                    remainingContracts = 0;
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
                else if (marketPosition == MarketPosition.Flat)
                {
                    Print("POSITION CLOSED: " + quantity + " contracts at " + price + " at " + time);
                }
            }
        }
    }
}