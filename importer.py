import os
from marshmallow import EXCLUDE
import requests

from schemas import ExternalMemberSchema

# Dev dependencies
# Docker swarm to scale horizontally

MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_API_URL = os.getenv('MAILCHIMP_API_URL')


class Importer:
    def create_request_session(self):
        session = requests.Session()
        session.headers = {
            'Authorization': f'Bearer {MAILCHIMP_API_KEY}'
        }
        return session

    def get_members(self, session, list_key, offset=0, count=10, since_last_changed=None):
        params = {'offset': offset, 'count': count}
        if since_last_changed:
            params['since_last_changed'] = since_last_changed.isoformat()
        resp = session.get(
            f'{MAILCHIMP_API_URL}/lists/{list_key}/members', params=params)
        data = resp.json()
        return ExternalMemberSchema(unknown=EXCLUDE, many=True).load(data.get('members')), data.get('total_items')
