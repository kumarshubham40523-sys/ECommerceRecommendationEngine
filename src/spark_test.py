import os
import sys

# Tell Spark to use the Python inside our virtual environment
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Force Spark to use the local machine
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

from pyspark.sql import SparkSession


spark = (
    SparkSession.builder
    .appName("ECommerceRecommendationEngine")
    .master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

print("\n🔥 Spark started successfully!")
print("Spark version:", spark.version)
print("Python executable:", sys.executable)


data = [
    (1, 101, 5),
    (1, 102, 4),
    (2, 101, 3),
    (2, 103, 5),
    (3, 102, 5),
]

columns = ["user_id", "product_id", "rating"]

df = spark.createDataFrame(data, columns)

print("\n📊 E-Commerce Interaction Data:")
df.show()

spark.stop()

print("\n✅ Spark test completed!")