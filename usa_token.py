import os
from load_dotenv import load_dotenv

load_dotenv()

kaggle_username=os.getenv('KAGGLE_USERNAME')
kaggle_key = os.getenv('KAGGLE_KEY')
