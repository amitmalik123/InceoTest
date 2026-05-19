# HTTP/API Error Patterns Debugging Checklist

Systematic approach to diagnosing and resolving HTTP and API communication errors in .NET applications.

## Common Causes (Ranked by Likelihood)

### 1. 401 Unauthorized - Authentication Failure
**Likelihood: Very High**

Missing, expired, or invalid authentication token.

```csharp
// Problem: Missing Authorization header
var response = await _httpClient.GetAsync(url);
// Returns 401 - no token sent

// Problem: Expired token
_httpClient.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", expiredToken);
```

### 2. 400 Bad Request - Invalid Payload
**Likelihood: Very High**

Request body doesn't match expected schema or validation fails.

```csharp
// Problem: Missing required field
var request = new CreateOrderRequest
{
    // CustomerId missing - required field
    Items = new List<OrderItem>()
};

// Problem: Invalid data type
{
    "orderId": "not-a-number", // Expected int
    "amount": "invalid"        // Expected decimal
}
```

### 3. 404 Not Found - Resource Doesn't Exist
**Likelihood: High**

Requesting a resource that doesn't exist or wrong URL.

```csharp
// Problem: Wrong URL path
await _httpClient.GetAsync("/api/v1/order/123"); // Should be /orders/

// Problem: Resource deleted or never existed
await _httpClient.GetAsync("/api/orders/999999"); // Order doesn't exist
```

### 4. 500 Internal Server Error - Server-Side Exception
**Likelihood: High**

Unhandled exception on the server.

```csharp
// Problem: Server throws unhandled exception
// Check server logs for stack trace
// Common causes:
// - NullReferenceException in controller
// - Database connection failure
// - Configuration missing
```

### 5. Timeout/TaskCanceledException
**Likelihood: Medium-High**

Request takes too long or connection cannot be established.

```csharp
// Problem: Server slow to respond
try
{
    var response = await _httpClient.GetAsync(url);
}
catch (TaskCanceledException ex) when (ex.InnerException is TimeoutException)
{
    // Timeout occurred
}

// Problem: HttpClient disposed or request cancelled
catch (TaskCanceledException ex) when (ex.CancellationToken.IsCancellationRequested)
{
    // Request was cancelled
}
```

### 6. 403 Forbidden - Authorization Failure
**Likelihood: Medium**

Authenticated but not authorized for the resource.

```csharp
// Problem: User doesn't have required role
[Authorize(Roles = "Admin")]
public async Task<IActionResult> DeleteOrder(int id) // User is not Admin

// Problem: Resource belongs to different user
// User 1 trying to access User 2's data
```

### 7. 415 Unsupported Media Type
**Likelihood: Medium**

Wrong Content-Type header for the request.

```csharp
// Problem: Missing or wrong Content-Type
var content = new StringContent(json); // Defaults to text/plain
// Server expects application/json

// Problem: Sending form data as JSON
var content = new FormUrlEncodedContent(data);
_httpClient.DefaultRequestHeaders.Accept.Add(
    new MediaTypeWithQualityHeaderValue("application/json")); // Mismatch
```

### 8. 429 Too Many Requests - Rate Limited
**Likelihood: Medium**

Exceeded API rate limits.

```csharp
// Problem: Too many requests in time window
for (int i = 0; i < 1000; i++)
{
    await _httpClient.GetAsync(url); // Rate limited after N requests
}
```

### 9. Connection Refused/Socket Exception
**Likelihood: Low-Medium**

Cannot establish connection to server.

```csharp
// Problem: Server not running or wrong port
// HttpRequestException: Connection refused
await _httpClient.GetAsync("http://localhost:5000/api/data");

// Problem: Firewall blocking connection
// Problem: DNS resolution failure
```

### 10. SSL/TLS Certificate Errors
**Likelihood: Low**

Certificate validation fails.

```csharp
// Problem: Self-signed or expired certificate
// HttpRequestException: The SSL connection could not be established

// Problem: Certificate hostname mismatch
// Connecting to IP but cert issued for domain name
```

---

## Investigation Steps

### Step 1: Capture Full Response Details
```csharp
var response = await _httpClient.SendAsync(request);

Console.WriteLine($"Status: {response.StatusCode} ({(int)response.StatusCode})");
Console.WriteLine($"Reason: {response.ReasonPhrase}");

foreach (var header in response.Headers)
{
    Console.WriteLine($"{header.Key}: {string.Join(", ", header.Value)}");
}

var body = await response.Content.ReadAsStringAsync();
Console.WriteLine($"Body: {body}");
```

### Step 2: Check Request Being Sent
```csharp
// Log the outgoing request
var request = new HttpRequestMessage(HttpMethod.Post, url);
request.Content = new StringContent(json, Encoding.UTF8, "application/json");

Console.WriteLine($"Method: {request.Method}");
Console.WriteLine($"URL: {request.RequestUri}");
Console.WriteLine($"Headers: {string.Join(", ", request.Headers)}");
Console.WriteLine($"Body: {json}");
```

### Step 3: Use HTTP Logging Handler
```csharp
public class LoggingHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        Console.WriteLine($"Request: {request.Method} {request.RequestUri}");
        foreach (var header in request.Headers)
            Console.WriteLine($"  {header.Key}: {string.Join(", ", header.Value)}");

        var response = await base.SendAsync(request, cancellationToken);

        Console.WriteLine($"Response: {(int)response.StatusCode} {response.ReasonPhrase}");
        return response;
    }
}

// Register
builder.Services.AddHttpClient<IMyService, MyService>()
    .AddHttpMessageHandler<LoggingHandler>();
```

### Step 4: Check Authentication Token
```csharp
// Decode and inspect JWT token
var token = "eyJhbGciOiJIUzI1NiIs...";
var handler = new JwtSecurityTokenHandler();
var jwt = handler.ReadJwtToken(token);

Console.WriteLine($"Issuer: {jwt.Issuer}");
Console.WriteLine($"Audience: {string.Join(", ", jwt.Audiences)}");
Console.WriteLine($"Expires: {jwt.ValidTo}");
Console.WriteLine($"Claims: {string.Join(", ", jwt.Claims.Select(c => $"{c.Type}={c.Value}"))}");
```

### Step 5: Test with curl/Postman
```bash
# Test the same request outside the application
curl -v -X POST "https://api.example.com/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customerId": 123}'
```

### Step 6: Check Server-Side Logs
```
1. Access server logs (Application Insights, Seq, console)
2. Search for the correlation ID or timestamp
3. Look for exception stack traces
4. Check for validation errors in model binding
```

---

## Quick Fixes

### Fix 1: Add/Refresh Authentication Token
```csharp
// Before
var response = await _httpClient.GetAsync(url);

// After - add token
_httpClient.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", await GetAccessTokenAsync());
var response = await _httpClient.GetAsync(url);

// Refresh if expired
if (response.StatusCode == HttpStatusCode.Unauthorized)
{
    var newToken = await RefreshTokenAsync();
    _httpClient.DefaultRequestHeaders.Authorization =
        new AuthenticationHeaderValue("Bearer", newToken);
    response = await _httpClient.GetAsync(url);
}
```

### Fix 2: Set Correct Content-Type
```csharp
// Before - wrong content type
var content = new StringContent(json);

// After - explicit JSON content type
var content = new StringContent(json, Encoding.UTF8, "application/json");

// Or use JsonContent
var content = JsonContent.Create(new { name = "test" });
```

### Fix 3: Handle 404 Gracefully
```csharp
// Before
var response = await _httpClient.GetAsync($"/api/orders/{orderId}");
response.EnsureSuccessStatusCode(); // Throws on 404

// After
var response = await _httpClient.GetAsync($"/api/orders/{orderId}");
if (response.StatusCode == HttpStatusCode.NotFound)
{
    return null; // Or throw domain-specific exception
}
response.EnsureSuccessStatusCode();
```

### Fix 4: Configure Timeouts
```csharp
// Before - default 100 second timeout
var client = new HttpClient();

// After - explicit timeout
var client = new HttpClient
{
    Timeout = TimeSpan.FromSeconds(30)
};

// Per-request timeout using CancellationToken
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
var response = await _httpClient.GetAsync(url, cts.Token);
```

### Fix 5: Implement Retry with Polly
```csharp
builder.Services.AddHttpClient<IMyService, MyService>()
    .AddTransientHttpErrorPolicy(policy => policy
        .WaitAndRetryAsync(3, retryAttempt =>
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt))))
    .AddTransientHttpErrorPolicy(policy => policy
        .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30)));
```

### Fix 6: Handle Rate Limiting
```csharp
var response = await _httpClient.GetAsync(url);

if (response.StatusCode == HttpStatusCode.TooManyRequests)
{
    if (response.Headers.TryGetValues("Retry-After", out var values))
    {
        var retryAfter = int.Parse(values.First());
        await Task.Delay(TimeSpan.FromSeconds(retryAfter));
        response = await _httpClient.GetAsync(url);
    }
}
```

### Fix 7: Accept Self-Signed Certificates (Development Only)
```csharp
// ONLY for development - never in production
var handler = new HttpClientHandler
{
    ServerCertificateCustomValidationCallback =
        HttpClientHandler.DangerousAcceptAnyServerCertificateValidator
};
var client = new HttpClient(handler);
```

---

## Prevention Patterns

### Pattern 1: Typed HttpClient with Configuration
```csharp
public class OrderServiceClient
{
    private readonly HttpClient _httpClient;

    public OrderServiceClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<Order?> GetOrderAsync(int id)
    {
        var response = await _httpClient.GetAsync($"orders/{id}");

        if (response.StatusCode == HttpStatusCode.NotFound)
            return null;

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<Order>();
    }
}

// Registration
builder.Services.AddHttpClient<OrderServiceClient>(client =>
{
    client.BaseAddress = new Uri(configuration["OrderService:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(30);
    client.DefaultRequestHeaders.Add("X-Api-Key", configuration["OrderService:ApiKey"]);
});
```

### Pattern 2: Centralized Error Handling
```csharp
public class ApiException : Exception
{
    public HttpStatusCode StatusCode { get; }
    public string? ResponseBody { get; }

    public ApiException(HttpStatusCode statusCode, string? responseBody, string message)
        : base(message)
    {
        StatusCode = statusCode;
        ResponseBody = responseBody;
    }
}

public static class HttpResponseExtensions
{
    public static async Task EnsureSuccessOrThrowAsync(this HttpResponseMessage response)
    {
        if (!response.IsSuccessStatusCode)
        {
            var body = await response.Content.ReadAsStringAsync();
            throw new ApiException(
                response.StatusCode,
                body,
                $"API request failed with status {(int)response.StatusCode}: {body}");
        }
    }
}
```

### Pattern 3: Token Refresh Handler
```csharp
public class AuthTokenHandler : DelegatingHandler
{
    private readonly ITokenService _tokenService;

    public AuthTokenHandler(ITokenService tokenService)
    {
        _tokenService = tokenService;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var token = await _tokenService.GetAccessTokenAsync();
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        var response = await base.SendAsync(request, cancellationToken);

        if (response.StatusCode == HttpStatusCode.Unauthorized)
        {
            token = await _tokenService.RefreshTokenAsync();
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
            response = await base.SendAsync(request, cancellationToken);
        }

        return response;
    }
}
```

### Pattern 4: Correlation ID Propagation
```csharp
public class CorrelationIdHandler : DelegatingHandler
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var correlationId = _httpContextAccessor.HttpContext?
            .Request.Headers["X-Correlation-ID"].FirstOrDefault()
            ?? Guid.NewGuid().ToString();

        request.Headers.Add("X-Correlation-ID", correlationId);

        return base.SendAsync(request, cancellationToken);
    }
}
```

### Pattern 5: Response Validation
```csharp
public async Task<T> GetAndValidateAsync<T>(string url) where T : class
{
    var response = await _httpClient.GetAsync(url);

    if (!response.IsSuccessStatusCode)
    {
        var error = await response.Content.ReadAsStringAsync();
        _logger.LogError("API call failed: {StatusCode} - {Error}",
            response.StatusCode, error);
        throw new ApiException(response.StatusCode, error);
    }

    var result = await response.Content.ReadFromJsonAsync<T>();

    if (result == null)
    {
        throw new InvalidOperationException($"API returned null for {url}");
    }

    return result;
}
```

### Pattern 6: Health Check for Dependencies
```csharp
public class ExternalApiHealthCheck : IHealthCheck
{
    private readonly HttpClient _httpClient;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken cancellationToken)
    {
        try
        {
            var response = await _httpClient.GetAsync("/health", cancellationToken);

            if (response.IsSuccessStatusCode)
                return HealthCheckResult.Healthy();

            return HealthCheckResult.Degraded($"API returned {response.StatusCode}");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("API unreachable", ex);
        }
    }
}

// Registration
builder.Services.AddHealthChecks()
    .AddCheck<ExternalApiHealthCheck>("external-api");
```

### Pattern 7: Request/Response Logging with Redaction
```csharp
public class SecureLoggingHandler : DelegatingHandler
{
    private readonly ILogger _logger;
    private static readonly string[] SensitiveHeaders = { "Authorization", "X-Api-Key" };

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var requestLog = new
        {
            Method = request.Method.Method,
            Url = request.RequestUri?.ToString(),
            Headers = request.Headers
                .Where(h => !SensitiveHeaders.Contains(h.Key, StringComparer.OrdinalIgnoreCase))
                .ToDictionary(h => h.Key, h => string.Join(", ", h.Value))
        };
        _logger.LogInformation("HTTP Request: {@Request}", requestLog);

        var response = await base.SendAsync(request, cancellationToken);

        _logger.LogInformation("HTTP Response: {StatusCode}", response.StatusCode);

        return response;
    }
}
```
