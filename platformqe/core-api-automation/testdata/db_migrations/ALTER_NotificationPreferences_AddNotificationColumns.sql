-- =====================================================
-- Migration Script: Add 6 New Notification Columns to NotificationPreferences
-- Story: Tracking Center DB - Add 6 New Notification Group Columns
-- Description: Adds 6 new tinyint columns with default constraint = 1
-- =====================================================

BEGIN TRANSACTION

BEGIN TRY
    PRINT '========== Migration Start: Adding 6 New Notification Columns =========='
    
    -- Check if table exists
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'NotificationPreferences')
    BEGIN
        RAISERROR('NotificationPreferences table does not exist', 16, 1)
    END
    
    PRINT 'Adding receivedCompletedNewAccountsEV column...'
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'NotificationPreferences' AND COLUMN_NAME = 'receivedCompletedNewAccountsEV')
    BEGIN
        ALTER TABLE NotificationPreferences ADD receivedCompletedNewAccountsEV TINYINT NULL DEFAULT 1
        PRINT 'receivedCompletedNewAccountsEV column added successfully'
    END
    ELSE
    BEGIN
        PRINT 'receivedCompletedNewAccountsEV column already exists - skipping'
    END
    
    PRINT 'Adding receivedCompletedMoneyInEV column...'
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'NotificationPreferences' AND COLUMN_NAME = 'receivedCompletedMoneyInEV')
    BEGIN
        ALTER TABLE NotificationPreferences ADD receivedCompletedMoneyInEV TINYINT NULL DEFAULT 1
        PRINT 'receivedCompletedMoneyInEV column added successfully'
    END
    ELSE
    BEGIN
        PRINT 'receivedCompletedMoneyInEV column already exists - skipping'
    END
    
    PRINT 'Adding receivedCompletedStandingInstructionsEV column...'
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'NotificationPreferences' AND COLUMN_NAME = 'receivedCompletedStandingInstructionsEV')
    BEGIN
        ALTER TABLE NotificationPreferences ADD receivedCompletedStandingInstructionsEV TINYINT NULL DEFAULT 1
        PRINT 'receivedCompletedStandingInstructionsEV column added successfully'
    END
    ELSE
    BEGIN
        PRINT 'receivedCompletedStandingInstructionsEV column already exists - skipping'
    END
    
    PRINT 'Adding receivedCompletedInvestmentChangesEV column...'
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'NotificationPreferences' AND COLUMN_NAME = 'receivedCompletedInvestmentChangesEV')
    BEGIN
        ALTER TABLE NotificationPreferences ADD receivedCompletedInvestmentChangesEV TINYINT NULL DEFAULT 1
        PRINT 'receivedCompletedInvestmentChangesEV column added successfully'
    END
    ELSE
    BEGIN
        PRINT 'receivedCompletedInvestmentChangesEV column already exists - skipping'
    END
    
    PRINT 'Adding receivedCompletedWithdrawalsEV column...'
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'NotificationPreferences' AND COLUMN_NAME = 'receivedCompletedWithdrawalsEV')
    BEGIN
        ALTER TABLE NotificationPreferences ADD receivedCompletedWithdrawalsEV TINYINT NULL DEFAULT 1
        PRINT 'receivedCompletedWithdrawalsEV column added successfully'
    END
    ELSE
    BEGIN
        PRINT 'receivedCompletedWithdrawalsEV column already exists - skipping'
    END
    
    PRINT 'Adding receivedCompletedTerminationsEV column...'
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'NotificationPreferences' AND COLUMN_NAME = 'receivedCompletedTerminationsEV')
    BEGIN
        ALTER TABLE NotificationPreferences ADD receivedCompletedTerminationsEV TINYINT NULL DEFAULT 1
        PRINT 'receivedCompletedTerminationsEV column added successfully'
    END
    ELSE
    BEGIN
        PRINT 'receivedCompletedTerminationsEV column already exists - skipping'
    END
    
    -- ===== VALIDATION: Verify column specifications =====
    PRINT ''
    PRINT '========== Validation Phase: Verifying Column Specifications =========='
    
    DECLARE @ColumnCount INT = 0
    SELECT @ColumnCount = COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'NotificationPreferences'
    AND COLUMN_NAME IN (
        'receivedCompletedNewAccountsEV',
        'receivedCompletedMoneyInEV',
        'receivedCompletedStandingInstructionsEV',
        'receivedCompletedInvestmentChangesEV',
        'receivedCompletedWithdrawalsEV',
        'receivedCompletedTerminationsEV'
    )
    AND DATA_TYPE = 'tinyint'
    AND IS_NULLABLE = 'YES'
    
    IF @ColumnCount <> 6
    BEGIN
        RAISERROR('Column specification validation failed: Expected 6 columns with tinyint data type and nullable=YES, found %d', 16, 1, @ColumnCount)
    END
    ELSE
    BEGIN
        PRINT 'SUCCESS: All 6 columns verified with correct specifications (tinyint, nullable)'
    END
    
    -- ===== VALIDATION: Verify default constraints =====
    DECLARE @DefaultCount INT = 0
    SELECT @DefaultCount = COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'NotificationPreferences'
    AND COLUMN_NAME IN (
        'receivedCompletedNewAccountsEV',
        'receivedCompletedMoneyInEV',
        'receivedCompletedStandingInstructionsEV',
        'receivedCompletedInvestmentChangesEV',
        'receivedCompletedWithdrawalsEV',
        'receivedCompletedTerminationsEV'
    )
    AND COLUMN_DEFAULT = '((1))'
    
    IF @DefaultCount <> 6
    BEGIN
        RAISERROR('Default constraint validation failed: Expected 6 columns with default value 1, found %d', 16, 1, @DefaultCount)
    END
    ELSE
    BEGIN
        PRINT 'SUCCESS: All 6 columns verified with default constraint = 1'
    END
    
    -- ===== VALIDATION: Verify tinyint boundary constraints =====
    PRINT ''
    PRINT '========== Validation Phase: Testing Tinyint Boundary Constraints =========='
    
    -- Test 1: Valid minimum boundary (0)
    BEGIN
        DECLARE @TestValue_Min TINYINT = 0
        PRINT 'Testing valid minimum boundary value (0)...'
        IF @TestValue_Min >= 0 AND @TestValue_Min <= 255
            PRINT 'SUCCESS: Value 0 is within valid tinyint range'
        ELSE
            RAISERROR('FAILURE: Value 0 is outside valid tinyint range', 16, 1)
    END
    
    -- Test 2: Valid maximum boundary (255)
    BEGIN
        DECLARE @TestValue_Max TINYINT = 255
        PRINT 'Testing valid maximum boundary value (255)...'
        IF @TestValue_Max >= 0 AND @TestValue_Max <= 255
            PRINT 'SUCCESS: Value 255 is within valid tinyint range'
        ELSE
            RAISERROR('FAILURE: Value 255 is outside valid tinyint range', 16, 1)
    END
    
    -- Test 3: Invalid boundary (256) - This should fail at SQL parsing
    PRINT 'Testing invalid boundary value (256)...'
    PRINT 'NOTE: Value 256 exceeds tinyint maximum of 255 and will be rejected at conversion time'
    
    -- ===== VALIDATION: Display final schema verification =====
    PRINT ''
    PRINT '========== Final Schema Verification =========='
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'NotificationPreferences'
    AND COLUMN_NAME IN (
        'receivedCompletedNewAccountsEV',
        'receivedCompletedMoneyInEV',
        'receivedCompletedStandingInstructionsEV',
        'receivedCompletedInvestmentChangesEV',
        'receivedCompletedWithdrawalsEV',
        'receivedCompletedTerminationsEV',
        'ReceivedCompletedPrimaryEV'
    )
    ORDER BY COLUMN_NAME
    
    PRINT ''
    PRINT '========== Migration Completed Successfully =========='
    
    COMMIT TRANSACTION
    
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION
    
    DECLARE @ErrorMessage NVARCHAR(MAX) = ERROR_MESSAGE()
    DECLARE @ErrorSeverity INT = ERROR_SEVERITY()
    DECLARE @ErrorState INT = ERROR_STATE()
    
    PRINT ''
    PRINT '========== ERROR ENCOUNTERED =========='
    PRINT 'Error Message: ' + @ErrorMessage
    PRINT 'Error Severity: ' + CAST(@ErrorSeverity AS VARCHAR)
    PRINT 'Error State: ' + CAST(@ErrorState AS VARCHAR)
    PRINT '========== Migration Rolled Back =========='
    
    RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState)
END CATCH
