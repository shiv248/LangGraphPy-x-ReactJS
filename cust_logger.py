# cust_logger.py

import logging
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama
init(autoreset=True)

# Custom logging formatter
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.INFO: Fore.GREEN,
        logging.ERROR: Fore.RED,
        logging.WARNING: Fore.YELLOW,
    }
    FILE_COLOR = Fore.CYAN + Style.BRIGHT  # Cyan + Bold

    def format(self, record):
        # Color only the level name
        log_color = self.COLORS.get(record.levelno, Style.RESET_ALL)
        levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"

        # Format filename and line number with fixed width (e.g., 20 for filename, 5 for line number)
        filename_lineno = f"{self.FILE_COLOR}{record.filename}:{record.lineno:<5}{Style.RESET_ALL}"

        # Add the timestamp manually in the JSON log output
        record.timestamp = datetime.now().isoformat()

        # Set the formatted levelname and filename back to the record
        record.levelname = levelname
        record.filename_lineno = filename_lineno

        return super().format(record)

# Configure logging
formatter = ColorFormatter('%(levelname)s:     %(filename_lineno)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Create and configure the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Set logging levels for other libraries to avoid too much verbosity
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
