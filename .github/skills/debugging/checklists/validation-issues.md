# Validation Issues

Investigation checklist for FluentValidation and ModelState errors.

## Symptoms

- `ValidationException` thrown unexpectedly
- ModelState.IsValid is false
- Validation not running at all
- Wrong validation rules applied
- Validation passing when it shouldn't

## Quick Checks

1. **Is the validator registered?**
   - Check for `AddFluentValidation()` or `AddValidatorsFromAssembly()`

2. **Is automatic validation enabled?**
   - ASP.NET Core doesn't auto-validate by default

3. **Are the right validators being used?**
   - Check inheritance and assembly scanning

4. **Is the validation scope correct?**
   - Some rules only run on certain operations

## Root Cause Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| Validation not running | Validator not registered | Register via DI |
| Wrong rules applied | Multiple validators for same type | Check registration order |
| Null reference in rule | Property null during validation | Add null check or NotNull first |
| Async rules not running | Using Validate instead of ValidateAsync | Use `ValidateAsync()` |
| ModelState shows errors | Auto-validation from DataAnnotations | Disable DataAnnotations or handle both |

## FluentValidation Issues

### Validator Not Registered

```csharp
// 🔴 Validator not registered
public class CreateOrderValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderValidator()
    {
        RuleFor(x => x.CustomerId).NotEmpty();
    }
}

// ✅ Register validators
services.AddValidatorsFromAssemblyContaining<CreateOrderValidator>();

// Or manually
services.AddScoped<IValidator<CreateOrderCommand>, CreateOrderValidator>();
```

### Validation Not Running Automatically

```csharp
// FluentValidation doesn't auto-validate in ASP.NET Core by default
// You need to explicitly validate

// Option 1: Manual validation in handler
public class CreateOrderHandler
{
    private readonly IValidator<CreateOrderCommand> _validator;

    public async Task<Result> Handle(CreateOrderCommand command)
    {
        var result = await _validator.ValidateAsync(command);
        if (!result.IsValid)
            return Result.Failure(result.Errors);
    }
}

// Option 2: MediatR pipeline behavior
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public async Task<TResponse> Handle(TRequest request, ...)
    {
        var failures = await ValidateAll(request);
        if (failures.Any())
            throw new ValidationException(failures);
    }
}
```

### Null Reference in Rules

```csharp
// 🔴 Will throw if Customer is null
RuleFor(x => x.Customer.Name).NotEmpty();

// ✅ Check parent first
RuleFor(x => x.Customer).NotNull();
RuleFor(x => x.Customer.Name).NotEmpty()
    .When(x => x.Customer != null);

// Or use cascade
RuleFor(x => x.Customer).NotNull()
    .DependentRules(() =>
    {
        RuleFor(x => x.Customer.Name).NotEmpty();
    });
```

### Async Rules Not Executing

```csharp
// 🔴 Async rule in sync validation
RuleFor(x => x.Email)
    .MustAsync(async (email, ct) => await IsUniqueEmail(email));

// Called with Validate() - async rule skipped!
validator.Validate(command);

// ✅ Use ValidateAsync
await validator.ValidateAsync(command);
```

### Conditional Validation

```csharp
// Only validate when condition is met
RuleFor(x => x.ShippingAddress)
    .NotEmpty()
    .When(x => x.RequiresShipping);

// Different rules for different scenarios
RuleSet("Create", () =>
{
    RuleFor(x => x.Id).Empty();
});

RuleSet("Update", () =>
{
    RuleFor(x => x.Id).NotEmpty();
});

// Execute specific rule set
validator.Validate(command, options => options.IncludeRuleSets("Create"));
```

## ModelState Issues

### Mixing DataAnnotations and FluentValidation

```csharp
// 🔴 Both run, causing duplicate errors
public class CreateOrderCommand
{
    [Required]  // DataAnnotations
    public string Name { get; set; }
}

public class CreateOrderValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderValidator()
    {
        RuleFor(x => x.Name).NotEmpty();  // FluentValidation
    }
}

// ✅ Disable automatic DataAnnotations validation
services.Configure<ApiBehaviorOptions>(options =>
{
    options.SuppressModelStateInvalidFilter = true;
});
```

### ModelState Not Being Checked

```csharp
// 🔴 Not checking ModelState
[HttpPost]
public IActionResult Create(CreateOrderCommand command)
{
    // ModelState.IsValid not checked!
    _service.Create(command);
}

// ✅ Check ModelState
[HttpPost]
public IActionResult Create(CreateOrderCommand command)
{
    if (!ModelState.IsValid)
        return BadRequest(ModelState);

    _service.Create(command);
}
```

## Debugging Steps

1. **Check validator registration:**
   ```csharp
   var validator = serviceProvider.GetService<IValidator<CreateOrderCommand>>();
   Console.WriteLine($"Validator: {validator?.GetType().Name ?? "NOT REGISTERED"}");
   ```

2. **Inspect validation result:**
   ```csharp
   var result = await validator.ValidateAsync(command);
   foreach (var error in result.Errors)
   {
       Console.WriteLine($"{error.PropertyName}: {error.ErrorMessage}");
   }
   ```

3. **Log failed rules:**
   ```csharp
   foreach (var error in result.Errors)
   {
       _logger.LogWarning("Validation failed: {Property} - {Error} (Severity: {Severity})",
           error.PropertyName, error.ErrorMessage, error.Severity);
   }
   ```

## Common Validator Patterns

### Reusable Property Validators

```csharp
public static class CustomValidators
{
    public static IRuleBuilderOptions<T, string> ValidEmail<T>(
        this IRuleBuilder<T, string> ruleBuilder)
    {
        return ruleBuilder
            .NotEmpty()
            .EmailAddress()
            .MaximumLength(255);
    }
}

// Usage
RuleFor(x => x.Email).ValidEmail();
```

### Child Validator

```csharp
public class OrderValidator : AbstractValidator<Order>
{
    public OrderValidator()
    {
        RuleFor(x => x.Customer).SetValidator(new CustomerValidator());
        RuleForEach(x => x.Items).SetValidator(new OrderItemValidator());
    }
}
```

## Prevention

- Always use `ValidateAsync` for validators with async rules
- Register validators via assembly scanning
- Add validation pipeline behavior for MediatR
- Test validation rules in unit tests
- Use consistent approach (DataAnnotations OR FluentValidation, not both)
