# SOAP client stub for framework


from zeep import Client as ZeepClient
from zeep.transports import Transport
from zeep.exceptions import Fault
from framework.common.logger import get_logger
logger = get_logger(__name__)

class SoapClient:
    def __init__(self, wsdl_url):
        self.wsdl_url = wsdl_url
        self.soap_client = None
        self._init_soap_client()

    def _init_soap_client(self):
        try:
            transport = Transport()
            self.soap_client = ZeepClient(wsdl=self.wsdl_url, transport=transport)
            logger.info(f"Initialized SOAP client with WSDL: {self.wsdl_url}")
        except Exception as e:
            logger.error(f"Failed to initialize SOAP client: {e}")
            raise

    def call(self, service_name, method_name, *args, **kwargs):
        if not self.soap_client:
            raise RuntimeError("SOAP client not initialized.")
        try:
            service = getattr(self.soap_client.service, service_name, None)
            if not service:
                raise AttributeError(f"SOAP service '{service_name}' not found.")
            method = getattr(service, method_name, None)
            if not method:
                raise AttributeError(f"SOAP method '{method_name}' not found in service '{service_name}'.")
            logger.info(f"SOAP Request: {service_name}.{method_name} args={args}, kwargs={kwargs}")
            response = method(*args, **kwargs)
            logger.info(f"SOAP Response: {response}")
            return response
        except Fault as fault:
            logger.error(f"SOAP Fault: {fault}")
            raise
        except Exception as e:
            logger.error(f"SOAP Error: {e}")
            raise
