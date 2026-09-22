import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, sum as spark_sum


spark = (
    SparkSession.builder
    .appName("PrepareALSData")
    .master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n🔥 Spark started!")


# Load raw interaction data
interactions = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/ecommerce_interactions.csv")
)

print("\n📥 Raw interaction data:")
interactions.show(5)


# Assign weights based on user behavior
weighted_data = interactions.withColumn(
    "interaction_score",
    when(col("event_type") == "view", 1)
    .when(col("event_type") == "click", 2)
    .when(col("event_type") == "cart", 3)
    .when(col("event_type") == "purchase", 5)
    .when(col("event_type") == "review", 5)
    .otherwise(0)
)


print("\n⚖️ Weighted interactions:")
weighted_data.select(
    "user_id",
    "product_id",
    "event_type",
    "interaction_score"
).show(10)


# Aggregate multiple interactions between
# the same user and product
als_data = (
    weighted_data
    .groupBy("user_id", "product_id")
    .agg(
        spark_sum("interaction_score").alias("rating")
    )
)


print("\n🤖 ALS-ready interaction data:")
als_data.show(10)


# Count final user-product interactions
print(
    "\n📊 Total user-product pairs:",
    als_data.count()
)


# Save the processed data
output_path = "outputs/als_data"

(
    als_data
    .coalesce(1)
    .write
    .mode("overwrite")
    .option("header", True)
    .csv(output_path)
)


print(f"\n💾 ALS data saved to: {output_path}")


spark.stop()

print("\n✅ ALS data preparation completed!")