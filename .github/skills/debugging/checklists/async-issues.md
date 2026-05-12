# Async/Await Issues Debugging Checklist

Systematic approach to diagnosing and resolving async/await problems in .NET applications.

## Common Causes (Ranked by Likelihood)

### 1. Sync-Over-Async (Blocking on Async Code)
**Likelihood: Very High**

Calling `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` on async methods.

```csharp
// Problem: Blocking on async in synchronous context
public string GetData()
{
    var result = GetDataAsync().Result; // Can deadlock
    return result;
}

// Problem: Using Wait() on task
public void Process()
{
    ProcessAsync().Wait(); // Can deadlock
}
```

### 2. Missing Await Keyword
**Likelihood: High**

Forgetting to await an async method, causing fire-and-forget behavior.

```csharp
// Problem: Missing await - method runs but isn't awaited
public async Task ProcessOrderAsync(Order order)
{
    ValidateOrderAsync(order); // Missing await - runs in background
    await SaveOrderAsync(order); // This might run before validation completes
}
```

### 3. Async Void Methods
**Likelihood: High**

Using `async void` instead of `async Task`, losing exception handling.

```csharp
// Problem: Exceptions cannot be caught
public async void ProcessInBackground() // Should be async Task
{
    await DoWorkAsync(); // Exception here crashes the app
}

// This won't catch the exception
try
{
    ProcessInBackground();
}
catch (Exception ex) { } // Never reached
```

### 4. Deadlock from SynchronizationContext
**Likelihood: Medium-High**

Deadlock when blocking on async code that captures context.

```csharp
// Problem: Classic ASP.NET deadlock pattern
public ActionResult Index()
{
    var data = GetDataAsync().Result; // Deadlock in ASP.NET
    return View(data);
}

private async Task<Data> GetDataAsync()
{
    await Task.Delay(100); // Tries to resume on captured context
    return new Data();     // But context is blocked by .Result
}
```

### 5. ConfigureAwait Issues
**Likelihood: Medium**

Missing `ConfigureAwait(false)` in library code causing context issues.

```csharp
// Problem: Library code captures context unnecessarily
public async Task<Data> GetDataAsync()
{
    var response = await _httpClient.GetAsync(url); // Captures context
    return await response.Content.ReadFromJsonAsync<Data>(); // Also captures
}

// Better for library code
public async Task<Data> GetDataAsync()
{
    var response = await _httpClient.GetAsync(url).ConfigureAwait(false);
    return await response.Content.ReadFromJsonAsync<Data>().ConfigureAwait(false);
}
```

### 6. Task Not Started
**Likelihood: Medium**

Creating a Task with `new Task()` but not starting it.

```csharp
// Problem: Task created but never started
var task = new Task(() => DoWork()); // Not started
await task; // Hangs forever

// Correct approach
var task = Task.Run(() => DoWork());
await task;
```

### 7. Cancellation Token Not Honored
**Likelihood: Medium**

Ignoring CancellationToken, causing operations to continue after cancellation.

```csharp
// Problem: Token passed but not checked
public async Task LongRunningAsync(CancellationToken cancellationToken)
{
    foreach (var item in items)
    {
        await ProcessItemAsync(item); // Doesn't pass or check token
    }
}
```

### 8. Exception Lost in Task
**Likelihood: Low-Medium**

Exceptions in unawaited tasks being swallowed.

```csharp
// Problem: Exception thrown but never observed
public void StartBackgroundWork()
{
    Task.Run(async () =>
    {
        throw new InvalidOperationException("Error!"); // Lost exception
    });
}
```

---

## Investigation Steps

### Step 1: Identify the Symptom
```
Symptoms and likely causes:
- Application hangs → Deadlock (sync-over-async)
- Random failures → Missing await or async void
- TaskCanceledException → Cancellation or timeout
- Operation continues after cancel → Token not honored
- Memory leaks → Unawaited tasks accumulating
```

### Step 2: Check for Sync-Over-Async
```csharp
// Search codebase for these patterns:
.Result
.Wait()
.GetAwaiter().GetResult()
Task.WaitAll
Task.WaitAny

// In controllers or handlers, these cause deadlocks
```

### Step 3: Verify Await Usage
```csharp
// Search for async method calls without await
// Look for CS4014 warning: "call is not awaited"

// Check that all async paths are awaited
public async Task ProcessAsync()
{
    await Step1Async();  // Correct
    Step2Async();        // Missing await - problem!
    await Step3Async();  // Correct
}
```

### Step 4: Check for Async Void
```csharp
// Search for "async void" - should only be in event handlers
async void  // Problem in most cases

// Event handlers are the exception
private async void Button_Click(object sender, EventArgs e)
{
    await DoWorkAsync(); // OK for event handlers only
}
```

### Step 5: Trace the Deadlock
```
1. Set breakpoint at the blocking call (.Result, .Wait())
2. Check what thread is blocked
3. Find the async method being awaited
4. Check if it needs to resume on the blocked context
```

### Step 6: Check Cancellation Flow
```csharp
// Verify token is passed through the call chain
public async Task ProcessAsync(CancellationToken ct)
{
    await _httpClient.GetAsync(url, ct);     // Passed
    await ProcessDataAsync(data);             // Missing - problem
    await ProcessDataAsync(data, ct);         // Correct
}
```

---

## Quick Fixes

### Fix 1: Convert to Async All the Way
```csharp
// Before - sync-over-async
public string GetData()
{
    return GetDataAsync().Result;
}

// After - async all the way
public async Task<string> GetDataAsync()
{
    return await GetDataInternalAsync();
}
```

### Fix 2: Add Missing Await
```csharp
// Before
public async Task ProcessAsync()
{
    ValidateAsync(); // Missing await
}

// After
public async Task ProcessAsync()
{
    await ValidateAsync();
}
```

### Fix 3: Convert Async Void to Async Task
```csharp
// Before
public async void ProcessBackgroundAsync()
{
    await DoWorkAsync();
}

// After
public async Task ProcessBackgroundAsync()
{
    await DoWorkAsync();
}
```

### Fix 4: Add ConfigureAwait(false) in Libraries
```csharp
// Before
public async Task<Data> LibraryMethodAsync()
{
    var result = await _client.GetAsync(url);
    return await ParseAsync(result);
}

// After
public async Task<Data> LibraryMethodAsync()
{
    var result = await _client.GetAsync(url).ConfigureAwait(false);
    return await ParseAsync(result).ConfigureAwait(false);
}
```

### Fix 5: Use Task.Run for CPU-Bound Work
```csharp
// Before - blocks thread pool
public async Task<int> CalculateAsync()
{
    return ExpensiveCalculation(); // CPU-bound, blocks
}

// After - offloads to thread pool
public async Task<int> CalculateAsync()
{
    return await Task.Run(() => ExpensiveCalculation());
}
```

### Fix 6: Honor Cancellation Token
```csharp
// Before
public async Task ProcessItemsAsync(CancellationToken ct)
{
    foreach (var item in items)
    {
        await ProcessAsync(item);
    }
}

// After
public async Task ProcessItemsAsync(CancellationToken ct)
{
    foreach (var item in items)
    {
        ct.ThrowIfCancellationRequested();
        await ProcessAsync(item, ct);
    }
}
```

### Fix 7: Handle Task Exceptions
```csharp
// Before - exception lost
Task.Run(async () => await DoWorkAsync());

// After - exception logged
_ = Task.Run(async () =>
{
    try
    {
        await DoWorkAsync();
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Background task failed");
    }
});
```

---

## Prevention Patterns

### Pattern 1: Async All the Way
```csharp
// Controller
public async Task<IActionResult> GetOrder(int id)
{
    var order = await _orderService.GetByIdAsync(id);
    return Ok(order);
}

// Service
public async Task<Order> GetByIdAsync(int id)
{
    return await _repository.GetByIdAsync(id);
}

// Repository
public async Task<Order> GetByIdAsync(int id)
{
    return await _context.Orders.FindAsync(id);
}
```

### Pattern 2: Return Task Directly When Possible
```csharp
// Instead of async/await overhead
public async Task<Order> GetByIdAsync(int id)
{
    return await _context.Orders.FindAsync(id);
}

// Return task directly (when no additional processing needed)
public Task<Order?> GetByIdAsync(int id)
{
    return _context.Orders.FindAsync(id).AsTask();
}
```

### Pattern 3: Structured Background Tasks
```csharp
public class BackgroundTaskService : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessQueueAsync(stoppingToken);
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                // Graceful shutdown
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Background processing failed");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }
}
```

### Pattern 4: Timeout Handling
```csharp
public async Task<Data> GetDataWithTimeoutAsync(CancellationToken cancellationToken)
{
    using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
    cts.CancelAfter(TimeSpan.FromSeconds(30));

    try
    {
        return await _client.GetDataAsync(cts.Token);
    }
    catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
    {
        throw new TimeoutException("Operation timed out after 30 seconds");
    }
}
```

### Pattern 5: ValueTask for Hot Paths
```csharp
// Use ValueTask for methods that often complete synchronously
public ValueTask<Data> GetCachedDataAsync(string key)
{
    if (_cache.TryGetValue(key, out var cached))
    {
        return ValueTask.FromResult(cached); // No allocation
    }

    return new ValueTask<Data>(LoadDataAsync(key)); // Async path
}
```

### Pattern 6: Avoid Async in Constructors
```csharp
// Problem - can't await in constructor
public class MyService
{
    public MyService()
    {
        InitializeAsync().Wait(); // Deadlock risk
    }
}

// Solution - factory pattern
public class MyService
{
    private MyService() { }

    public static async Task<MyService> CreateAsync()
    {
        var service = new MyService();
        await service.InitializeAsync();
        return service;
    }
}
```
