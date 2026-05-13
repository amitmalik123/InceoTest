# NullReferenceException Debugging Checklist

Systematic approach to diagnosing and resolving `NullReferenceException` in .NET applications.

## Common Causes (Ranked by Likelihood)

### 1. Uninitialized or Null Return Values
**Likelihood: Very High**

The called method returns null when a value was expected.

```csharp
// Problem: GetByIdAsync returns null when not found
var user = await _userRepository.GetByIdAsync(userId);
var name = user.Name; // NullReferenceException if user is null
```

### 2. Missing Dependency Injection Registration
**Likelihood: High**

Service not registered in DI container, injected as null.

```csharp
// Problem: IEmailService not registered
public class OrderService
{
    private readonly IEmailService _emailService; // null if not registered

    public OrderService(IEmailService emailService)
    {
        _emailService = emailService;
    }
}
```

### 3. Async Method Returns Null
**Likelihood: High**

Async methods returning `Task<T>` where T is null.

```csharp
// Problem: Awaiting a method that returns null
var result = await GetDataAsync(); // returns null
result.Process(); // NullReferenceException
```

### 4. Navigation Property Not Loaded
**Likelihood: Medium-High**

EF Core navigation properties accessed without Include/loading.

```csharp
// Problem: Related entity not loaded
var order = await _context.Orders.FindAsync(orderId);
var customerName = order.Customer.Name; // Customer is null without Include
```

### 5. Collection Not Initialized
**Likelihood: Medium**

Collection properties returning null instead of empty collection.

```csharp
// Problem: Collection property is null
public class Order
{
    public List<OrderItem> Items { get; set; } // null by default
}

foreach (var item in order.Items) { } // NullReferenceException
```

### 6. String Operations on Null
**Likelihood: Medium**

Calling string methods on null string values.

```csharp
// Problem: Null string from database or input
string input = GetUserInput(); // returns null
var upper = input.ToUpper(); // NullReferenceException
```

### 7. Event Handler Not Subscribed
**Likelihood: Low-Medium**

Invoking events with no subscribers.

```csharp
// Problem: Event has no subscribers
public event EventHandler DataChanged;
DataChanged.Invoke(this, EventArgs.Empty); // NullReferenceException
```

### 8. Deserialization Returns Null
**Likelihood: Low-Medium**

JSON/XML deserialization producing null objects.

```csharp
// Problem: Empty or invalid JSON
var data = JsonSerializer.Deserialize<MyClass>(json); // null if json is "null"
data.Property = value; // NullReferenceException
```

---

## Investigation Steps

### Step 1: Locate the Exact Line
```
1. Check the stack trace for the exact line number
2. Identify which object on that line could be null
3. If multiple objects, set breakpoint and inspect each
```

### Step 2: Trace the Null Value
```
1. Find where the null object was assigned or returned
2. Check method return values for null scenarios
3. Verify constructor initialization
4. Check DI registration if injected dependency
```

### Step 3: Check Data Flow
```
1. Trace the object from creation to usage
2. Check for conditional assignments that might skip initialization
3. Verify async flow doesn't lose object references
4. Check for null returns from database queries
```

### Step 4: Verify DI Registration (if applicable)
```csharp
// Check Program.cs or Startup.cs for registration
builder.Services.AddScoped<IMyService, MyService>();
builder.Services.AddTransient<IOtherService, OtherService>();

// Verify interface matches implementation
// Verify lifetime scope is appropriate
```

### Step 5: Check EF Core Loading (if entity)
```csharp
// Verify Include() for navigation properties
var order = await _context.Orders
    .Include(o => o.Customer)    // Required for o.Customer access
    .Include(o => o.Items)       // Required for o.Items access
    .FirstOrDefaultAsync(o => o.Id == orderId);
```

---

## Quick Fixes

### Fix 1: Null Conditional Operator
```csharp
// Before
var name = user.Name;

// After
var name = user?.Name;
```

### Fix 2: Null Coalescing Operator
```csharp
// Before
var items = order.Items;

// After
var items = order.Items ?? new List<OrderItem>();
```

### Fix 3: Null Check with Exception
```csharp
// Before
var user = await _userRepository.GetByIdAsync(userId);
return user.Name;

// After
var user = await _userRepository.GetByIdAsync(userId)
    ?? throw new NotFoundException($"User {userId} not found");
return user.Name;
```

### Fix 4: Guard Clause
```csharp
public void ProcessUser(User user)
{
    ArgumentNullException.ThrowIfNull(user);
    // Safe to use user here
}
```

### Fix 5: Initialize Collections
```csharp
// Before
public List<OrderItem> Items { get; set; }

// After
public List<OrderItem> Items { get; set; } = new();
```

### Fix 6: Register Missing Service
```csharp
// Add to Program.cs
builder.Services.AddScoped<IMissingService, MissingServiceImplementation>();
```

### Fix 7: Safe Event Invocation
```csharp
// Before
DataChanged.Invoke(this, EventArgs.Empty);

// After
DataChanged?.Invoke(this, EventArgs.Empty);
```

---

## Prevention Patterns

### Pattern 1: Enable Nullable Reference Types
```xml
<!-- In .csproj -->
<PropertyGroup>
    <Nullable>enable</Nullable>
</PropertyGroup>
```

```csharp
// Compiler warns about potential null
public string? GetName() { } // Explicitly nullable
public string GetRequiredName() { } // Must not return null
```

### Pattern 2: Repository Pattern with Optional Returns
```csharp
public interface IRepository<T>
{
    Task<T?> GetByIdAsync(int id); // Clearly nullable
    Task<T> GetByIdRequiredAsync(int id); // Throws if not found
}

public async Task<T> GetByIdRequiredAsync(int id)
{
    return await GetByIdAsync(id)
        ?? throw new NotFoundException($"{typeof(T).Name} with ID {id} not found");
}
```

### Pattern 3: Initialize Collections in Constructors
```csharp
public class Order
{
    public List<OrderItem> Items { get; set; } = new();
    public ICollection<Tag> Tags { get; set; } = new HashSet<Tag>();
}
```

### Pattern 4: Validate at Boundaries
```csharp
public class OrderService
{
    public async Task<OrderDto> CreateOrderAsync(CreateOrderRequest request)
    {
        // Validate at service boundary
        ArgumentNullException.ThrowIfNull(request);
        ArgumentNullException.ThrowIfNull(request.CustomerId);

        // Now safe to proceed
    }
}
```

### Pattern 5: Use Required Keyword (.NET 7+)
```csharp
public class CreateOrderRequest
{
    public required string CustomerId { get; init; }
    public required List<OrderItemRequest> Items { get; init; }
}
```

### Pattern 6: Fail-Fast DI Validation
```csharp
// In Program.cs, validate all services resolve
var app = builder.Build();

// Development environment validation
if (app.Environment.IsDevelopment())
{
    using var scope = app.Services.CreateScope();
    // Attempt to resolve critical services
    _ = scope.ServiceProvider.GetRequiredService<IOrderService>();
    _ = scope.ServiceProvider.GetRequiredService<IUserService>();
}
```
