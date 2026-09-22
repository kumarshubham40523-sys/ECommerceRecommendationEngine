import os
import sys

# Use the project's virtual environment
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg


# --------------------------------------------------
# 1. Start Spark
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("ECommerceDataProcessing")
    .master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n🔥 Spark started!")
print("Spark version:", spark.version)


# --------------------------------------------------
# 2. Load interaction data
# --------------------------------------------------

interaction_path = "data/ecommerce_interactions.csv"

interactions = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(interaction_path)
)

print("\n📥 Raw Interaction Data:")
interactions.show(10)


# --------------------------------------------------
# 3. Display schema
# --------------------------------------------------

print("\n📋 Dataset Schema:")
interactions.printSchema()


# --------------------------------------------------
# 4. Count records
# --------------------------------------------------

total_records = interactions.count()

print(f"\n📊 Total interactions: {total_records}")


# --------------------------------------------------
# 5. Check missing values
# --------------------------------------------------

print("\n🔍 Missing Values:")

for column_name in interactions.columns:

    missing_count = (
        interactions
        .filter(col(column_name).isNull())
        .count()
    )

    print(f"{column_name}: {missing_count}")


# --------------------------------------------------
# 6. Count different event types
# --------------------------------------------------

print("\n🛒 Event Type Distribution:")

event_distribution = (
    interactions
    .groupBy("event_type")
    .agg(count("*").alias("interaction_count"))
    .orderBy(col("interaction_count").desc())
)

event_distribution.show()


# --------------------------------------------------
# 7. Calculate average rating
# --------------------------------------------------

print("\n⭐ Average Review Rating:")

average_rating = (
    interactions
    .filter(col("rating") > 0)
    .agg(avg("rating").alias("average_rating"))
)

average_rating.show()


# --------------------------------------------------
# 8. Most interacted products
# --------------------------------------------------

print("\n🏆 Top 10 Most Interacted Products:")

top_products = (
    interactions
    .groupBy("product_id")
    .agg(count("*").alias("interaction_count"))
    .orderBy(col("interaction_count").desc())
    .limit(10)
)

top_products.show()


# --------------------------------------------------
# 9. Most active users
# --------------------------------------------------

print("\n👤 Top 10 Most Active Users:")

top_users = (
    interactions
    .groupBy("user_id")
    .agg(count("*").alias("interaction_count"))
    .orderBy(col("interaction_count").desc())
    .limit(10)
)

top_users.show()


# --------------------------------------------------
# 10. Stop Spark
# --------------------------------------------------

spark.stop()

print("\n✅ PySpark data processing completed!")