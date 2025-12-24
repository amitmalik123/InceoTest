"""
Enhanced Database Client Module
Supports multiple database types, servers, and connection pooling
Supports: MSSQL, PostgreSQL, CosmosDB, MongoDB, SQLite
"""

import platform
import psycopg2
import sqlite3

# Platform-aware driver selection: prefer pymssql on Linux, pyodbc on Windows
PYODBC_AVAILABLE = False
PYMSSQL_AVAILABLE = False

if platform.system() == 'Windows':
    # On Windows, prefer pyodbc (better Windows Auth support)
    try:
        import pyodbc
        PYODBC_AVAILABLE = True
        logger_msg = "Using pyodbc for MSSQL connections (Windows)"
    except ImportError:
        try:
            import pymssql
            PYMSSQL_AVAILABLE = True
            logger_msg = "Using pymssql for MSSQL connections (pyodbc not available)"
        except ImportError:
            logger_msg = "No MSSQL driver available"
else:
    # On Linux/Unix, prefer pymssql (no ODBC system dependencies)
    try:
        import pymssql
        PYMSSQL_AVAILABLE = True
        logger_msg = "Using pymssql for MSSQL connections (Linux/Unix)"
    except ImportError:
        try:
            import pyodbc
            PYODBC_AVAILABLE = True
            logger_msg = "Using pyodbc for MSSQL connections (pymssql not available)"
        except ImportError:
            logger_msg = "No MSSQL driver available"
import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from framework.common.logger import get_logger
from framework.loaders.config_loader import get_config, substitute_env_vars

logger = get_logger(__name__)

# Log which MSSQL driver is available
if PYODBC_AVAILABLE:
    logger.info("MSSQL driver: pyodbc (ODBC-based, typically used on Windows)")
elif PYMSSQL_AVAILABLE:
    logger.info("MSSQL driver: pymssql (pure Python, no ODBC required)")
else:
    logger.warning("No MSSQL driver available. Install either pyodbc or pymssql.")

# Import Azure authentication utilities
try:
    from framework.clients.azure_auth import get_azure_access_token, check_azure_login
    AZURE_AUTH_AVAILABLE = True
except ImportError:
    AZURE_AUTH_AVAILABLE = False
    logger.warning("Azure authentication utilities not available. Install azure-cli for Azure AD authentication.")

# Optional imports for additional databases
try:
    from pymongo import MongoClient as PyMongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    logger.warning("pymongo not installed. MongoDB support disabled.")

try:
    from azure.cosmos import CosmosClient as AzureCosmosClient, exceptions
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    logger.warning("azure-cosmos not installed. CosmosDB support disabled.")

try:
    from influxdb_client import InfluxDBClient as InfluxClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False
    logger.warning("influxdb-client not installed. InfluxDB support disabled.")


class DatabaseClient(ABC):
    """Abstract base class for all database clients"""
    
    def __init__(self, connection_name: str = None, config: Dict = None):
        self.connection_name = connection_name
        self.config = config or {}
        self.conn = None
        self._is_connected = False
    
    @abstractmethod
    def connect(self):
        """Establish database connection"""
        pass
    
    @abstractmethod
    def query(self, sql: str, params: tuple = None) -> List[Dict]:
        """Execute query and return results as list of dictionaries"""
        pass
    
    @abstractmethod
    def execute(self, sql: str, params: tuple = None) -> int:
        """Execute non-query statement (INSERT, UPDATE, DELETE)"""
        pass
    
    @abstractmethod
    def close(self):
        """Close database connection"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False


class MSSQLClient(DatabaseClient):
    """Microsoft SQL Server Client"""
    
    def __init__(self, connection_string: str = None, connection_name: str = None, config: Dict = None):
        super().__init__(connection_name, config)
        self.connection_string = connection_string
        
        if not self.connection_string:
            self.connection_string = self._build_connection_string()
    
    def _build_connection_string(self):
        """Build MSSQL connection string/params - supports both pyodbc and pymssql"""
        if not self.config:
            return None
        
        # Check if connection_string is directly provided in config
        if 'connection_string' in self.config:
            conn_str = substitute_env_vars(self.config['connection_string'])
            logger.info(f"Using direct connection string from config for {self.connection_name}")
            return conn_str
        
        server = self.config.get('server')
        database = self.config.get('database')
        user = self.config.get('user')
        password = substitute_env_vars(self.config.get('password', ''))
        port = self.config.get('port', 1433)
        driver = self.config.get('driver', 'ODBC Driver 17 for SQL Server')
        trusted_connection = self.config.get('trusted_connection', False)
        encrypt = self.config.get('encrypt', False)
        trust_server_certificate = self.config.get('trust_server_certificate', False)
        
        if PYODBC_AVAILABLE:
            # Build ODBC connection string
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            
            if trusted_connection:
                conn_str += "Trusted_Connection=yes;"
            else:
                if user:
                    conn_str += f"UID={user};"
                if password:
                    conn_str += f"PWD={password};"
            
            if encrypt:
                conn_str += "Encrypt=yes;"
            if trust_server_certificate:
                conn_str += "TrustServerCertificate=yes;"
            
            logger.info(f"Built ODBC connection string for {self.connection_name}")
            return conn_str
        elif PYMSSQL_AVAILABLE:
            # Build pymssql connection params (dict)
            conn_params = {
                'server': server,
                'database': database,
                'port': port
            }
            if user:
                conn_params['user'] = user
            if password:
                conn_params['password'] = password
            
            logger.info(f"Built pymssql connection params for {self.connection_name}")
            return conn_params
        else:
            raise ImportError("No MSSQL driver available. Install either pyodbc or pymssql.")
    
    def connect(self):
        """Establish MSSQL connection using available driver (pyodbc or pymssql)"""
        try:
            if PYODBC_AVAILABLE:
                # Use pyodbc (ODBC driver)
                if isinstance(self.connection_string, str):
                    self.conn = pyodbc.connect(self.connection_string)
                else:
                    raise ValueError("pyodbc requires connection string format")
                logger.info(f"Connected to MSSQL via pyodbc: {self.connection_name or 'default'}")
            elif PYMSSQL_AVAILABLE:
                # Use pymssql (pure Python)
                if isinstance(self.connection_string, dict):
                    self.conn = pymssql.connect(**self.connection_string)
                elif isinstance(self.connection_string, str):
                    params = self._parse_connection_string(self.connection_string)
                    self.conn = pymssql.connect(**params)
                else:
                    raise ValueError("Invalid connection configuration")
                logger.info(f"Connected to MSSQL via pymssql: {self.connection_name or 'default'}")
            else:
                raise ImportError("No MSSQL driver available. Install either pyodbc or pymssql.")
            
            self._is_connected = True
        except Exception as e:
            logger.error(f"Failed to connect to MSSQL: {e}")
            raise
    
    def _parse_connection_string(self, conn_str: str) -> dict:
        """Parse ODBC-style connection string to pymssql parameters"""
        params = {}
        for part in conn_str.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key in ['SERVER', 'HOST']:
                    params['server'] = value
                elif key in ['DATABASE', 'DB']:
                    params['database'] = value
                elif key in ['UID', 'USER', 'USERNAME']:
                    params['user'] = value
                elif key in ['PWD', 'PASSWORD']:
                    params['password'] = value
                elif key == 'PORT':
                    params['port'] = int(value)
        
        # Set defaults
        params.setdefault('port', 1433)
        return params
    
    def query(self, sql: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        if not self._is_connected:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            logger.info(f"MSSQL query executed successfully. Rows returned: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"MSSQL query failed: {e}")
            raise
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """Execute non-query statement"""
        if not self._is_connected:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            self.conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"MSSQL execute completed. Rows affected: {rows_affected}")
            return rows_affected
        except Exception as e:
            logger.error(f"MSSQL execute failed: {e}")
            self.conn.rollback()
            raise
    
    def close(self):
        """Close MSSQL connection"""
        if self.conn:
            self.conn.close()
            self._is_connected = False
            logger.info(f"MSSQL connection closed: {self.connection_name or 'default'}")


class PostgreSQLClient(DatabaseClient):
    """PostgreSQL Client"""
    
    def __init__(self, connection_string: str = None, connection_name: str = None, config: Dict = None):
        super().__init__(connection_name, config)
        self.connection_string = connection_string
        
        if not self.connection_string:
            self.connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string from config with Azure AD support"""
        if not self.config:
            return None
        
        # Check if connection_string is directly provided in config
        if 'connection_string' in self.config:
            conn_str = substitute_env_vars(self.config['connection_string'])
            logger.info(f"Using direct connection string from config for {self.connection_name}")
            return conn_str
        
        host = self.config.get('host')
        port = self.config.get('port', 5432)
        database = self.config.get('database')
        user = self.config.get('user')
        password = self.config.get('password')
        sslmode = self.config.get('sslmode', 'prefer')
        use_azure_auth = self.config.get('use_azure_auth', False)
        
        # Azure AD Authentication support
        if use_azure_auth and AZURE_AUTH_AVAILABLE:
            try:
                logger.info(f"Using Azure AD authentication for PostgreSQL: {self.connection_name}")
                if not check_azure_login():
                    raise RuntimeError("Not logged in to Azure CLI. Please run 'az login' first.")
                
                # Generate Azure access token for PostgreSQL
                password = get_azure_access_token("https://ossrdbms-aad.database.windows.net")
                logger.debug("Azure AD access token generated successfully")
            except Exception as e:
                logger.error(f"Azure AD authentication failed: {e}")
                raise
        elif use_azure_auth and not AZURE_AUTH_AVAILABLE:
            logger.warning("Azure AD authentication requested but not available. Falling back to password authentication.")
        
        # Handle special case where password might be a placeholder for Azure auth
        if password and password.upper() in ['AZURE_AD', 'AZURE_AUTH', 'USE_AZURE_AD']:
            if AZURE_AUTH_AVAILABLE:
                try:
                    logger.info(f"Password placeholder detected, using Azure AD authentication")
                    password = get_azure_access_token("https://ossrdbms-aad.database.windows.net")
                except Exception as e:
                    logger.error(f"Failed to get Azure AD token: {e}")
                    raise
            else:
                raise ValueError("Azure AD authentication requested but azure_auth module not available")
        
        conn_str = f"host={host} port={port} dbname={database} user={user} password={password} sslmode={sslmode}"
        return conn_str
    
    def connect(self):
        """Establish PostgreSQL connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self._is_connected = True
            logger.info(f"Connected to PostgreSQL database: {self.connection_name or 'default'}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def query(self, sql: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        if not self._is_connected:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            logger.info(f"PostgreSQL query executed successfully. Rows returned: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"PostgreSQL query failed: {e}")
            raise
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """Execute non-query statement"""
        if not self._is_connected:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            self.conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"PostgreSQL execute completed. Rows affected: {rows_affected}")
            return rows_affected
        except Exception as e:
            logger.error(f"PostgreSQL execute failed: {e}")
            self.conn.rollback()
            raise
    
    def close(self):
        """Close PostgreSQL connection"""
        if self.conn:
            self.conn.close()
            self._is_connected = False
            logger.info(f"PostgreSQL connection closed: {self.connection_name or 'default'}")


class SQLiteClient(DatabaseClient):
    """SQLite Client"""
    
    def __init__(self, db_path: str = None, connection_name: str = None, config: Dict = None):
        super().__init__(connection_name, config)
        self.db_path = db_path or (config.get('path') if config else None)
    
    def connect(self):
        """Establish SQLite connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self._is_connected = True
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise
    
    def query(self, sql: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        if not self._is_connected:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            logger.info(f"SQLite query executed successfully. Rows returned: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"SQLite query failed: {e}")
            raise
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """Execute non-query statement"""
        if not self._is_connected:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            self.conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"SQLite execute completed. Rows affected: {rows_affected}")
            return rows_affected
        except Exception as e:
            logger.error(f"SQLite execute failed: {e}")
            self.conn.rollback()
            raise
    
    def close(self):
        """Close SQLite connection"""
        if self.conn:
            self.conn.close()
            self._is_connected = False
            logger.info(f"SQLite connection closed: {self.db_path}")


class MongoDBClient(DatabaseClient):
    """MongoDB Client"""
    
    def __init__(self, connection_name: str = None, config: Dict = None):
        if not MONGO_AVAILABLE:
            raise ImportError("pymongo is required for MongoDB support. Install with: pip install pymongo")
        
        super().__init__(connection_name, config)
        self.connection_string = config.get('connection_string') if config else None
        self.database_name = config.get('database') if config else None
        self.collection_name = config.get('collection') if config else None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.conn = PyMongoClient(self.connection_string)
            self.db = self.conn[self.database_name]
            if self.collection_name:
                self.collection = self.db[self.collection_name]
            self._is_connected = True
            logger.info(f"Connected to MongoDB: {self.connection_name or self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def query(self, filter_query: Dict = None, collection: str = None) -> List[Dict]:
        """Execute MongoDB find query"""
        if not self._is_connected:
            self.connect()
        
        try:
            coll = self.db[collection] if collection else self.collection
            results = list(coll.find(filter_query or {}))
            logger.info(f"MongoDB query executed successfully. Documents returned: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"MongoDB query failed: {e}")
            raise
    
    def execute(self, operation: str, data: Dict, collection: str = None) -> Any:
        """Execute MongoDB operation (insert, update, delete)"""
        if not self._is_connected:
            self.connect()
        
        try:
            coll = self.db[collection] if collection else self.collection
            result = None
            
            if operation == 'insert_one':
                result = coll.insert_one(data)
            elif operation == 'insert_many':
                result = coll.insert_many(data)
            elif operation == 'update_one':
                result = coll.update_one(data.get('filter'), data.get('update'))
            elif operation == 'delete_one':
                result = coll.delete_one(data)
            
            logger.info(f"MongoDB {operation} executed successfully")
            return result
        except Exception as e:
            logger.error(f"MongoDB execute failed: {e}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.conn:
            self.conn.close()
            self._is_connected = False
            logger.info(f"MongoDB connection closed: {self.connection_name or self.database_name}")


class CosmosDBClient(DatabaseClient):
    """Azure CosmosDB Client"""
    
    def __init__(self, connection_name: str = None, config: Dict = None):
        if not COSMOS_AVAILABLE:
            raise ImportError("azure-cosmos is required for CosmosDB support. Install with: pip install azure-cosmos")
        
        super().__init__(connection_name, config)
        self.endpoint = config.get('endpoint') if config else None
        self.key = config.get('key') if config else None
        self.database_name = config.get('database') if config else None
        self.container_name = config.get('container') if config else None
        self.database = None
        self.container = None
    
    def connect(self):
        """Establish CosmosDB connection"""
        try:
            self.conn = AzureCosmosClient(self.endpoint, self.key)
            self.database = self.conn.get_database_client(self.database_name)
            if self.container_name:
                self.container = self.database.get_container_client(self.container_name)
            self._is_connected = True
            logger.info(f"Connected to CosmosDB: {self.connection_name or self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to CosmosDB: {e}")
            raise
    
    def query(self, query: str, container: str = None) -> List[Dict]:
        """Execute CosmosDB SQL query"""
        if not self._is_connected:
            self.connect()
        
        try:
            cont = self.database.get_container_client(container) if container else self.container
            results = list(cont.query_items(query=query, enable_cross_partition_query=True))
            logger.info(f"CosmosDB query executed successfully. Items returned: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"CosmosDB query failed: {e}")
            raise
    
    def execute(self, operation: str, data: Dict, container: str = None) -> Any:
        """Execute CosmosDB operation"""
        if not self._is_connected:
            self.connect()
        
        try:
            cont = self.database.get_container_client(container) if container else self.container
            result = None
            
            if operation == 'create_item':
                result = cont.create_item(body=data)
            elif operation == 'upsert_item':
                result = cont.upsert_item(body=data)
            elif operation == 'delete_item':
                result = cont.delete_item(item=data.get('id'), partition_key=data.get('partition_key'))
            
            logger.info(f"CosmosDB {operation} executed successfully")
            return result
        except Exception as e:
            logger.error(f"CosmosDB execute failed: {e}")
            raise
    
    def close(self):
        """Close CosmosDB connection"""
        if self.conn:
            self.conn = None
            self._is_connected = False
            logger.info(f"CosmosDB connection closed: {self.connection_name or self.database_name}")


class InfluxDBClient(DatabaseClient):
    """InfluxDB Client for time-series metrics"""
    
    def __init__(self, connection_name: str = None, config: Dict = None):
        if not INFLUX_AVAILABLE:
            raise ImportError("influxdb-client is required for InfluxDB support. Install with: pip install influxdb-client")
        
        super().__init__(connection_name, config)
        self.url = config.get('url') if config else None
        self.token = config.get('token') if config else None
        self.org = config.get('org') if config else None
        self.bucket = config.get('bucket') if config else None
        self.timeout = config.get('timeout', 10000) if config else 10000
        self.write_api = None
        self.query_api = None
    
    def connect(self):
        """Establish InfluxDB connection"""
        try:
            # Validate required configuration
            if not all([self.url, self.token, self.org, self.bucket]):
                raise ValueError("Missing required InfluxDB configuration (url, token, org, bucket)")
            
            self.conn = InfluxClient(url=self.url, token=self.token, org=self.org, timeout=self.timeout)
            self.write_api = self.conn.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.conn.query_api()
            self._is_connected = True
            logger.info(f"Connected to InfluxDB at {self.url} (org: {self.org}, bucket: {self.bucket})")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            raise
    
    def query(self, flux_query: str) -> List[Dict]:
        """
        Execute Flux query and return results
        
        Args:
            flux_query: Flux query string
        
        Returns:
            List of dictionaries with query results
        """
        if not self._is_connected:
            self.connect()
        
        try:
            tables = self.query_api.query(flux_query, org=self.org)
            results = []
            
            for table in tables:
                for record in table.records:
                    results.append(record.values)
            
            logger.info(f"InfluxDB query executed successfully. Records returned: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"InfluxDB query failed: {e}")
            raise
    
    def execute(self, operation: str, data: Any) -> bool:
        """
        Execute InfluxDB write operation
        
        Args:
            operation: Operation type ('write_point', 'write_points', 'write_dict')
            data: Data to write (Point object, list of Points, or dict)
        
        Returns:
            True if successful
        """
        if not self._is_connected:
            self.connect()
        
        try:
            # Validate data before writing
            if operation in ['write_point', 'write_points']:
                if data is None:
                    logger.error(f"Cannot write None data for {operation}")
                    return False
                if operation == 'write_points' and not isinstance(data, list):
                    logger.error(f"write_points requires a list, got {type(data)}")
                    return False
                if operation == 'write_points' and len(data) == 0:
                    logger.warning("write_points called with empty list")
                    return False
            
            logger.debug(f"Writing to bucket: {self.bucket}, org: {self.org}")
            
            if operation == 'write_point':
                # Write single Point
                self.write_api.write(bucket=self.bucket, org=self.org, record=data)
                logger.debug(f"Single point written to InfluxDB")
            elif operation == 'write_points':
                # Write multiple Points
                logger.debug(f"Writing {len(data)} points to InfluxDB")
                self.write_api.write(bucket=self.bucket, org=self.org, record=data)
                logger.debug(f"Batch of {len(data)} points written to InfluxDB")
            elif operation == 'write_dict':
                # Write dictionary
                self.write_api.write(bucket=self.bucket, org=self.org, record=data)
                logger.debug(f"Dictionary data written to InfluxDB")
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Force flush to ensure data is sent
            self.write_api.flush()
            logger.debug(f"InfluxDB {operation} executed and flushed successfully")
            return True
        except Exception as e:
            logger.error(f"InfluxDB execute failed for {operation}: {e}", exc_info=True)
            raise
    
    def write_point(self, point: 'Point') -> bool:
        """
        Write a single data point to InfluxDB
        
        Args:
            point: InfluxDB Point object
        
        Returns:
            True if successful
        """
        return self.execute('write_point', point)
    
    def write_points(self, points: List['Point']) -> bool:
        """
        Write multiple data points to InfluxDB
        
        Args:
            points: List of InfluxDB Point objects
        
        Returns:
            True if successful
        """
        if not points:
            logger.warning("write_points called with empty or None points list")
            return False
        
        logger.debug(f"Preparing to write {len(points)} points to InfluxDB")
        result = self.execute('write_points', points)
        if result:
            logger.info(f"InfluxDB batch write completed: {len(points)} points written to bucket '{self.bucket}'")
        return result
    
    def close(self):
        """Close InfluxDB connection"""
        if self.conn:
            self.conn.close()
            self._is_connected = False
            logger.info(f"InfluxDB connection closed: {self.connection_name or 'default'}")


class DatabaseClientFactory:
    """
    Factory class to create and manage multiple database connections
    Supports connection pooling and centralized configuration management
    """
    
    _instances = {}  # Connection pool
    _config = None
    
    @classmethod
    def load_config(cls, env: str = None):
        """Load database configuration using centralized ConfigManager"""
        if cls._config:
            return cls._config
        
        # Use centralized config manager
        cls._config = get_config(reload=False)
        logger.info(f"Loaded database configuration from ConfigManager")
        
        return cls._config
    
    @classmethod
    def get_client(cls, db_type: str, connection_name: str = None, auto_connect: bool = True) -> DatabaseClient:
        """
        Get or create a database client
        
        Args:
            db_type: Type of database (mssql, postgresql, sqlite, mongodb, cosmosdb)
            connection_name: Name of the connection in config (e.g., 'tracking_center', 'parties')
            auto_connect: Automatically connect to the database
        
        Returns:
            DatabaseClient instance
        """
        # Load config if not already loaded
        if not cls._config:
            cls.load_config()
        
        # Create unique key for connection pool
        pool_key = f"{db_type}:{connection_name or 'default'}"
        
        # Return existing connection if available
        if pool_key in cls._instances:
            logger.info(f"Reusing existing connection: {pool_key}")
            return cls._instances[pool_key]
        
        # Get connection configuration
        db_connections = cls._config.get('db_connections', {})
        db_config = None
        
        if db_type in db_connections:
            if connection_name:
                # Get specific named connection
                db_config = db_connections[db_type].get(connection_name)
            elif isinstance(db_connections[db_type], dict):
                # Get first connection or handle direct config
                if 'host' in db_connections[db_type] or 'server' in db_connections[db_type]:
                    # Direct config (old format)
                    db_config = db_connections[db_type]
                else:
                    # Named connections, get first one
                    first_key = next(iter(db_connections[db_type]))
                    db_config = db_connections[db_type][first_key]
                    connection_name = first_key
            else:
                # Legacy format: connection string directly
                db_config = {'connection_string': db_connections[db_type]}
        
        if not db_config:
            raise ValueError(f"No configuration found for {db_type}:{connection_name}")
        
        # Substitute environment variables in config
        db_config = substitute_env_vars(db_config)
        
        # Create appropriate client
        client = None
        
        if db_type.lower() == 'mssql':
            client = MSSQLClient(connection_name=connection_name, config=db_config)
        elif db_type.lower() in ['postgresql', 'postgres']:
            client = PostgreSQLClient(connection_name=connection_name, config=db_config)
        elif db_type.lower() == 'sqlite':
            client = SQLiteClient(connection_name=connection_name, config=db_config)
        elif db_type.lower() == 'mongodb':
            client = MongoDBClient(connection_name=connection_name, config=db_config)
        elif db_type.lower() == 'cosmosdb':
            client = CosmosDBClient(connection_name=connection_name, config=db_config)
        elif db_type.lower() == 'influxdb':
            client = InfluxDBClient(connection_name=connection_name, config=db_config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Auto-connect if requested
        if auto_connect:
            client.connect()
        
        # Store in connection pool
        cls._instances[pool_key] = client
        logger.info(f"Created new database client: {pool_key}")
        
        return client
    
    @classmethod
    def close_all(cls):
        """Close all active database connections"""
        for pool_key, client in cls._instances.items():
            try:
                client.close()
                logger.info(f"Closed connection: {pool_key}")
            except Exception as e:
                logger.error(f"Error closing connection {pool_key}: {e}")
        
        cls._instances.clear()
        logger.info("All database connections closed")
    
    @classmethod
    @contextmanager
    def get_connection(cls, db_type: str, connection_name: str = None):
        """
        Context manager for database connections
        
        Usage:
            with DatabaseClientFactory.get_connection('mssql', 'tracking_center') as db:
                results = db.query("SELECT * FROM users")
        """
        client = cls.get_client(db_type, connection_name, auto_connect=True)
        try:
            yield client
        finally:
            # Don't close pooled connections, just leave them open for reuse
            pass


# Backward compatibility: Keep old MSSQLClient interface
def create_postgres_connection(config_path):
    """Legacy function for PostgreSQL connection"""
    logger.warning("create_postgres_connection is deprecated. Use DatabaseClientFactory.get_client() instead.")
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    conn_str = f"host={cfg['PG_HOST']} port={cfg['PG_PORT']} dbname={cfg['PG_DB']} user={cfg['PG_USER']} password={cfg['PG_PASSWORD']}"
    return psycopg2.connect(conn_str)


# Usage examples:
"""
# Using factory to get MSSQL client
db = DatabaseClientFactory.get_client('mssql', 'tracking_center')
results = db.query("SELECT * FROM users")
db.close()

# Using PostgreSQL client
pg_db = DatabaseClientFactory.get_client('postgresql', 'parties')
results = pg_db.query("SELECT * FROM parties WHERE id = %s", (123,))
pg_db.close()

# Using InfluxDB client
from influxdb_client import Point, WritePrecision
influx_db = DatabaseClientFactory.get_client('influxdb', 'default')
point = Point("test_metrics").tag("environment", "dev").field("value", 100).time(datetime.utcnow(), WritePrecision.S)
influx_db.write_point(point)
influx_db.close()

# Using context manager
with DatabaseClientFactory.get_connection('mssql', 'tracking_center') as db:
    results = db.query("SELECT * FROM users")
    # Connection automatically managed

# Close all connections at end of test run
DatabaseClientFactory.close_all()
"""
