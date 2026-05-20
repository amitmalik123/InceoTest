import requests
from typing import Optional, Dict, Any
from utils.settings import settings
from config.stp.stp_moneyin_moneyout.api_endpoints import APIEndpoints


class ApiClient:
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or self._get_base_url()
        self.session = requests.Session()
        self._setup_default_headers()
    
    def _get_base_url(self) -> str:
        return settings.env_vars.get('base_api_url', APIEndpoints.BASE_APPLICATION_API)
    
    def _setup_default_headers(self):
        self.session.headers.update({
            'accept': 'text/plain',
            'Content-Type': 'application/json'
        })
    
    def set_auth_token(self, token: str):
        self.session.headers.update({
            'Authorization': token
        })
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        response = self.session.get(url, params=params, headers=request_headers)
        return response
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        response = self.session.post(url, data=data, json=json, headers=request_headers)
        return response
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        response = self.session.put(url, data=data, json=json, headers=request_headers)
        return response
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        response = self.session.delete(url, headers=request_headers)
        return response
    
    def close(self):
        self.session.close()
