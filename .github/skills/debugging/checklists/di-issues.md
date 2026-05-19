# Dependency Injection Issues

Investigation checklist for DI-related errors in .NET applications.

## Symptoms

- `InvalidOperationException: Unable to resolve service for type 'X'`
- `InvalidOperationException: A suitable constructor for type 'X' could not be located`
- `ObjectDisposedException` when accessing scoped services
- Unexpected `null` values for injected dependencies

## Quick Checks

1. **Is the service registered?**
   - Check `Program.cs` or `Startup.cs` for `services.Add*<TService>()`
   - Search for the interface/class name in DI configuration

2. **Is the lifetime correct?**
   - Scoped in singleton? → `InvalidOperationException`
   - Singleton in scoped? → State pollution across requests

3. **Are all constructor dependencies registered?**
   - Check the class constructor
   - Verify each parameter type is registered

4. **Is the registration order correct?**
   - Some services depend on others being registered first

## Root Cause Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| "Unable to resolve service" | Service not registered | Add `services.AddScoped<IService, Service>()` |
| "No suitable constructor" | Constructor has unregistered params | Register missing dependencies |
| "Cannot consume scoped from singleton" | Scoped service in singleton | Change lifetime or use `IServiceScopeFactory` |
| Unexpected null | Manually instantiated instead of injected | Use DI, don't `new` the class |
| Multiple implementations conflict | Multiple registrations for same interface | Use named/keyed services or remove duplicate |

## Common Mistakes

### Wrong Lifetime

```csharp
// 🔴 DbContext is scoped, but service is singleton
services.AddSingleton<IOrderService, OrderService>();
services.AddDbContext<AppDbContext>();

// ✅ Match lifetimes
services.AddScoped<IOrderService, OrderService>();
```

### Manual Instantiation

```csharp
// 🔴 Dependencies not injected
var service = new OrderService();

// ✅ Let DI container create it
public class OrderController(IOrderService orderService) { }
```

### Circular Dependencies

```csharp
// 🔴 A depends on B, B depends on A
public class ServiceA(IServiceB serviceB) { }
public class ServiceB(IServiceA serviceA) { }

// ✅ Use Lazy<T> or refactor to break cycle
public class ServiceA(Lazy<IServiceB> serviceB) { }
```

### Scoped Service in Background Task

```csharp
// 🔴 Accessing scoped service after request ends
public class BackgroundJob
{
    private readonly IOrderService _orderService; // May be disposed!
}

// ✅ Create new scope for background work
public class BackgroundJob(IServiceScopeFactory scopeFactory)
{
    public async Task ExecuteAsync()
    {
        using var scope = scopeFactory.CreateScope();
        var orderService = scope.ServiceProvider.GetRequiredService<IOrderService>();
    }
}
```

## Debugging Steps

1. **Enable detailed DI errors:**
   ```csharp
   builder.Host.UseDefaultServiceProvider(options =>
   {
       options.ValidateScopes = true;
       options.ValidateOnBuild = true;  // Fail fast at startup
   });
   ```

2. **Check registration:**
   ```csharp
   var descriptor = services.FirstOrDefault(d => d.ServiceType == typeof(IMyService));
   Console.WriteLine($"Registered: {descriptor?.ImplementationType?.Name}");
   ```

3. **Trace constructor resolution:**
   - Add logging to constructors
   - Check which dependencies are null

## Prevention

- Enable `ValidateOnBuild` in development
- Use constructor injection exclusively
- Match lifetimes (scoped → scoped, singleton → singleton)
- Avoid `IServiceProvider` direct access when possible
- Document required registrations in library README
