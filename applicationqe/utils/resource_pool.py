"""
Resource pool management for parallel test execution.

Provides thread-safe resource pools for:
- Browser contexts
- Database connections
- API clients
- Test data
"""

import logging
import threading
from contextlib import contextmanager
from queue import Empty, Queue
from typing import Callable, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ResourcePool(Generic[T]):
    """
    Thread-safe resource pool for managing shared resources in parallel tests.

    Example:
        def create_browser():
            return playwright.chromium.launch()

        pool = ResourcePool(
            factory=create_browser,
            max_size=5,
            cleanup=lambda b: b.close()
        )

        with pool.acquire() as browser:
            # Use browser
            pass
    """

    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 5,
        cleanup: Optional[Callable[[T], None]] = None,
        validation: Optional[Callable[[T], bool]] = None,
    ):
        """
        Initialize resource pool.

        Args:
            factory: Function to create new resources
            max_size: Maximum pool size
            cleanup: Function to cleanup resources (optional)
            validation: Function to validate resources (optional)
        """
        self.factory = factory
        self.max_size = max_size
        self.cleanup = cleanup
        self.validation = validation

        self._pool: Queue[T] = Queue(maxsize=max_size)
        self._current_size = 0
        self._lock = threading.Lock()
        self._stats = {
            "created": 0,
            "acquired": 0,
            "released": 0,
            "destroyed": 0,
            "validation_failures": 0,
        }

    def _create_resource(self) -> T:
        """Create a new resource using the factory."""
        with self._lock:
            if self._current_size >= self.max_size:
                raise RuntimeError(f"Pool size limit reached: {self.max_size}")

            resource = self.factory()
            self._current_size += 1
            self._stats["created"] += 1
            logger.debug(f"Created new resource. Pool size: {self._current_size}/{self.max_size}")
            return resource

    def _validate_resource(self, resource: T) -> bool:
        """Validate a resource before returning it."""
        if self.validation is None:
            return True

        try:
            is_valid = self.validation(resource)
            if not is_valid:
                self._stats["validation_failures"] += 1
                logger.warning("Resource validation failed")
            return is_valid
        except Exception as e:
            logger.error(f"Resource validation error: {str(e).splitlines()[0]}")
            self._stats["validation_failures"] += 1
            return False

    def acquire(self, timeout: float = 10.0) -> T:
        """
        Acquire a resource from the pool.

        Args:
            timeout: Maximum time to wait for a resource (seconds)

        Returns:
            Resource from the pool

        Raises:
            Empty: If no resource available within timeout
        """
        # Try to get existing resource from pool
        try:
            resource = self._pool.get(timeout=timeout)

            # Validate resource
            if self._validate_resource(resource):
                self._stats["acquired"] += 1
                logger.debug("Acquired resource from pool")
                return resource
            else:
                # Resource invalid, destroy it and create new one
                self._destroy_resource(resource)
                return self._create_resource()

        except Empty:
            # No resource available, try to create new one
            with self._lock:
                if self._current_size < self.max_size:
                    return self._create_resource()
                else:
                    raise Empty(f"No resources available in pool (timeout: {timeout}s)")

    def release(self, resource: T):
        """
        Release a resource back to the pool.

        Args:
            resource: Resource to release
        """
        if self._validate_resource(resource):
            self._pool.put(resource)
            self._stats["released"] += 1
            logger.debug("Released resource back to pool")
        else:
            # Resource invalid, destroy it
            self._destroy_resource(resource)

    def _destroy_resource(self, resource: T):
        """Destroy a resource and update pool size."""
        with self._lock:
            if self.cleanup:
                try:
                    self.cleanup(resource)
                except Exception as e:
                    logger.error(f"Resource cleanup error: {str(e).splitlines()[0]}")

            self._current_size -= 1
            self._stats["destroyed"] += 1
            logger.debug(f"Destroyed resource. Pool size: {self._current_size}/{self.max_size}")

    @contextmanager
    def acquire_context(self, timeout: float = 10.0):
        """
        Context manager for acquiring and releasing resources.

        Args:
            timeout: Maximum time to wait for resource

        Example:
            with pool.acquire_context() as resource:
                # Use resource
                pass
        """
        resource = self.acquire(timeout=timeout)
        try:
            yield resource
        finally:
            self.release(resource)

    def clear(self):
        """Clear all resources from the pool."""
        while not self._pool.empty():
            try:
                resource = self._pool.get_nowait()
                self._destroy_resource(resource)
            except Empty:
                break

    def get_stats(self) -> dict:
        """
        Get pool statistics.

        Returns:
            dict: Pool statistics
        """
        return {
            **self._stats,
            "current_size": self._current_size,
            "max_size": self.max_size,
            "available": self._pool.qsize(),
        }

    def __del__(self):
        """Cleanup on object destruction."""
        self.clear()


# Global resource pools
_browser_pool: Optional[ResourcePool] = None
_api_client_pool: Optional[ResourcePool] = None


def get_browser_pool(max_size: int = 5) -> ResourcePool:
    """
    Get or create the global browser resource pool.

    Args:
        max_size: Maximum pool size

    Returns:
        ResourcePool: Browser resource pool
    """
    global _browser_pool

    if _browser_pool is None:
        from playwright.sync_api import sync_playwright

        def create_browser():
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            return browser

        def cleanup_browser(browser):
            try:
                browser.close()
            except Exception:
                pass

        _browser_pool = ResourcePool(
            factory=create_browser, max_size=max_size, cleanup=cleanup_browser
        )

    return _browser_pool


def get_api_client_pool(max_size: int = 10) -> ResourcePool:
    """
    Get or create the global API client resource pool.

    Args:
        max_size: Maximum pool size

    Returns:
        ResourcePool: API client resource pool
    """
    global _api_client_pool

    if _api_client_pool is None:
        import requests

        def create_client():
            session = requests.Session()
            return session

        def cleanup_client(session):
            try:
                session.close()
            except Exception:
                pass

        _api_client_pool = ResourcePool(
            factory=create_client, max_size=max_size, cleanup=cleanup_client
        )

    return _api_client_pool


# Pytest fixtures for resource pools
def pytest_configure(config):
    """Configure resource pools for test session."""
    # Initialize pools based on number of workers
    num_workers = getattr(config.option, "numprocesses", 1)

    if num_workers == "auto":
        import multiprocessing

        num_workers = multiprocessing.cpu_count()

    # Set pool sizes based on number of workers
    pool_size = max(num_workers, 5)
    logger.info(f"Configuring resource pools with size: {pool_size}")


def pytest_sessionfinish(session, exitstatus):
    """Cleanup resource pools after session."""
    global _browser_pool, _api_client_pool

    if _browser_pool:
        _browser_pool.clear()
        logger.info(f"Browser pool stats: {_browser_pool.get_stats()}")

    if _api_client_pool:
        _api_client_pool.clear()
        logger.info(f"API client pool stats: {_api_client_pool.get_stats()}")
