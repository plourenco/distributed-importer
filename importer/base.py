from datetime import datetime
from marshmallow import EXCLUDE
import requests
from importer.config import INTERNAL_API_KEY, INTERNAL_API_URL, MAILCHIMP_API_KEY, MAILCHIMP_API_URL

from importer.schemas import ExternalMemberSchema, MemberSchema


class Importer:
    def create_session(self):
        session = requests.Session()
        session.headers = {
            'Authorization': f'Bearer {MAILCHIMP_API_KEY}'
        }
        return session

    def get_members(self, session, list_key, offset=0, count=10, since_last_changed=None):
        params = {'offset': offset, 'count': count}
        if since_last_changed and type(since_last_changed) is datetime:
            params['since_last_changed'] = since_last_changed.isoformat()
        resp = session.get(
            f'{MAILCHIMP_API_URL}/lists/{list_key}/members', params=params)
        data = resp.json()
        return ExternalMemberSchema(unknown=EXCLUDE, many=True).load(data.get('members')), data.get('total_items')


class Consumer:
    def create_session(self):
        session = requests.Session()
        session.headers = {
            'Authorization': INTERNAL_API_KEY
        }
        return session

    def run(self, records):
        session = self.create_session()
        resp = session.post(f'{INTERNAL_API_URL}/record',
                            json=MemberSchema(many=True).dump(records))
        resp.raise_for_status()
        json = resp.json()
        return json.get('response')
