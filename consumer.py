import os
import requests
from dotenv import load_dotenv
from schemas import MemberSchema

load_dotenv()

OMETRIA_API_URL = os.getenv('OMETRIA_API_URL')
OMETRIA_API_KEY = os.getenv('OMETRIA_API_KEY')


class Consumer:
    def create_session(self):
        session = requests.Session()
        session.headers = {
            'Authorization': OMETRIA_API_KEY
        }
        return session

    def run(self, records):
        session = self.create_session()
        resp = session.post(f'{OMETRIA_API_URL}/record',
                            json=MemberSchema(many=True).dump(records))
        resp.raise_for_status()
        json = resp.json()
        return json.get('response')
