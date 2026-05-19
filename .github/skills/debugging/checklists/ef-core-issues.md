# Entity Framework Core Issues Debugging Checklist

Systematic approach to diagnosing and resolving EF Core problems in .NET applications.

## Common Causes (Ranked by Likelihood)

### 1. N+1 Query Problem
**Likelihood: Very High**

Loading related entities in a loop instead of using Include.

```csharp
// Problem: N+1 queries - 1 query for orders, N queries for customers
var orders = await _context.Orders.ToListAsync();
foreach (var order in orders)
{
    var customer = order.Customer; // Lazy load or null
    Console.WriteLine(customer.Name); // Additional query each iteration
}
```

### 2. DbContext Disposed/Out of Scope
**Likelihood: High**

Accessing entities after their DbContext has been disposed.

```csharp
// Problem: Context disposed before navigation accessed
public async Task<Order> GetOrderAsync(int id)
{
    using var context = new AppDbContext();
    return await context.Orders.FindAsync(id);
} // Context disposed here

// Later...
var order = await GetOrderAsync(1);
var customer = order.Customer; // ObjectDisposedException or null
```

### 3. Tracking Conflicts
**Likelihood: High**

Multiple tracked entities with the same key causing conflicts.

```csharp
// Problem: Tracking conflict
var order1 = await _context.Orders.FindAsync(1);
var order2 = new Order { Id = 1, Status = "Updated" };
_context.Orders.Update(order2); // Throws - already tracking entity with Id=1
```

### 4. Missing Include for Navigation Properties
**Likelihood: High**

Expecting related data without explicitly loading it.

```csharp
// Problem: Navigation property is null without Include
var order = await _context.Orders
    .FirstOrDefaultAsync(o => o.Id == orderId);

var customerName = order.Customer.Name; // NullReferenceException
```

### 5. Detached Entity Updates
**Likelihood: Medium-High**

Trying to update an entity that isn't tracked.

```csharp
// Problem: Entity from different context or deserialized
public async Task UpdateOrderAsync(Order order)
{
    _context.SaveChangesAsync(); // No changes detected - order isn't tracked
}
```

### 6. Lazy Loading Without Proxy
**Likelihood: Medium**

Expecting lazy loading without proper configuration.

```csharp
// Problem: Lazy loading not configured
var order = await _context.Orders.FindAsync(1);
var items = order.Items; // Null - lazy loading not enabled
```

### 7. Concurrency Conflicts
**Likelihood: Medium**

Optimistic concurrency violations when data changed between read and write.

```csharp
// Problem: Row version changed between read and update
var order = await _context.Orders.FindAsync(1);
// Meanwhile, another process updates the same order
order.Status = "Completed";
await _context.SaveChangesAsync(); // DbUpdateConcurrencyException
```

### 8. Migration Issues
**Likelihood: Medium**

Database schema out of sync with model.

```csharp
// Problem: Column doesn't exist in database
public class Order
{
    public string NewProperty { get; set; } // Added to model
}

// Query fails because column doesn't exist in database
var orders = await _context.Orders.ToListAsync();
// SqlException: Invalid column name 'NewProperty'
```

### 9. Query Filter Interference
**Likelihood: Low-Medium**

Global query filters affecting unexpected queries.

```csharp
// Problem: Soft delete filter hides expected records
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Order>().HasQueryFilter(o => !o.IsDeleted);
}

// This returns null even though order exists (but is soft-deleted)
var order = await _context.Orders.FindAsync(deletedOrderId);
```

---

## Investigation Steps

### Step 1: Enable EF Core Logging
```csharp
// In Program.cs or DbContext
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder
        .LogTo(Console.WriteLine, LogLevel.Information)
        .EnableSensitiveDataLogging() // Shows parameter values
        .EnableDetailedErrors();
}

// Or via appsettings.json
{
    "Logging": {
        "LogLevel": {
            "Microsoft.EntityFrameworkCore.Database.Command": "Information"
        }
    }
}
```

### Step 2: Check Query Translation
```csharp
// Use ToQueryString() to see generated SQL
var query = _context.Orders
    .Include(o => o.Customer)
    .Where(o => o.Status == "Active");

var sql = query.ToQueryString();
Console.WriteLine(sql);
```

### Step 3: Verify Tracking State
```csharp
// Check entity state
var entry = _context.Entry(order);
Console.WriteLine($"State: {entry.State}");
Console.WriteLine($"Is Tracked: {_context.ChangeTracker.Entries().Any(e => e.Entity == order)}");

// List all tracked entities
foreach (var tracked in _context.ChangeTracker.Entries())
{
    Console.WriteLine($"{tracked.Entity.GetType().Name}: {tracked.State}");
}
```

### Step 4: Identify N+1 Queries
```
1. Enable SQL logging
2. Run the operation
3. Count the number of queries executed
4. If queries = N + 1 (where N is collection size), you have N+1 problem
```

### Step 5: Check DbContext Lifetime
```csharp
// Verify DI registration
// Scoped (per-request) is recommended for web apps
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString));

// Check for manual instantiation without proper disposal
using var context = new AppDbContext(); // Ensure using statement
```

### Step 6: Verify Migration Status
```bash
# Check pending migrations
dotnet ef migrations list

# Check if database matches model
dotnet ef database update --dry-run
```

---

## Quick Fixes

### Fix 1: Add Include for Navigation Properties
```csharp
// Before - navigation property null
var order = await _context.Orders.FindAsync(id);

// After - navigation property loaded
var order = await _context.Orders
    .Include(o => o.Customer)
    .Include(o => o.Items)
    .FirstOrDefaultAsync(o => o.Id == id);
```

### Fix 2: Use AsNoTracking for Read-Only Queries
```csharp
// Before - entities tracked unnecessarily
var orders = await _context.Orders.ToListAsync();

// After - no tracking overhead
var orders = await _context.Orders
    .AsNoTracking()
    .ToListAsync();
```

### Fix 3: Fix Tracking Conflicts
```csharp
// Option 1: Detach existing entity
var existing = await _context.Orders.FindAsync(order.Id);
if (existing != null)
{
    _context.Entry(existing).State = EntityState.Detached;
}
_context.Orders.Update(order);

// Option 2: Update properties instead of entity
var existing = await _context.Orders.FindAsync(order.Id);
_context.Entry(existing).CurrentValues.SetValues(order);
```

### Fix 4: Attach Detached Entity
```csharp
// Before - detached entity not saved
public async Task UpdateAsync(Order order)
{
    await _context.SaveChangesAsync(); // Nothing happens
}

// After - explicitly attach and mark modified
public async Task UpdateAsync(Order order)
{
    _context.Attach(order);
    _context.Entry(order).State = EntityState.Modified;
    await _context.SaveChangesAsync();
}
```

### Fix 5: Fix N+1 with Projection
```csharp
// Before - N+1 problem
var orders = await _context.Orders.ToListAsync();
var dtos = orders.Select(o => new OrderDto
{
    Id = o.Id,
    CustomerName = o.Customer.Name // N queries
});

// After - single query with projection
var dtos = await _context.Orders
    .Select(o => new OrderDto
    {
        Id = o.Id,
        CustomerName = o.Customer.Name // Translated to JOIN
    })
    .ToListAsync();
```

### Fix 6: Handle Concurrency Conflict
```csharp
try
{
    await _context.SaveChangesAsync();
}
catch (DbUpdateConcurrencyException ex)
{
    foreach (var entry in ex.Entries)
    {
        var databaseValues = await entry.GetDatabaseValuesAsync();
        if (databaseValues == null)
        {
            // Entity was deleted
            throw new NotFoundException("Entity was deleted by another user");
        }

        // Option 1: Client wins - keep current values
        entry.OriginalValues.SetValues(databaseValues);
        await _context.SaveChangesAsync();

        // Option 2: Database wins - reload values
        await entry.ReloadAsync();
    }
}
```

### Fix 7: Bypass Query Filters
```csharp
// Temporarily ignore global filters
var allOrders = await _context.Orders
    .IgnoreQueryFilters()
    .ToListAsync();
```

---

## Prevention Patterns

### Pattern 1: Repository with Eager Loading Options
```csharp
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(int id, bool includeCustomer = false, bool includeItems = false);
}

public class OrderRepository : IOrderRepository
{
    public async Task<Order?> GetByIdAsync(int id, bool includeCustomer = false, bool includeItems = false)
    {
        var query = _context.Orders.AsQueryable();

        if (includeCustomer)
            query = query.Include(o => o.Customer);

        if (includeItems)
            query = query.Include(o => o.Items);

        return await query.FirstOrDefaultAsync(o => o.Id == id);
    }
}
```

### Pattern 2: Specification Pattern
```csharp
public class OrderWithCustomerSpec : Specification<Order>
{
    public OrderWithCustomerSpec(int orderId)
    {
        Query
            .Where(o => o.Id == orderId)
            .Include(o => o.Customer);
    }
}

// Usage
var order = await _repository.GetBySpecAsync(new OrderWithCustomerSpec(orderId));
```

### Pattern 3: Explicit Loading When Needed
```csharp
public async Task<Order> GetOrderWithItemsIfNeededAsync(int id, bool needItems)
{
    var order = await _context.Orders.FindAsync(id);

    if (needItems && order != null)
    {
        await _context.Entry(order)
            .Collection(o => o.Items)
            .LoadAsync();
    }

    return order;
}
```

### Pattern 4: Split Queries for Complex Includes
```csharp
// Single query can cause cartesian explosion
var order = await _context.Orders
    .Include(o => o.Items)
    .Include(o => o.Payments)
    .Include(o => o.ShippingDetails)
    .AsSplitQuery() // Executes as separate queries
    .FirstOrDefaultAsync(o => o.Id == id);
```

### Pattern 5: Compiled Queries for Hot Paths
```csharp
private static readonly Func<AppDbContext, int, Task<Order?>> GetOrderById =
    EF.CompileAsyncQuery((AppDbContext context, int id) =>
        context.Orders
            .Include(o => o.Customer)
            .FirstOrDefault(o => o.Id == id));

public async Task<Order?> GetByIdAsync(int id)
{
    return await GetOrderById(_context, id);
}
```

### Pattern 6: Unit of Work with Scoped Context
```csharp
public interface IUnitOfWork : IDisposable
{
    IOrderRepository Orders { get; }
    ICustomerRepository Customers { get; }
    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}

// Ensures all repositories use same context instance
public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _context;

    public UnitOfWork(AppDbContext context)
    {
        _context = context;
        Orders = new OrderRepository(_context);
        Customers = new CustomerRepository(_context);
    }

    public async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        return await _context.SaveChangesAsync(cancellationToken);
    }
}
```

### Pattern 7: Row Version for Concurrency
```csharp
public class Order
{
    public int Id { get; set; }

    [Timestamp]
    public byte[] RowVersion { get; set; }
}

// Or via Fluent API
modelBuilder.Entity<Order>()
    .Property(o => o.RowVersion)
    .IsRowVersion();
```
