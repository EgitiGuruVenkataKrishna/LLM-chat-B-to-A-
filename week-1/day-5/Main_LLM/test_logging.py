import logging

# Step 1: Configure logging (do this ONCE at the start)
logging.basicConfig(
    level=logging.INFO,  # Show INFO and above (INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # How it looks
    handlers=[
        logging.FileHandler('app.log'),  # Save to file
        logging.StreamHandler()          # Also show in terminal
    ]
)

# Step 2: Use it in your code
logging.info("App started")

try:
    result = 10 / 2
    logging.info(f"Calculation successful: {result}")
except Exception as e:
    logging.error(f"Calculation failed: {e}")

logging.info("App finished")