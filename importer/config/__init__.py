import os
from dotenv import load_dotenv


load_dotenv()

INTERNAL_API_URL = os.getenv('INTERNAL_API_URL')
INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY')
MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_API_URL = os.getenv('MAILCHIMP_API_URL')
