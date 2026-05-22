# Databricks notebook source
# DBTITLE 1,Step 1: Input CSV Path
# Step 1: Specify the path to the input CSV file directory
# CSV files should be named "Account.csv" or "Sleeve.csv" based on the table being updated.
file_path = "/mnt/EDH/02curated/Delta_Updates/"

# COMMAND ----------

# DBTITLE 1,Step 2: Delta Table Path
# Step 2: Specify the Delta table paths for Account and Sleeve
account_delta_path = "/mnt/EDH/01stage/Billing/Redi2/CurrentView/Account/"
sleeve_delta_path = "/mnt/EDH/01stage/Billing/Redi2/CurrentView/Sleeve/"

# COMMAND ----------

# DBTITLE 1,Step 3: Read CSV File
# Step 3: Detect CSV files and read into DataFrames
# Checks for Account.csv and Sleeve.csv in the input directory
account_df = None
sleeve_df = None

try:
    account_df = spark.read.format("csv").option("header", "true").load(file_path + "Account.csv")
    print("Account.csv found and loaded successfully.")
except Exception:
    print("Account.csv not found. Skipping Account processing.")

try:
    sleeve_df = spark.read.format("csv").option("header", "true").load(file_path + "Sleeve.csv")
    print("Sleeve.csv found and loaded successfully.")
except Exception:
    print("Sleeve.csv not found. Skipping Sleeve processing.")

# COMMAND ----------

# DBTITLE 1,Step 4: Data Transformations (Optional)
# Step 4: Perform any necessary data transformations or cleaning (optional)
# For example, you could cast columns, filter rows, or handle missing values here
# account_df = account_df.withColumn("column_name", account_df["column_name"].cast("desired_type"))
# sleeve_df = sleeve_df.withColumn("column_name", sleeve_df["column_name"].cast("desired_type"))

# COMMAND ----------

# DBTITLE 1,Step 5: Apply Account Delta Updates (Update, Insert, Delete)
from delta.tables import DeltaTable
from pyspark.sql.functions import col

# =============================================
# Part 1: Apply Delta Updates for Account
# =============================================
if account_df is not None:
    account_delta = DeltaTable.forPath(spark, account_delta_path)

    # Separate rows based on Operation column and drop it before writing
    update_df = account_df.filter(account_df.Operation == "Update").drop("Operation")
    insert_df = account_df.filter(account_df.Operation == "Insert").drop("Operation")
    delete_df = account_df.filter(account_df.Operation == "Delete")

    # Cast columns to match Delta schema (CSV reads everything as string)
    # Fetch existing CreatedDate for each ExternalAccountIdentifier from account_delta
    existing_dates = account_delta.toDF().select("ExternalAccountIdentifier", "CreatedDate").distinct()

    # Join update_df with existing_dates to retain CreatedDate and set ModifiedDate to current timestamp
    from pyspark.sql.functions import current_timestamp

    update_df = update_df.drop("CreatedDate").join(
        existing_dates,
        on="ExternalAccountIdentifier",
        how="left"
    ).withColumn("CreatedDate", col("CreatedDate")) \
     .withColumn("ModifiedDate", current_timestamp())

    # Update existing records using merge on Delta format files
    account_delta.alias("target").merge(
        update_df.alias("source"),
        "target.ExternalAccountIdentifier = source.ExternalAccountIdentifier"
    ).whenMatchedUpdateAll().execute()

    # Insert new records using DataFrame append (not SQL INSERT, since this is Delta format, not a table)
    from pyspark.sql.functions import current_timestamp

    insert_df = insert_df.withColumn("CreatedDate", current_timestamp()) \
                         .withColumn("ModifiedDate", current_timestamp())

    insert_df.write.format("delta").mode("append").save(account_delta_path)

    # Delete records
    for row in delete_df.select("ExternalAccountIdentifier").distinct().collect():
        account_delta.delete(f"ExternalAccountIdentifier = '{row.ExternalAccountIdentifier}'")

    print("Account Delta updates applied successfully.")
else:
    print("No Account.csv to process. Skipping Part 1.")

# COMMAND ----------

# DBTITLE 1,Step 6: Apply Sleeve Delta Updates (Update, Insert, Delete)
from delta.tables import DeltaTable
from pyspark.sql.functions import col, current_timestamp

# =============================================
# Part 2: Apply Delta Updates for Sleeve
# =============================================
if sleeve_df is not None:
    sleeve_delta = DeltaTable.forPath(spark, sleeve_delta_path)

    # Separate rows based on operation_type column and drop it before writing
    update_df = sleeve_df.filter(sleeve_df.Operation == "Update").drop("Operation")
    insert_df = sleeve_df.filter(sleeve_df.Operation == "Insert").drop("Operation")
    delete_df = sleeve_df.filter(sleeve_df.Operation == "Delete")

    # Cast columns to match Delta schema (CSV reads everything as string)
    # Fetch existing CreatedDate for each ExternalSleeveIdentifier from sleeve_delta
    existing_dates = sleeve_delta.toDF().select("ExternalSleeveIdentifier", "CreatedDate").distinct()

    # Join update_df with existing_dates to retain CreatedDate and set ModifiedDate to current timestamp
    update_df = update_df.drop("CreatedDate").join(
        existing_dates,
        on="ExternalSleeveIdentifier",
        how="left"
    ).withColumn("CreatedDate", col("CreatedDate")) \
     .withColumn("ModifiedDate", current_timestamp())

    # Update existing records using merge on Delta format files
    sleeve_delta.alias("target").merge(
        update_df.alias("source"),
        "target.ExternalSleeveIdentifier = source.ExternalSleeveIdentifier"
    ).whenMatchedUpdateAll().execute()

    # Insert new records using DataFrame append (not SQL INSERT, since this is Delta format, not a table)
    insert_df = insert_df.withColumn("CreatedDate", current_timestamp()) \
                         .withColumn("ModifiedDate", current_timestamp())

    insert_df.write.format("delta").mode("append").save(sleeve_delta_path)

    # Delete records
    for row in delete_df.select("ExternalSleeveIdentifier").distinct().collect():
        sleeve_delta.delete(f"ExternalSleeveIdentifier = '{row.ExternalSleeveIdentifier}'")

    print("Sleeve Delta updates applied successfully.")
else:
    print("No Sleeve.csv to process. Skipping Part 2.")

# COMMAND ----------

# DBTITLE 1,Step 7: Archieving CSV Files after updates
# Step 7: Archive the processed CSV files after conversion
from datetime import datetime

archive_base_path = file_path + "archive/"
current_date = datetime.now().strftime("%Y-%m-%d")
archive_date_path = f"{archive_base_path}{current_date}/"

def get_next_archive_subfolder(base_path, filename):
    i = 1
    while True:
        subfolder = f"{base_path}{i}/"
        dbutils.fs.mkdirs(subfolder)
        file_exists = any(f.name == filename for f in dbutils.fs.ls(subfolder))
        if not file_exists:
            return subfolder
        i += 1

# Archive Account.csv if it was processed
if account_df is not None:
    final_archive = get_next_archive_subfolder(archive_date_path, "Account.csv")
    dbutils.fs.mv(file_path + "Account.csv", final_archive + "Account.csv")
    print(f"Account.csv archived to: {final_archive}")

# Archive Sleeve.csv if it was processed
if sleeve_df is not None:
    final_archive = get_next_archive_subfolder(archive_date_path, "Sleeve.csv")
    dbutils.fs.mv(file_path + "Sleeve.csv", final_archive + "Sleeve.csv")
    print(f"Sleeve.csv archived to: {final_archive}")