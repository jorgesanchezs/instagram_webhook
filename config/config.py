#%%
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Configuration file for the application
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 600))
LAST_POST_FILE = os.getenv('LAST_POST_FILE', 'data/last_post.txt')
