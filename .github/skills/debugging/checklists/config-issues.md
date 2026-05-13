# Configuration Issues

Investigation checklist for configuration and appsettings errors.

## Symptoms

- `null` values from `IOptions<T>` or `IConfiguration`
- `OptionsValidationException` at startup
- Wrong environment settings loaded
- Missing connection strings
- `JsonException` when binding configuration

## Quick Checks

1. **Is the section name correct?**
   - Check `appsettings.json` section name matches code
   - Section names are case-sensitive

2. **Is the environment correct?**
   - Check `ASPNETCORE_ENVIRONMENT` or `DOTNET_ENVIRONMENT`
   - Verify correct `appsettings.{Environment}.json` exists

3. **Are property names matching?**
   - JSON property names must match C# property names (case-insensitive by default)

4. **Is the configuration bound?**
   - Check for `Configure<T>()` or `Bind()` calls in startup

## Root Cause Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| Properties are null | Section name mismatch | Match JSON section name exactly |
| IOptions<T> is null | Not registered | Add `services.Configure<T>(config.GetSection("Name"))` |
| Wrong environment | Env var not set | Set `ASPNETCORE_ENVIRONMENT` |
| Validation exception | Invalid config value | Fix value or adjust validation rules |
| Missing connection string | Key mismatch or missing file | Check `ConnectionStrings:Name` key |

## Common Mistakes

### Section Name Mismatch

```json
// appsettings.json
{
  "EmailSettings": {  // Note: "EmailSettings"
    "SmtpHost": "smtp.example.com"
  }
}
```

```csharp
// 🔴 Wrong section name
services.Configure<EmailSettings>(config.GetSection("Email"));

// ✅ Correct section name
services.Configure<EmailSettings>(config.GetSection("EmailSettings"));
```

### Missing Nested Section

```json
{
  "App": {
    "Email": {
      "Host": "smtp.example.com"
    }
  }
}
```

```csharp
// 🔴 Missing nested path
config.GetSection("Email");

// ✅ Full path
config.GetSection("App:Email");
```

### Type Mismatch

```json
{
  "Settings": {
    "MaxRetries": "five"  // 🔴 Should be number
  }
}
```

```csharp
public class Settings
{
    public int MaxRetries { get; set; }  // Will fail to bind
}
```

### Environment-Specific Override Not Applied

```
// Files load order:
1. appsettings.json (base)
2. appsettings.{Environment}.json (override)
3. Environment variables
4. Command line args

// 🔴 Environment not set, defaults to Production
// Check: echo $ASPNETCORE_ENVIRONMENT
```

## Debugging Steps

1. **Log loaded configuration:**
   ```csharp
   var section = config.GetSection("MySettings");
   foreach (var child in section.GetChildren())
   {
       Console.WriteLine($"{child.Key} = {child.Value}");
   }
   ```

2. **Check environment:**
   ```csharp
   Console.WriteLine($"Environment: {builder.Environment.EnvironmentName}");
   ```

3. **Validate at startup:**
   ```csharp
   services.AddOptions<EmailSettings>()
       .Bind(config.GetSection("EmailSettings"))
       .ValidateDataAnnotations()
       .ValidateOnStart();  // Fail fast
   ```

4. **Check loaded providers:**
   ```csharp
   foreach (var provider in ((IConfigurationRoot)config).Providers)
   {
       Console.WriteLine(provider.GetType().Name);
   }
   ```

## Connection String Issues

```csharp
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=..."
  }
}

// 🔴 Wrong key
config.GetConnectionString("Default");

// ✅ Correct key
config.GetConnectionString("DefaultConnection");

// Or from section
config.GetSection("ConnectionStrings:DefaultConnection").Value;
```

## Environment Variables

```bash
# Override nested values using __ (double underscore)
export EmailSettings__SmtpHost=smtp.production.com
export ConnectionStrings__DefaultConnection="Server=prod;..."
```

## Prevention

- Use `ValidateOnStart()` for early failure
- Add `[Required]` attributes to required properties
- Document all configuration sections in README
- Use strongly-typed options with validation
- Keep environment-specific secrets in User Secrets or Key Vault
