import pandas as pd
import numpy as np
import yfinance as yf
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PositionType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"

@dataclass
class OrderBlock:
    level: float
    timestamp: datetime
    is_bullish: bool
    is_mitigated: bool = False

@dataclass
class Trade:
    entry_price: float
    entry_time: datetime
    position_type: PositionType
    stop_loss: float
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None

class BullishOrderBlockBot:
    def __init__(self, symbol: str = "QQQ", timeframe: str = "1m", 
                 initial_capital: float = 10000.0, position_size: float = 0.1):
        """
        Initialize the Bullish Order Block Trading Bot
        
        Args:
            symbol: Trading symbol (default: QQQ)
            timeframe: Data timeframe (default: 1m for 1-minute)
            initial_capital: Starting capital
            position_size: Fraction of capital to risk per trade (0.1 = 10%)
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.position_size = position_size
        
        # Trading state
        self.current_position = PositionType.FLAT
        self.current_trade: Optional[Trade] = None
        self.order_blocks: List[OrderBlock] = []
        self.last_bullish_level: Optional[float] = None
        self.red_dot_plotted = False
        
        # Performance tracking
        self.trades: List[Trade] = []
        self.total_pnl = 0.0
        self.win_count = 0
        self.loss_count = 0
        
        # Data storage
        self.price_data: pd.DataFrame = pd.DataFrame()
        self.is_running = False
        
        logger.info(f"Bot initialized for {symbol} with ${initial_capital:,.2f} capital")
    
    def fetch_data(self, period: str = "1d") -> pd.DataFrame:
        """Fetch real-time or historical data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period=period, interval=self.timeframe)
            
            if data.empty:
                logger.error(f"No data received for {self.symbol}")
                return pd.DataFrame()
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_columns):
                logger.error(f"Missing required columns in data: {data.columns}")
                return pd.DataFrame()
            
            # Rename columns to match our logic
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def detect_bullish_order_block(self, data: pd.DataFrame) -> Tuple[bool, float]:
        """
        Detect Bullish Order Block based on the ThinkorSwim logic
        
        Returns:
            Tuple of (is_bullish_order_block, order_block_level)
        """
        if len(data) < 4:
            return False, None
        
        # Get current and previous candle data
        current = data.iloc[-1]
        prev1 = data.iloc[-2]
        prev2 = data.iloc[-3]
        prev3 = data.iloc[-4]
        
        # Inefficiency: Shadow gap > 1.5x candle body
        inefficiency = abs(prev1['high'] - current['low']) > abs(prev1['close'] - prev1['open']) * 1.5
        
        # Bullish Break of Structure (BOS) and Change of Character (CHOCH)
        recent_highs = [prev2['high'], prev3['high']]
        recent_lows = [prev2['low'], prev3['low']]
        
        bos_up = current['high'] > max(recent_highs)
        choch_up = (current['low'] < min(recent_lows) and 
                   current['high'] > max(recent_highs))
        
        # Bullish Order Block detection
        is_bullish_order_block = (inefficiency and (bos_up or choch_up))
        
        order_block_level = prev1['open'] if is_bullish_order_block else None
        
        return is_bullish_order_block, order_block_level
    
    def check_mitigation(self, data: pd.DataFrame, order_block: OrderBlock) -> bool:
        """Check if the order block has been mitigated (price closed below for bullish)"""
        if len(data) < 2:
            return False
        
        current_close = data.iloc[-1]['close']
        
        if order_block.is_bullish:
            return current_close < order_block.level
        else:
            return current_close > order_block.level
    
    def should_enter_long(self, data: pd.DataFrame) -> bool:
        """Check if we should enter a long position (green dot)"""
        if self.current_position != PositionType.FLAT:
            return False
        
        is_bullish, level = self.detect_bullish_order_block(data)
        
        if is_bullish and level is not None:
            # Check if this is a new bullish order block
            if (not self.order_blocks or 
                self.order_blocks[-1].level != level or
                self.order_blocks[-1].timestamp != data.index[-2]):
                
                logger.info(f"Bullish Order Block detected at level: {level:.2f}")
                return True
        
        return False
    
    def should_exit_long_enter_short(self, data: pd.DataFrame) -> bool:
        """Check if we should exit long and enter short (red dot)"""
        if self.current_position != PositionType.LONG:
            return False
        
        if not self.last_bullish_level:
            return False
        
        current_close = data.iloc[-1]['close']
        
        # Price closed below the last bullish order block level
        if current_close < self.last_bullish_level and not self.red_dot_plotted:
            logger.info(f"Price closed below bullish order block level: {self.last_bullish_level:.2f}")
            self.red_dot_plotted = True
            return True
        
        return False
    
    def should_exit_short_enter_long(self, data: pd.DataFrame) -> bool:
        """Check if we should exit short and enter long (stop at green dot)"""
        if self.current_position != PositionType.SHORT:
            return False
        
        if not self.last_bullish_level:
            return False
        
        current_high = data.iloc[-1]['high']
        
        # Price hit the bullish order block level (stop loss for short)
        if current_high >= self.last_bullish_level:
            logger.info(f"Short position stopped out at bullish order block level: {self.last_bullish_level:.2f}")
            return True
        
        return False
    
    def execute_trade(self, position_type: PositionType, entry_price: float, 
                     stop_loss: float, data: pd.DataFrame):
        """Execute a trade"""
        # Close existing position if any
        if self.current_trade:
            self.close_position(data.iloc[-1]['close'], data.index[-1])
        
        # Calculate position size
        risk_amount = self.capital * self.position_size
        stop_distance = abs(entry_price - stop_loss)
        shares = risk_amount / stop_distance if stop_distance > 0 else 0
        
        # Create new trade
        self.current_trade = Trade(
            entry_price=entry_price,
            entry_time=data.index[-1],
            position_type=position_type,
            stop_loss=stop_loss
        )
        
        self.current_position = position_type
        
        logger.info(f"Executed {position_type.value} trade: Entry=${entry_price:.2f}, "
                   f"Stop=${stop_loss:.2f}, Shares={shares:.2f}")
    
    def close_position(self, exit_price: float, exit_time: datetime):
        """Close the current position"""
        if not self.current_trade:
            return
        
        self.current_trade.exit_price = exit_price
        self.current_trade.exit_time = exit_time
        
        # Calculate P&L
        if self.current_trade.position_type == PositionType.LONG:
            self.current_trade.pnl = (exit_price - self.current_trade.entry_price) * 100
        else:  # SHORT
            self.current_trade.pnl = (self.current_trade.entry_price - exit_price) * 100
        
        # Update statistics
        self.total_pnl += self.current_trade.pnl
        if self.current_trade.pnl > 0:
            self.win_count += 1
        else:
            self.loss_count += 1
        
        # Store trade
        self.trades.append(self.current_trade)
        
        logger.info(f"Closed {self.current_trade.position_type.value} position: "
                   f"Exit=${exit_price:.2f}, P&L=${self.current_trade.pnl:.2f}")
        
        # Reset for next trade
        self.current_trade = None
        self.current_position = PositionType.FLAT
    
    def process_data(self, data: pd.DataFrame):
        """Process new data and execute trading logic"""
        if data.empty or len(data) < 4:
            return
        
        # Update order blocks
        is_bullish, level = self.detect_bullish_order_block(data)
        if is_bullish and level is not None:
            new_order_block = OrderBlock(
                level=level,
                timestamp=data.index[-2],
                is_bullish=True
            )
            self.order_blocks.append(new_order_block)
            self.last_bullish_level = level
            self.red_dot_plotted = False
        
        # Check for mitigation of existing order blocks
        for order_block in self.order_blocks:
            if not order_block.is_mitigated:
                order_block.is_mitigated = self.check_mitigation(data, order_block)
        
        # Trading logic
        if self.should_enter_long(data):
            # Enter long position
            current_price = data.iloc[-1]['close']
            stop_loss = current_price * 0.99  # 1% stop loss
            self.execute_trade(PositionType.LONG, current_price, stop_loss, data)
            
        elif self.should_exit_long_enter_short(data):
            # Exit long and enter short
            current_price = data.iloc[-1]['close']
            self.close_position(current_price, data.index[-1])
            
            # Enter short position
            stop_loss = self.last_bullish_level
            self.execute_trade(PositionType.SHORT, current_price, stop_loss, data)
            
        elif self.should_exit_short_enter_long(data):
            # Exit short and enter long
            current_price = self.last_bullish_level
            self.close_position(current_price, data.index[-1])
            
            # Enter long position
            stop_loss = current_price * 0.99
            self.execute_trade(PositionType.LONG, current_price, stop_loss, data)
    
    def run_backtest(self, start_date: str, end_date: str):
        """Run backtest on historical data"""
        logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        # Fetch historical data
        ticker = yf.Ticker(self.symbol)
        data = ticker.history(start=start_date, end=end_date, interval=self.timeframe)
        
        if data.empty:
            logger.error("No data available for backtest")
            return
        
        # Rename columns to match our logic
        data = data.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Process data
        for i in range(4, len(data)):
            window_data = data.iloc[:i+1]
            self.process_data(window_data)
        
        # Print results
        self.print_performance()
    
    def run_live(self, update_interval: int = 60):
        """Run live trading (simulated)"""
        logger.info("Starting live trading simulation")
        self.is_running = True
        
        while self.is_running:
            try:
                # Fetch latest data
                data = self.fetch_data(period="1d")
                
                if not data.empty:
                    self.process_data(data)
                    
                    # Print current status
                    self.print_status()
                
                # Wait for next update
                time.sleep(update_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping live trading")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Error in live trading: {e}")
                time.sleep(update_interval)
    
    def print_status(self):
        """Print current trading status"""
        print(f"\n{'='*50}")
        print(f"Symbol: {self.symbol}")
        print(f"Current Position: {self.current_position.value}")
        print(f"Capital: ${self.capital:,.2f}")
        print(f"Total P&L: ${self.total_pnl:,.2f}")
        
        if self.current_trade:
            print(f"Current Trade: {self.current_trade.position_type.value} at ${self.current_trade.entry_price:.2f}")
            print(f"Stop Loss: ${self.current_trade.stop_loss:.2f}")
        
        if self.last_bullish_level:
            print(f"Last Bullish Level: ${self.last_bullish_level:.2f}")
        
        print(f"Total Trades: {len(self.trades)}")
        print(f"Win Rate: {self.win_count/(self.win_count + self.loss_count)*100:.1f}%" if (self.win_count + self.loss_count) > 0 else "Win Rate: N/A")
        print(f"{'='*50}\n")
    
    def print_performance(self):
        """Print detailed performance metrics"""
        print(f"\n{'='*60}")
        print(f"BACKTEST RESULTS FOR {self.symbol}")
        print(f"{'='*60}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Capital: ${self.capital:,.2f}")
        print(f"Total Return: {((self.capital - self.initial_capital) / self.initial_capital) * 100:.2f}%")
        print(f"Total P&L: ${self.total_pnl:,.2f}")
        print(f"Total Trades: {len(self.trades)}")
        print(f"Winning Trades: {self.win_count}")
        print(f"Losing Trades: {self.loss_count}")
        print(f"Win Rate: {self.win_count/(self.win_count + self.loss_count)*100:.1f}%" if (self.win_count + self.loss_count) > 0 else "Win Rate: N/A")
        
        if self.trades:
            avg_win = np.mean([t.pnl for t in self.trades if t.pnl > 0]) if any(t.pnl > 0 for t in self.trades) else 0
            avg_loss = np.mean([t.pnl for t in self.trades if t.pnl < 0]) if any(t.pnl < 0 for t in self.trades) else 0
            print(f"Average Win: ${avg_win:.2f}")
            print(f"Average Loss: ${avg_loss:.2f}")
            print(f"Profit Factor: {abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "Profit Factor: N/A")
        
        print(f"{'='*60}\n")

def main():
    """Main function to run the trading bot"""
    # Initialize the bot
    bot = BullishOrderBlockBot(
        symbol="QQQ",
        timeframe="1m",
        initial_capital=10000.0,
        position_size=0.1
    )
    
    # Choose mode: backtest or live
    mode = input("Choose mode (1 for backtest, 2 for live): ").strip()
    
    if mode == "1":
        # Backtest mode
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        bot.run_backtest(start_date, end_date)
        
    elif mode == "2":
        # Live mode
        print("Starting live trading simulation...")
        print("Press Ctrl+C to stop")
        bot.run_live()
        
    else:
        print("Invalid mode selected")

if __name__ == "__main__":
    main()