# Performance Issues

Investigation checklist for timeouts, memory leaks, and slow operations.

## Symptoms

- Request timeouts
- High memory usage / OutOfMemoryException
- Slow API responses
- Database query timeouts
- High CPU utilization
- Application hangs or freezes

## Quick Checks

1. **Is it the database?**
   - Check query execution times
   - Look for missing indexes
   - Check for N+1 queries

2. **Is it memory?**
   - Check for large object allocations
   - Look for undisposed resources
   - Check for collection growth

3. **Is it external calls?**
   - Check HTTP client timeouts
   - Look for sequential calls that could be parallel
   - Check for retry storms

4. **Is it the code?**
   - Look for synchronous over async
   - Check for blocking calls
   - Look for inefficient algorithms

## Root Cause Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Timeout on list endpoints | N+1 queries | Use `.Include()` or projection |
| Memory grows over time | Resource leak | Dispose IDisposable, check static collections |
| Slow first request | Cold start / JIT | Warm up, use AOT where possible |
| Sporadic timeouts | Connection pool exhaustion | Check connection limits, dispose properly |
| High CPU, low throughput | Sync over async | Use async/await properly |

## Database Performance

### N+1 Query Detection

```csharp
// 🔴 N+1 problem - 1 query for orders + N queries for customers
var orders = context.Orders.ToList();
foreach (var order in orders)
{
    Console.WriteLine(order.Customer.Name);  // Lazy load each customer
}

// ✅ Eager load with Include
var orders = context.Orders
    .Include(o => o.Customer)
    .ToList();

// ✅ Or use projection
var orders = context.Orders
    .Select(o => new { o.Id, CustomerName = o.Customer.Name })
    .ToList();
```

### Missing Indexes

```sql
-- Check for missing index recommendations (SQL Server)
SELECT
    mig.index_group_handle,
    mid.statement AS table_name,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns,
    migs.avg_user_impact
FROM sys.dm_db_missing_index_groups mig
JOIN sys.dm_db_missing_index_group_stats migs
    ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details mid
    ON mig.index_handle = mid.index_handle
ORDER BY migs.avg_user_impact DESC;
```

### Query Timeout

```csharp
// 🔴 Default timeout may be too short for complex queries
var results = await context.Orders.ToListAsync();

// ✅ Increase timeout for specific operations
context.Database.SetCommandTimeout(TimeSpan.FromMinutes(5));

// ✅ Or configure globally
optionsBuilder.UseSqlServer(connectionString,
    options => options.CommandTimeout(120));
```

## Memory Issues

### Unbounded Collections

```csharp
// 🔴 Loading entire table into memory
var allOrders = await context.Orders.ToListAsync();

// ✅ Paginate
var orders = await context.Orders
    .Skip(page * pageSize)
    .Take(pageSize)
    .ToListAsync();

// ✅ Or stream with AsAsyncEnumerable
await foreach (var order in context.Orders.AsAsyncEnumerable())
{
    ProcessOrder(order);
}
```

### Resource Leaks

```csharp
// 🔴 HttpClient not disposed properly
public async Task<string> GetData()
{
    var client = new HttpClient();  // New client each call
    return await client.GetStringAsync(url);
}

// ✅ Use IHttpClientFactory
public class MyService(IHttpClientFactory factory)
{
    public async Task<string> GetData()
    {
        var client = factory.CreateClient();
        return await client.GetStringAsync(url);
    }
}

// 🔴 DbContext held too long
public class OrderService
{
    private readonly AppDbContext _context;  // Singleton with scoped DbContext?
}
```

### Large Object Heap (LOH) Issues

```csharp
// 🔴 Large string concatenation
string result = "";
foreach (var item in items)
{
    result += item.ToString();  // Creates new string each iteration
}

// ✅ Use StringBuilder
var sb = new StringBuilder();
foreach (var item in items)
{
    sb.Append(item.ToString());
}
var result = sb.ToString();

// 🔴 Large arrays
var buffer = new byte[100_000_000];  // Goes to LOH, fragments memory

// ✅ Use ArrayPool for large arrays
var buffer = ArrayPool<byte>.Shared.Rent(100_000_000);
try { /* use buffer */ }
finally { ArrayPool<byte>.Shared.Return(buffer); }
```

## Async/Await Issues

### Sync Over Async

```csharp
// 🔴 Blocking on async - can cause deadlocks and thread pool starvation
public string GetData()
{
    return GetDataAsync().Result;  // Blocks thread
}

// 🔴 Also bad
public string GetData()
{
    return GetDataAsync().GetAwaiter().GetResult();
}

// ✅ Async all the way
public async Task<string> GetDataAsync()
{
    return await httpClient.GetStringAsync(url);
}
```

### Missing ConfigureAwait

```csharp
// In library code, use ConfigureAwait(false)
public async Task<string> GetDataAsync()
{
    var response = await httpClient.GetAsync(url).ConfigureAwait(false);
    return await response.Content.ReadAsStringAsync().ConfigureAwait(false);
}
```

### Task.WhenAll for Parallel Operations

```csharp
// 🔴 Sequential - slow
var user = await GetUserAsync(userId);
var orders = await GetOrdersAsync(userId);
var preferences = await GetPreferencesAsync(userId);

// ✅ Parallel - faster
var userTask = GetUserAsync(userId);
var ordersTask = GetOrdersAsync(userId);
var preferencesTask = GetPreferencesAsync(userId);

await Task.WhenAll(userTask, ordersTask, preferencesTask);

var user = userTask.Result;
var orders = ordersTask.Result;
var preferences = preferencesTask.Result;
```

## HTTP Client Issues

### Connection Pool Exhaustion

```csharp
// 🔴 Creating new HttpClient for each request
public async Task<string> GetData()
{
    using var client = new HttpClient();
    return await client.GetStringAsync(url);
}
// Connections stay in TIME_WAIT state, pool exhausts

// ✅ Use IHttpClientFactory
services.AddHttpClient<MyService>(client =>
{
    client.BaseAddress = new Uri("https://api.example.com");
    client.Timeout = TimeSpan.FromSeconds(30);
});
```

### Retry Storms

```csharp
// 🔴 Aggressive retries can overwhelm downstream services
services.AddHttpClient<MyService>()
    .AddTransientHttpErrorPolicy(p =>
        p.WaitAndRetryAsync(10, _ => TimeSpan.FromMilliseconds(100)));

// ✅ Use exponential backoff with jitter
services.AddHttpClient<MyService>()
    .AddTransientHttpErrorPolicy(p =>
        p.WaitAndRetryAsync(3, retryAttempt =>
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt))
            + TimeSpan.FromMilliseconds(Random.Shared.Next(0, 100))));
```

## Debugging Steps

1. **Profile the application:**
   ```csharp
   // Add timing to suspect code
   var sw = Stopwatch.StartNew();
   await DoOperation();
   _logger.LogInformation("Operation took {Elapsed}ms", sw.ElapsedMilliseconds);
   ```

2. **Check EF Core query logging:**
   ```csharp
   optionsBuilder
       .UseSqlServer(connectionString)
       .LogTo(Console.WriteLine, LogLevel.Information)
       .EnableSensitiveDataLogging();
   ```

3. **Use Application Insights / diagnostics:**
   ```csharp
   services.AddApplicationInsightsTelemetry();
   ```

4. **Check connection pool:**
   ```sql
   -- SQL Server connection usage
   SELECT
       DB_NAME(dbid) as DatabaseName,
       COUNT(*) as NumberOfConnections,
       loginame as LoginName
   FROM sys.sysprocesses
   WHERE dbid > 0
   GROUP BY dbid, loginame;
   ```

5. **Memory dump analysis:**
   ```bash
   # Capture dump
   dotnet-dump collect -p <pid>

   # Analyze
   dotnet-dump analyze <dump-file>
   ```

## Prevention

- Use query profiling in development
- Set up performance budgets and alerts
- Load test before production deployments
- Use caching for frequently accessed data
- Implement pagination for list endpoints
- Use async/await consistently
- Dispose resources properly (use `using` statements)
- Monitor and alert on performance metrics
