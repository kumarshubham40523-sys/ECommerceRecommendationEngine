import os
import sys
import csv

# --------------------------------------------------
# Spark / Python configuration
# --------------------------------------------------

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    sum as spark_sum,
    explode,
    collect_set,
    size,
    array_intersect,
    avg,
    lit,
    row_number
)
from pyspark.sql.window import Window
from pyspark.ml.recommendation import ALS


# --------------------------------------------------
# 1. Start Spark
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("ECommerceRecommendationEngine")
    .master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n🔥 Spark started!")
print("Spark version:", spark.version)


# --------------------------------------------------
# 2. Load ORIGINAL interaction data
# --------------------------------------------------

interactions = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/ecommerce_interactions.csv")
)

print("\n📥 Raw interaction data:")
interactions.show(5)


# --------------------------------------------------
# 3. Convert events into interaction scores
# --------------------------------------------------

weighted_data = interactions.withColumn(
    "interaction_score",
    when(col("event_type") == "view", 1)
    .when(col("event_type") == "click", 2)
    .when(col("event_type") == "cart", 3)
    .when(col("event_type") == "purchase", 5)
    .when(col("event_type") == "review", 5)
    .otherwise(0)
)


# --------------------------------------------------
# 4. Aggregate user-product interactions
# --------------------------------------------------

als_data = (
    weighted_data
    .groupBy("user_id", "product_id")
    .agg(
        spark_sum("interaction_score").alias("rating")
    )
)


# --------------------------------------------------
# 5. Set correct data types
# --------------------------------------------------

als_data = (
    als_data
    .withColumn("user_id", col("user_id").cast("integer"))
    .withColumn("product_id", col("product_id").cast("integer"))
    .withColumn("rating", col("rating").cast("float"))
)


print("\n🤖 ALS-ready data:")
als_data.show(10)

print(
    "\n📊 Total user-product pairs:",
    als_data.count()
)


# --------------------------------------------------
# 6. Split into training and testing data
# --------------------------------------------------

training_data, testing_data = als_data.randomSplit(
    [0.8, 0.2],
    seed=42
)

print("\n📚 Training records:", training_data.count())
print("🧪 Testing records:", testing_data.count())


# --------------------------------------------------
# 7. Create ALS model
# --------------------------------------------------

als = ALS(
    userCol="user_id",
    itemCol="product_id",
    ratingCol="rating",
    rank=10,
    maxIter=10,
    regParam=0.1,
    implicitPrefs=True,
    coldStartStrategy="drop",
    seed=42
)


# --------------------------------------------------
# 8. Train model
# --------------------------------------------------

print("\n🤖 Training ALS recommendation model...")

model = als.fit(training_data)

print("✅ ALS model training completed!")


# --------------------------------------------------
# 9. Generate top 5 recommendations
# --------------------------------------------------

recommendations = model.recommendForAllUsers(5)

print("\n🎯 Top 5 recommendations for sample users:")

recommendations.show(10, truncate=False)


# --------------------------------------------------
# 10. Flatten recommendations
# --------------------------------------------------

flat_recommendations = (
    recommendations
    .select(
        col("user_id"),
        explode("recommendations").alias("recommendation")
    )
    .select(
        col("user_id"),
        col("recommendation.product_id").alias("product_id"),
        col("recommendation.rating").alias("recommendation_score")
    )
)


print("\n📌 Flattened recommendations:")

flat_recommendations.show(20)


# --------------------------------------------------
# 11. Load product information
# --------------------------------------------------

products = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/products.csv")
)


# --------------------------------------------------
# 12. Attach product information
# --------------------------------------------------

final_recommendations = (
    flat_recommendations
    .join(
        products,
        on="product_id",
        how="left"
    )
    .select(
        "user_id",
        "product_id",
        "product_name",
        "category",
        "recommendation_score"
    )
    .orderBy(
        "user_id",
        col("recommendation_score").desc()
    )
)


print("\n🛍️ Final product recommendations:")

final_recommendations.show(25, truncate=False)


# --------------------------------------------------
# 13. Save recommendation results
# --------------------------------------------------

output_file = "outputs/recommendations.csv"

rows = final_recommendations.collect()

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "user_id",
        "product_id",
        "product_name",
        "category",
        "recommendation_score"
    ])

    for row in rows:
        writer.writerow([
            row["user_id"],
            row["product_id"],
            row["product_name"],
            row["category"],
            row["recommendation_score"]
        ])

print(f"\n💾 Recommendations saved to {output_file}")


# ==================================================
# 14. MODEL EVALUATION
# ==================================================

print("\n📊 Evaluating ALS Recommendation Model...")


# --------------------------------------------------
# 14.1 Actual products from testing data
# --------------------------------------------------

actual_items = (
    testing_data
    .filter(col("rating") > 0)
    .groupBy("user_id")
    .agg(
        collect_set("product_id").alias("actual_items")
    )
)


# --------------------------------------------------
# 14.2 Generate more candidates
# --------------------------------------------------

all_recommendations = (
    model
    .recommendForAllUsers(20)
    .select(
        "user_id",
        "recommendations"
    )
)


# --------------------------------------------------
# 14.3 Explode recommendation structures
# --------------------------------------------------

candidate_recommendations = (
    all_recommendations
    .select(
        "user_id",
        explode("recommendations").alias("recommendation")
    )
    .select(
        "user_id",
        col("recommendation.product_id").alias("product_id"),
        col("recommendation.rating").alias("score")
    )
)


# --------------------------------------------------
# 14.4 Find products already seen during training
# --------------------------------------------------

seen_items = (
    training_data
    .select(
        "user_id",
        "product_id"
    )
    .distinct()
)


# --------------------------------------------------
# 14.5 Remove already-seen products
# --------------------------------------------------

unseen_recommendations = (
    candidate_recommendations
    .join(
        seen_items,
        ["user_id", "product_id"],
        "left_anti"
    )
)


# --------------------------------------------------
# 14.6 Rank unseen products by ALS score
# --------------------------------------------------

ranking_window = Window.partitionBy(
    "user_id"
).orderBy(
    col("score").desc()
)


predicted_items = (
    unseen_recommendations
    .withColumn(
        "rank",
        row_number().over(ranking_window)
    )
    .filter(
        col("rank") <= 5
    )
    .groupBy("user_id")
    .agg(
        collect_set("product_id").alias(
            "predicted_items"
        )
    )
)


# --------------------------------------------------
# 14.7 Compare predictions with actual items
# --------------------------------------------------

evaluation_data = (
    actual_items
    .join(
        predicted_items,
        "user_id",
        "inner"
    )
    .withColumn(
        "hits",
        size(
            array_intersect(
                "actual_items",
                "predicted_items"
            )
        )
    )
    .withColumn(
        "precision_at_5",
        col("hits") / lit(5)
    )
    .withColumn(
        "recall_at_5",
        col("hits") / size("actual_items")
    )
)


# --------------------------------------------------
# 14.8 Calculate average metrics
# --------------------------------------------------

evaluation_results = (
    evaluation_data
    .agg(
        avg("precision_at_5").alias(
            "Precision_at_5"
        ),
        avg("recall_at_5").alias(
            "Recall_at_5"
        )
    )
    .first()
)


precision_at_5 = evaluation_results[
    "Precision_at_5"
]

recall_at_5 = evaluation_results[
    "Recall_at_5"
]


# --------------------------------------------------
# 14.9 Display evaluation results
# --------------------------------------------------

print("\n==============================")
print("       MODEL EVALUATION")
print("==============================")

print(
    f"Precision@5 : {precision_at_5:.4f}"
)

print(
    f"Recall@5    : {recall_at_5:.4f}"
)

print("==============================")


# --------------------------------------------------
# 15. Stop Spark
# --------------------------------------------------

spark.stop()

print("\n🛑 Spark stopped.")
print("✅ Recommendation Engine execution completed!")