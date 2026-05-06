# gRPC client stub for framework


import grpc
from framework.common.logger import get_logger
logger = get_logger(__name__)

class GrpcClient:
    def __init__(self, grpc_host, grpc_port, grpc_stub_class):
        self.grpc_host = grpc_host
        self.grpc_port = grpc_port
        self.grpc_stub_class = grpc_stub_class
        self.grpc_channel = None
        self.grpc_stub = None
        self._init_grpc_client()

    def _init_grpc_client(self):
        address = f"{self.grpc_host}:{self.grpc_port}"
        self.grpc_channel = grpc.insecure_channel(address)
        self.grpc_stub = self.grpc_stub_class(self.grpc_channel)
        logger.info(f"Initialized gRPC client at {address}")

    def call(self, rpc_method_name, request_message):
        if not self.grpc_stub:
            raise RuntimeError("gRPC client not initialized.")
        rpc_method = getattr(self.grpc_stub, rpc_method_name, None)
        if not rpc_method:
            raise AttributeError(f"RPC method '{rpc_method_name}' not found in stub.")
        logger.info(f"gRPC Request: {rpc_method_name}({request_message})")
        response = rpc_method(request_message)
        logger.info(f"gRPC Response: {response}")
        return response
