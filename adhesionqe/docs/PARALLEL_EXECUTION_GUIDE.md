# Parallel Execution Enhancement Guide

This guide covers the parallel execution enhancements implemented in the framework.

## 🚀 Overview

The framework now supports:
- ✅ Parallel test execution with pytest-xdist
- ✅ Test sharding for distributed execution
- ✅ Resource pool management
- ✅ Worker-specific file paths
- ✅ Shared resource locking
- ✅ Intelligent test distribution

## 📦 Components

### 1. pytest-xdist Integration

**Configuration**: `pytest.ini`

Run tests in parallel automatically using CPU cores:

```powershell
# Auto-detect CPUs
pytest -n auto

# Specific number of workers
pytest -n 4

# With specific distribution strategy
pytest -n auto --dist loadscope
```

### 2. Parallel Execution Utilities

**File**: `utils/parallel_execution.py`

Provides:
- Worker ID detection
- Worker-specific directories
- Resource locking
- Test grouping

### 3. Test Sharding

**File**: `utils/test_sharding.py`

Distribute tests across multiple machines/CI jobs:

```powershell
# Machine 1 (Shard 1 of 4)
$env:TEST_SHARD_INDEX=0; $env:TEST_SHARD_TOTAL=4; pytest

# Machine 2 (Shard 2 of 4)
$env:TEST_SHARD_INDEX=1; $env:TEST_SHARD_TOTAL=4; pytest

# Machine 3 (Shard 3 of 4)
$env:TEST_SHARD_INDEX=2; $env:TEST_SHARD_TOTAL=4; pytest

# Machine 4 (Shard 4 of 4)
$env:TEST_SHARD_INDEX=3; $env:TEST_SHARD_TOTAL=4; pytest
```

### 4. Resource Pool Management

**File**: `utils/resource_pool.py`

Thread-safe resource pools for:
- Browser contexts
- API clients
- Database connections
- Test data

## 🎯 Usage Examples

### Basic Parallel Execution

```powershell
# Run all tests in parallel
pytest -n auto

# Run specific tests in parallel
pytest tests/test_login.py -n 4

# Parallel with specific browser
pytest -n auto --browser=chromium

# Parallel with live browser (headed)
pytest -n auto --headed
```

### Distribution Strategies

```powershell
# Load by scope (recommended for BDD/grouped tests)
pytest -n auto --dist loadscope

# Load by file (good for independent test files)
pytest -n auto --dist loadfile

# Load by custom group (using xdist_group marker)
pytest -n auto --dist loadgroup
```

### Test Markers for Parallel Control

```python
import pytest

# Test can run in parallel (default)
@pytest.mark.parallel
def test_parallel_safe():
    assert True

# Test must run serially (not in parallel)
@pytest.mark.serial
def test_must_run_alone():
    # Test that modifies global state
    pass

# Group related tests together in same worker
@pytest.mark.xdist_group(name="auth")
def test_login():
    pass

@pytest.mark.xdist_group(name="auth")
def test_logout():
    # Runs in same worker as test_login
    pass
```

### Using Worker-Specific Paths

```python
def test_screenshot(worker_screenshot_path, page):
    """Test with worker-specific screenshot path."""
    page.goto("https://example.com")

    # Each worker saves to its own directory
    screenshot_path = worker_screenshot_path("example.png")
    page.screenshot(path=screenshot_path)

def test_video(worker_video_path, page):
    """Test with worker-specific video path."""
    video_path = worker_video_path("test.webm")
    # Use video_path for recording
```

### Resource Locking for Shared Resources

```python
import pytest

@pytest.mark.parallel
def test_shared_database(shared_resource_lock):
    """Test that safely accesses shared database."""

    # Lock database for this operation
    with shared_resource_lock("database"):
        # Only one test can access database at a time
        # Even across different workers
        db.insert_test_data()
        result = db.query()
        assert result is not None
```

### Using Resource Pools

```python
from utils.resource_pool import ResourcePool

# Create a resource pool
def create_api_client():
    return APIClient(base_url="https://api.example.com")

pool = ResourcePool(
    factory=create_api_client,
    max_size=5,
    cleanup=lambda client: client.close()
)

def test_api_with_pool():
    """Test using resource pool."""
    with pool.acquire_context() as client:
        response = client.get("/users")
        assert response.status_code == 200
```

### Worker ID Detection

```python
def test_worker_aware(worker_id, is_parallel_execution):
    """Test that knows about its execution context."""

    print(f"Running on worker: {worker_id}")

    if is_parallel_execution:
        # Running in parallel mode
        print("Parallel execution enabled")
    else:
        # Running in serial mode
        print("Serial execution")
```

## 🔧 Configuration

### pytest.ini Settings

```ini
[pytest]
# Enable parallel by default (uncomment)
# addopts = -n auto --dist loadscope

# Markers for parallel control
markers =
    parallel: Tests that can run in parallel
    serial: Tests that must run serially
    xdist_group(name): Tests that should run in the same worker
```

### Environment Variables

```powershell
# Test Sharding
$env:TEST_SHARD_INDEX=0      # Current shard (0-based)
$env:TEST_SHARD_TOTAL=4      # Total shards

# Pytest-xdist (set automatically)
$env:PYTEST_XDIST_WORKER     # Worker ID (gw0, gw1, etc.)
```

## 📊 Performance Optimization

### Recommended Settings

```powershell
# For smoke tests (fast)
pytest -n auto --dist loadscope -m smoke

# For regression tests (many tests)
pytest -n auto --dist loadfile -m regression

# For API tests (I/O bound)
pytest -n 10 --dist loadfile tests/api/

# For UI tests (CPU bound)
pytest -n auto --dist loadscope tests/ui/
```

### Load Balancing

The framework automatically balances tests by:
1. **Test duration** - Slower tests distributed first
2. **Test scope** - Tests with same scope run together
3. **Test groups** - Related tests (same xdist_group) run in same worker

### Resource Limits

Configure resource pool sizes based on workers:

```python
# In conftest.py or test file
import pytest
from utils.resource_pool import get_browser_pool

@pytest.fixture(scope="session")
def browser_pool(request):
    num_workers = getattr(request.config.option, 'numprocesses', 1)
    pool_size = max(num_workers, 5)
    return get_browser_pool(max_size=pool_size)
```

## 🎛️ Advanced Usage

### Custom Test Distribution

```python
# In conftest.py
def pytest_collection_modifyitems(config, items):
    """Custom test distribution logic."""

    # Separate fast and slow tests
    fast_tests = []
    slow_tests = []

    for item in items:
        if 'slow' in item.keywords:
            slow_tests.append(item)
        else:
            fast_tests.append(item)

    # Run slow tests first for better parallelization
    items[:] = slow_tests + fast_tests
```

### Conditional Parallel Execution

```python
import pytest
import sys

# Skip parallel execution on Windows (if needed)
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Parallel execution not supported on Windows"
)

def test_example():
    pass
```

### Test Sharding in CI/CD

**GitHub Actions Example**:

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]

steps:
  - name: Run tests (Shard ${{ matrix.shard }}/4)
    env:
      TEST_SHARD_INDEX: ${{ matrix.shard - 1 }}
      TEST_SHARD_TOTAL: 4
    run: pytest -n auto
```

**Azure DevOps Example**:

```yaml
strategy:
  parallel: 4

steps:
  - script: |
      $env:TEST_SHARD_INDEX=$env:SYSTEM_JOBPOSITIONINPHASE - 1
      $env:TEST_SHARD_TOTAL=$env:SYSTEM_TOTALJOBSINPHASE
      pytest -n auto
```

## 📈 Monitoring & Analysis

### View Parallel Execution Stats

```powershell
# Run with verbose output
pytest -n auto -v

# Show worker assignments
pytest -n auto -v --verbose
```

### Analyze Test Distribution

```python
from utils.test_sharding import print_shard_distribution

# Get all test IDs
test_ids = ["test_login", "test_logout", "test_home", ...]

# Analyze distribution across 4 shards
print_shard_distribution(test_ids, 4)
```

### Resource Pool Statistics

```python
from utils.resource_pool import get_browser_pool

pool = get_browser_pool()

# Get statistics after tests
stats = pool.get_stats()
print(f"Resources created: {stats['created']}")
print(f"Resources acquired: {stats['acquired']}")
print(f"Resources destroyed: {stats['destroyed']}")
print(f"Current pool size: {stats['current_size']}")
```

## ⚠️ Important Notes

### Thread Safety

- All fixtures are thread-safe
- Use `shared_resource_lock` for shared resources
- Resource pools handle concurrency automatically

### File Conflicts

- Worker-specific directories prevent file conflicts
- Screenshots/videos automatically separated by worker
- Use provided fixtures for paths

### Test Independence

- Tests should be independent (no shared state)
- Use fixtures for setup/teardown
- Clean up resources properly

### Performance Considerations

- **CPU-bound tests**: Use `-n auto` (matches CPU cores)
- **I/O-bound tests**: Use `-n <higher number>` (e.g., `-n 10`)
- **Mixed tests**: Use `-n auto` with `--dist loadscope`

## 🐛 Troubleshooting

### Tests Fail in Parallel But Pass Serially

**Cause**: Shared state or resource conflicts

**Solution**:
1. Use `@pytest.mark.serial` for problematic tests
2. Add resource locking
3. Fix shared state issues

```python
@pytest.mark.serial
def test_with_shared_state():
    # This will run alone
    pass
```

### Uneven Load Distribution

**Cause**: Some tests much slower than others

**Solution**: Use different distribution strategy

```powershell
# Try loadscope instead of loadfile
pytest -n auto --dist loadscope
```

### Resource Exhaustion

**Cause**: Too many workers, not enough resources

**Solution**: Limit workers or increase pool size

```powershell
# Limit workers
pytest -n 4  # Instead of -n auto

# Or increase pool size in code
pool = get_browser_pool(max_size=10)
```

### File Path Conflicts

**Cause**: Multiple workers writing to same file

**Solution**: Use worker-specific path fixtures

```python
def test_example(worker_screenshot_path):
    path = worker_screenshot_path("file.png")
    # Each worker has unique path
```

## 📚 Best Practices

1. **Mark serial tests explicitly**
   ```python
   @pytest.mark.serial
   def test_modifies_global_state():
       pass
   ```

2. **Use resource pools for expensive resources**
   ```python
   with browser_pool.acquire_context() as browser:
       # Reuse browser instance
       pass
   ```

3. **Group related tests**
   ```python
   @pytest.mark.xdist_group(name="auth")
   def test_login():
       pass
   ```

4. **Use worker-specific paths**
   ```python
   def test_screenshot(worker_screenshot_path, page):
       path = worker_screenshot_path("test.png")
       page.screenshot(path=path)
   ```

5. **Test with parallel execution enabled**
   ```powershell
   # Always test with parallelization
   pytest -n auto
   ```

## 🎓 Examples

### Complete Test Example

```python
import pytest
from utils.resource_pool import ResourcePool

@pytest.mark.parallel
@pytest.mark.xdist_group(name="api")
def test_api_parallel(shared_resource_lock, worker_id):
    """
    Example of parallel-safe API test.
    """
    print(f"Running on worker: {worker_id}")

    # Use resource pool
    with api_pool.acquire_context() as client:
        response = client.get("/users")
        assert response.status_code == 200

    # Lock shared resource if needed
    with shared_resource_lock("test_data"):
        # Modify shared test data safely
        pass

@pytest.mark.serial
def test_requires_isolation():
    """
    Example of test that must run alone.
    """
    # Test that modifies global state
    # or requires exclusive resource access
    pass
```

## 🔗 Related Documentation

- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [Pytest documentation](https://docs.pytest.org/)
- [CODE_QUALITY_GUIDE.md](CODE_QUALITY_GUIDE.md)
- [BDD_GUIDE.md](BDD_GUIDE.md)

## 🚀 Quick Reference

```powershell
# Run in parallel (auto CPU count)
pytest -n auto

# Run with 4 workers
pytest -n 4

# Parallel with distribution strategy
pytest -n auto --dist loadscope

# Parallel with sharding
$env:TEST_SHARD_INDEX=0; $env:TEST_SHARD_TOTAL=4; pytest -n auto

# Run only parallel-safe tests
pytest -n auto -m parallel

# Run serial tests only
pytest -m serial
```
