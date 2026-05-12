# EF Core Migration Issues

Investigation checklist for Entity Framework Core migration and schema errors.

## Symptoms

- `SqlException: Invalid object name 'TableName'`
- `SqlException: Invalid column name 'ColumnName'`
- `DbUpdateException` during save
- Migration not applying
- Model and database out of sync
- `PendingModelChangesWarning`

## Quick Checks

1. **Are migrations up to date?**
   - Run `dotnet ef migrations list`
   - Check for pending migrations

2. **Is the connection string correct?**
   - Verify targeting correct database
   - Check environment-specific settings

3. **Does the migration match the model?**
   - Compare migration snapshot with DbContext

4. **Was a migration accidentally deleted?**
   - Check `__EFMigrationsHistory` table

## Root Cause Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| Invalid object name | Table doesn't exist | Apply pending migrations |
| Invalid column name | Column missing/renamed | Add migration for model changes |
| Pending changes warning | Model changed, no migration | `dotnet ef migrations add` |
| Migration already applied | Manual DB changes | Sync or reset migrations |
| Timeout during migration | Long-running data migration | Increase timeout, batch operations |

## Migration Commands

```bash
# List migrations
dotnet ef migrations list

# Add new migration
dotnet ef migrations add <MigrationName>

# Apply migrations
dotnet ef database update

# Remove last migration (if not applied)
dotnet ef migrations remove

# Generate SQL script
dotnet ef migrations script

# Revert to specific migration
dotnet ef database update <TargetMigration>
```

## Common Mistakes

### Model Changed Without Migration

```csharp
// 🔴 Added property but no migration
public class Order
{
    public int Id { get; set; }
    public string Notes { get; set; }  // New property, no migration
}

// ✅ Add migration after model change
// dotnet ef migrations add AddNotesToOrder
```

### Incorrect Migration Order

```
Migrations/
├── 20240101_Initial.cs
├── 20240102_AddOrders.cs
├── 20240103_AddProducts.cs  // 🔴 References Orders but applied before?
```

Check `__EFMigrationsHistory` for actual application order.

### Snapshot Out of Sync

```csharp
// ModelSnapshot.cs may be stale
// 🔴 Manual edits to migrations can cause this

// ✅ Regenerate snapshot if needed
// Remove last migration and re-add
```

### Connection String Mismatch

```csharp
// 🔴 Development migration applied to wrong database
// appsettings.Development.json → DevDb
// appsettings.Production.json → ProdDb

// ✅ Verify environment before running migrations
Console.WriteLine($"Database: {context.Database.GetConnectionString()}");
```

## Schema Drift Issues

### Detecting Drift

```csharp
// Check for pending model changes
var pendingMigrations = context.Database.GetPendingMigrations();
var appliedMigrations = context.Database.GetAppliedMigrations();

// Compare model with database
// This requires SQL comparison tools or manual inspection
```

### Manual Database Changes

```sql
-- 🔴 Someone ran this directly on the database
ALTER TABLE Orders ADD Notes NVARCHAR(500);

-- ✅ Now EF doesn't know about it
-- Option 1: Add empty migration to sync
-- Option 2: Generate script, compare, update model
```

### Resolving Drift

```bash
# Generate script from current state
dotnet ef migrations script --idempotent

# Compare with actual database schema
# Use SQL Server Management Studio or Azure Data Studio

# Add "empty" migration to align snapshot
dotnet ef migrations add SyncWithDatabase --no-build
# Then edit the migration to be empty (Up/Down methods empty)
```

## Data Migration Issues

### Large Data Migrations

```csharp
// 🔴 Will timeout on large tables
migrationBuilder.Sql("UPDATE Orders SET Status = 'Active'");

// ✅ Batch the operation
migrationBuilder.Sql(@"
    WHILE EXISTS (SELECT 1 FROM Orders WHERE Status IS NULL)
    BEGIN
        UPDATE TOP (10000) Orders SET Status = 'Active' WHERE Status IS NULL;
    END
");
```

### Data Loss Prevention

```csharp
// 🔴 Dropping column loses data
migrationBuilder.DropColumn(name: "LegacyCode", table: "Products");

// ✅ Migrate data first
migrationBuilder.Sql(@"
    UPDATE Products SET NewCode = LegacyCode WHERE NewCode IS NULL;
");
migrationBuilder.DropColumn(name: "LegacyCode", table: "Products");
```

## Debugging Steps

1. **Check migration status:**
   ```bash
   dotnet ef migrations list --context AppDbContext
   ```

2. **Check database history:**
   ```sql
   SELECT * FROM __EFMigrationsHistory ORDER BY MigrationId;
   ```

3. **Compare schemas:**
   ```bash
   # Generate script of what EF expects
   dotnet ef migrations script --idempotent -o expected.sql

   # Compare with actual database schema
   ```

4. **Verify model configuration:**
   ```csharp
   var entityType = context.Model.FindEntityType(typeof(Order));
   foreach (var property in entityType.GetProperties())
   {
       Console.WriteLine($"{property.Name}: {property.GetColumnType()}");
   }
   ```

## Multiple DbContext Issues

```csharp
// 🔴 Wrong context specified
dotnet ef migrations add Test  // Which context?

// ✅ Specify context explicitly
dotnet ef migrations add Test --context OrderDbContext
dotnet ef database update --context OrderDbContext
```

## CI/CD Migration Strategies

### Safe Deployment Pattern

```csharp
// In Program.cs or startup
if (app.Environment.IsDevelopment())
{
    // Auto-migrate only in dev
    using var scope = app.Services.CreateScope();
    var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    context.Database.Migrate();
}
else
{
    // Production: Run migrations separately
    // via deployment script or admin endpoint
}
```

### Migration Script for CI/CD

```bash
# Generate idempotent script for deployment
dotnet ef migrations script --idempotent --output migrations.sql

# Apply via sqlcmd or Azure DevOps task
sqlcmd -S server -d database -i migrations.sql
```

## Prevention

- Always add migrations when changing models
- Review migration code before applying
- Test migrations on a copy of production data
- Use idempotent scripts for deployments
- Never manually edit `__EFMigrationsHistory`
- Keep migrations small and focused
- Document data migrations in commit messages
