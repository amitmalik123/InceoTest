# GraphQL client stub for framework


import requests
from framework.common.logger import get_logger
logger = get_logger(__name__)

class GraphQLClient:
    def __init__(self, base_url, auth_token=None, endpoint='/graphql'):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.endpoint = endpoint

    def query(self, query, variables=None):
        url = f"{self.base_url}{self.endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        payload = {
            'query': query,
            'variables': variables or {}
        }
        logger.info(f"GraphQL Request to {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logger.info(f"GraphQL Response: {response.status_code}")
        return response.json()
