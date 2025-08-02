# Trading Bot Configuration
# Bullish Order Block Strategy Configuration

class TradingConfig:
    # Symbol and Timeframe
    SYMBOL = "QQQ"  # Trading symbol
    TIMEFRAME = "1m"  # Data timeframe (1m, 5m, 15m, 1h, 1d)
    
    # Capital and Risk Management
    INITIAL_CAPITAL = 10000.0  # Starting capital
    POSITION_SIZE = 0.1  # Fraction of capital to risk per trade (0.1 = 10%)
    MAX_POSITION_SIZE = 0.25  # Maximum position size as fraction of capital
    
    # Order Block Detection Parameters
    INEFFICIENCY_MULTIPLIER = 1.5  # Shadow gap multiplier for inefficiency detection
    LOOKBACK_PERIODS = 3  # Number of periods to look back for BOS/CHOCH
    
    # Stop Loss and Risk Management
    DEFAULT_STOP_LOSS_PCT = 0.01  # Default stop loss percentage (1%)
    TRAILING_STOP = True  # Enable trailing stop
    TRAILING_STOP_PCT = 0.005  # Trailing stop percentage (0.5%)
    
    # Trading Logic
    ENABLE_SHORTING = True  # Enable short positions
    AUTO_CYCLE = True  # Enable automatic long/short cycling
    
    # Data and Execution
    UPDATE_INTERVAL = 60  # Seconds between data updates in live mode
    DATA_SOURCE = "yfinance"  # Data source (yfinance, alpaca, etc.)
    
    # Logging and Monitoring
    LOG_LEVEL = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR)
    SAVE_TRADES = True  # Save trade history to file
    TRADE_LOG_FILE = "trade_history.csv"  # File to save trade history
    
    # Backtest Settings
    BACKTEST_START_DATE = "2024-01-01"  # Default backtest start date
    BACKTEST_END_DATE = "2024-12-31"  # Default backtest end date
    
    # Alert Settings
    ENABLE_ALERTS = True  # Enable trading alerts
    ALERT_EMAIL = None  # Email for alerts (if configured)
    
    # Performance Tracking
    TRACK_METRICS = True  # Enable performance metrics tracking
    CALCULATE_SHARPE = True  # Calculate Sharpe ratio
    CALCULATE_MAX_DRAWDOWN = True  # Calculate maximum drawdown

# Strategy-specific configurations
class BullishOrderBlockConfig:
    """Configuration specific to Bullish Order Block strategy"""
    
    # Order Block Detection
    MIN_ORDER_BLOCK_SIZE = 0.001  # Minimum size for order block (0.1%)
    MAX_ORDER_BLOCKS = 10  # Maximum number of order blocks to track
    
    # Mitigation Logic
    MITIGATION_CONFIRMATION = 1  # Number of candles to confirm mitigation
    PARTIAL_MITIGATION = False  # Allow partial mitigation
    
    # Entry/Exit Rules
    ENTRY_CONFIRMATION = 1  # Number of candles to confirm entry
    EXIT_CONFIRMATION = 1  # Number of candles to confirm exit
    
    # Risk Management
    MAX_DAILY_LOSS = 0.05  # Maximum daily loss (5%)
    MAX_WEEKLY_LOSS = 0.15  # Maximum weekly loss (15%)
    DAILY_LOSS_RESET = True  # Reset daily loss counter each day
    
    # Position Sizing
    DYNAMIC_POSITION_SIZING = True  # Adjust position size based on volatility
    VOLATILITY_LOOKBACK = 20  # Periods for volatility calculation
    MIN_POSITION_SIZE = 0.05  # Minimum position size (5%)
    
    # Market Conditions
    TREND_FILTER = True  # Use trend filter for entries
    TREND_PERIOD = 50  # Period for trend calculation
    VOLUME_FILTER = False  # Use volume filter
    MIN_VOLUME_MULTIPLIER = 1.5  # Minimum volume multiplier

# Risk Management Configuration
class RiskConfig:
    """Risk management configuration"""
    
    # Position Limits
    MAX_OPEN_POSITIONS = 1  # Maximum number of open positions
    MAX_CORRELATED_POSITIONS = 1  # Maximum correlated positions
    
    # Loss Limits
    MAX_SINGLE_LOSS = 0.02  # Maximum single trade loss (2%)
    MAX_CONSECUTIVE_LOSSES = 5  # Maximum consecutive losses before pause
    
    # Time-based Limits
    MAX_HOLDING_TIME = 24  # Maximum holding time in hours
    MIN_HOLDING_TIME = 0  # Minimum holding time in minutes
    
    # Market Hours
    TRADING_HOURS = {
        "start": "09:30",
        "end": "16:00",
        "timezone": "US/Eastern"
    }
    
    # Weekend and Holiday Handling
    TRADE_WEEKENDS = False  # Allow weekend trading
    TRADE_HOLIDAYS = False  # Allow holiday trading
    
    # Emergency Controls
    EMERGENCY_STOP = False  # Emergency stop flag
    EMERGENCY_STOP_THRESHOLD = 0.20  # Emergency stop threshold (20%)

# Notification Configuration
class NotificationConfig:
    """Notification and alert configuration"""
    
    # Email Notifications
    EMAIL_ENABLED = False
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_USERNAME = ""
    EMAIL_PASSWORD = ""
    EMAIL_RECIPIENTS = []
    
    # Discord Notifications
    DISCORD_ENABLED = False
    DISCORD_WEBHOOK_URL = ""
    
    # Telegram Notifications
    TELEGRAM_ENABLED = False
    TELEGRAM_BOT_TOKEN = ""
    TELEGRAM_CHAT_ID = ""
    
    # Notification Events
    NOTIFY_ON_ENTRY = True
    NOTIFY_ON_EXIT = True
    NOTIFY_ON_STOP_LOSS = True
    NOTIFY_ON_DAILY_SUMMARY = True
    NOTIFY_ON_ERROR = True
    
    # Notification Frequency
    NOTIFICATION_COOLDOWN = 300  # Seconds between notifications (5 minutes)
    DAILY_SUMMARY_TIME = "17:00"  # Time for daily summary (5 PM)