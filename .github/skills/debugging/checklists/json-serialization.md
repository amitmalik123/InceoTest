# JSON Serialization Issues

Investigation checklist for System.Text.Json and Newtonsoft.Json errors.

## Symptoms

- Properties missing from JSON output
- `JsonException` during serialization/deserialization
- Unexpected `null` values after deserialization
- Case sensitivity issues
- Circular reference exceptions
- Date format problems

## Quick Checks

1. **Which serializer is being used?**
   - ASP.NET Core uses `System.Text.Json` by default
   - Some libraries use `Newtonsoft.Json`

2. **Are properties public with getters/setters?**
   - Private or init-only properties may not serialize

3. **Is the property naming policy correct?**
   - `System.Text.Json` is case-sensitive by default

4. **Are there circular references?**
   - Check for navigation properties pointing back

## Root Cause Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| Property missing from output | Private setter | Add `[JsonInclude]` or make public |
| `JsonException` on deserialize | Type mismatch or missing constructor | Match types, add parameterless constructor |
| Null after deserialize | Case mismatch | Configure `PropertyNameCaseInsensitive` |
| Circular reference | Navigation properties | Use `ReferenceHandler.Preserve` or DTOs |
| Date format wrong | Default format differs | Configure `JsonSerializerOptions` |

## System.Text.Json Issues

### Case Sensitivity

```csharp
// 🔴 Default is case-sensitive
var json = """{"name": "John"}""";
var person = JsonSerializer.Deserialize<Person>(json);
// person.Name is null because "name" != "Name"

// ✅ Configure case-insensitive
var options = new JsonSerializerOptions
{
    PropertyNameCaseInsensitive = true
};
var person = JsonSerializer.Deserialize<Person>(json, options);
```

### Private Setters

```csharp
public class Order
{
    public int Id { get; private set; }  // 🔴 Won't deserialize
}

// ✅ Option 1: Add [JsonInclude]
public class Order
{
    [JsonInclude]
    public int Id { get; private set; }
}

// ✅ Option 2: Add constructor
public class Order
{
    public int Id { get; }

    [JsonConstructor]
    public Order(int id) => Id = id;
}
```

### Circular References

```csharp
public class Parent
{
    public List<Child> Children { get; set; }
}

public class Child
{
    public Parent Parent { get; set; }  // 🔴 Circular reference
}

// ✅ Configure reference handling
var options = new JsonSerializerOptions
{
    ReferenceHandler = ReferenceHandler.IgnoreCycles,
    // Or: ReferenceHandler = ReferenceHandler.Preserve
};
```

### Missing Parameterless Constructor

```csharp
// 🔴 No parameterless constructor
public class Order
{
    public Order(int id) => Id = id;
    public int Id { get; }
}

// ✅ Add parameterless constructor or [JsonConstructor]
public class Order
{
    public Order() { }  // Parameterless
    public Order(int id) => Id = id;
    public int Id { get; set; }
}
```

## Newtonsoft.Json Issues

### Different Defaults

```csharp
// Newtonsoft defaults (more lenient):
// - Case-insensitive
// - Handles private setters
// - Supports circular references with settings

// When migrating to System.Text.Json:
var options = new JsonSerializerOptions
{
    PropertyNameCaseInsensitive = true,
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
};
```

### Conflicting Attributes

```csharp
// 🔴 Mixed attributes cause confusion
public class Order
{
    [JsonProperty("order_id")]           // Newtonsoft
    [JsonPropertyName("orderId")]        // System.Text.Json
    public int Id { get; set; }
}

// ✅ Use consistent serializer attributes
```

## ASP.NET Core Configuration

### Configure Globally

```csharp
// Program.cs
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.PropertyNameCaseInsensitive = true;
        options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    });
```

### Use Newtonsoft Instead

```csharp
// If you need Newtonsoft compatibility
builder.Services.AddControllers()
    .AddNewtonsoftJson(options =>
    {
        options.SerializerSettings.ReferenceLoopHandling = ReferenceLoopHandling.Ignore;
    });
```

## Common Patterns

### DTO Pattern (Avoid Circular References)

```csharp
// Instead of serializing entities directly
public class OrderDto
{
    public int Id { get; set; }
    public List<OrderItemDto> Items { get; set; }  // No back-reference
}
```

### Custom Converters

```csharp
public class DateOnlyConverter : JsonConverter<DateOnly>
{
    public override DateOnly Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        return DateOnly.Parse(reader.GetString()!);
    }

    public override void Write(Utf8JsonWriter writer, DateOnly value, JsonSerializerOptions options)
    {
        writer.WriteStringValue(value.ToString("yyyy-MM-dd"));
    }
}
```

## Debugging Steps

1. **Serialize to see output:**
   ```csharp
   var json = JsonSerializer.Serialize(obj, new JsonSerializerOptions { WriteIndented = true });
   Console.WriteLine(json);
   ```

2. **Check for attribute conflicts:**
   - Search for `[JsonProperty]` and `[JsonPropertyName]` in same class

3. **Validate JSON input:**
   ```csharp
   try
   {
       JsonDocument.Parse(jsonString);
   }
   catch (JsonException ex)
   {
       Console.WriteLine($"Invalid JSON: {ex.Message}");
   }
   ```

## Prevention

- Use DTOs for API responses, not entities
- Configure serializer options globally
- Test serialization round-trip in unit tests
- Avoid mixing Newtonsoft and System.Text.Json
- Document expected JSON format in API specs
