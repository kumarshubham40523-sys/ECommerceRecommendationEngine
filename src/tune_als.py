import os
import sys
import csv

# ==================================================
# Spark / Python configuration
# ==================================================

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


# ==================================================
# 1. Start Spark
# ==================================================

spark = (
    SparkSession.builder
    .appName("ECommerceALSHyperparameterTuning")
    .master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print("\n🔥 Spark started!")
print("Spark version:", spark.version)


# ==================================================
# 2. Load interaction data
# ==================================================

interactions = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/ecommerce_interactions.csv")
)

print("\n📥 Interaction data loaded:")
print("Total interactions:", interactions.count())


# ==================================================
# 3. Convert events into interaction scores
# ==================================================

weighted_data = interactions.withColumn(
    "interaction_score",
    when(col("event_type") == "view", 1)
    .when(col("event_type") == "click", 2)
    .when(col("event_type") == "cart", 3)
    .when(col("event_type") == "purchase", 5)
    .when(col("event_type") == "review", 5)
    .otherwise(0)
)


# ==================================================
# 4. Create ALS-ready user-product data
# ==================================================

als_data = (
    weighted_data
    .groupBy("user_id", "product_id")
    .agg(
        spark_sum("interaction_score").alias("rating")
    )
    .withColumn(
        "user_id",
        col("user_id").cast("integer")
    )
    .withColumn(
        "product_id",
        col("product_id").cast("integer")
    )
    .withColumn(
        "rating",
        col("rating").cast("float")
    )
)

print(
    "\n📊 User-product pairs:",
    als_data.count()
)


# ==================================================
# 5. Create fixed train/test split
# ==================================================

training_data, testing_data = als_data.randomSplit(
    [0.8, 0.2],
    seed=42
)

# Cache because we will reuse these for every model
training_data.cache()
testing_data.cache()

training_count = training_data.count()
testing_count = testing_data.count()

print("\n📚 Training records:", training_count)
print("🧪 Testing records:", testing_count)


# ==================================================
# 6. Prepare actual test items
# ==================================================

actual_items = (
    testing_data
    .filter(col("rating") > 0)
    .groupBy("user_id")
    .agg(
        collect_set("product_id").alias("actual_items")
    )
)


# ==================================================
# 7. ALS configurations to test
# ==================================================

configurations = [
    {
        "name": "Config_1",
        "rank": 10,
        "maxIter": 10,
        "regParam": 0.10
    },
    {
        "name": "Config_2",
        "rank": 20,
        "maxIter": 10,
        "regParam": 0.10
    },
    {
        "name": "Config_3",
        "rank": 20,
        "maxIter": 15,
        "regParam": 0.05
    },
    {
        "name": "Config_4",
        "rank": 30,
        "maxIter": 15,
        "regParam": 0.01
    }
]


# ==================================================
# 8. Evaluate each configuration
# ==================================================

results = []

print("\n")
print("==============================================")
print("       ALS HYPERPARAMETER TUNING")
print("==============================================")


for config in configurations:

    print("\n----------------------------------------------")
    print(f"🤖 Testing {config['name']}")
    print("----------------------------------------------")

    print(
        f"Rank      : {config['rank']}"
    )

    print(
        f"Max Iter  : {config['maxIter']}"
    )

    print(
        f"Reg Param : {config['regParam']}"
    )

    # --------------------------------------------------
    # Create ALS model
    # --------------------------------------------------

    als = ALS(
        userCol="user_id",
        itemCol="product_id",
        ratingCol="rating",
        rank=config["rank"],
        maxIter=config["maxIter"],
        regParam=config["regParam"],
        implicitPrefs=True,
        coldStartStrategy="drop",
        seed=42
    )

    # --------------------------------------------------
    # Train model
    # --------------------------------------------------

    print("⏳ Training...")

    model = als.fit(training_data)

    print("✅ Training completed!")

    # --------------------------------------------------
    # Generate 20 candidates
    # --------------------------------------------------

    recommendations = (
        model
        .recommendForAllUsers(20)
        .select(
            "user_id",
            "recommendations"
        )
    )

    # --------------------------------------------------
    # Flatten recommendations
    # --------------------------------------------------

    candidate_recommendations = (
        recommendations
        .select(
            "user_id",
            explode("recommendations").alias(
                "recommendation"
            )
        )
        .select(
            "user_id",
            col(
                "recommendation.product_id"
            ).alias("product_id"),
            col(
                "recommendation.rating"
            ).alias("score")
        )
    )

    # --------------------------------------------------
    # Find products already seen during training
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
    # Remove previously seen products
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
    # Rank recommendations by ALS score
    # --------------------------------------------------

    ranking_window = (
        Window
        .partitionBy("user_id")
        .orderBy(
            col("score").desc()
        )
    )

    predicted_items = (
        unseen_recommendations
        .withColumn(
            "rank",
            row_number().over(
                ranking_window
            )
        )
        .filter(
            col("rank") <= 5
        )
        .groupBy("user_id")
        .agg(
            collect_set(
                "product_id"
            ).alias(
                "predicted_items"
            )
        )
    )

    # --------------------------------------------------
    # Compare predicted vs actual
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
            col("hits")
            / size("actual_items")
        )
    )

    # --------------------------------------------------
    # Calculate averages
    # --------------------------------------------------

    metrics = (
        evaluation_data
        .agg(
            avg(
                "precision_at_5"
            ).alias(
                "precision_at_5"
            ),
            avg(
                "recall_at_5"
            ).alias(
                "recall_at_5"
            )
        )
        .first()
    )

    precision_value = metrics[
        "precision_at_5"
    ]

    recall_value = metrics[
        "recall_at_5"
    ]

    # --------------------------------------------------
    # Store results
    # --------------------------------------------------

    results.append({
        "configuration": config["name"],
        "rank": config["rank"],
        "maxIter": config["maxIter"],
        "regParam": config["regParam"],
        "precision_at_5": precision_value,
        "recall_at_5": recall_value
    })

    print("\n📊 Results:")
    print(
        f"Precision@5 : {precision_value:.4f}"
    )
    print(
        f"Recall@5    : {recall_value:.4f}"
    )


# ==================================================
# 9. Display comparison
# ==================================================

print("\n")
print("======================================================")
print("             ALS TUNING RESULTS")
print("======================================================")

print(
    "\nConfiguration | Rank | Iterations | RegParam | "
    "Precision@5 | Recall@5"
)

print(
    "-" * 75
)

for result in results:

    print(
        f"{result['configuration']:13} | "
        f"{result['rank']:4} | "
        f"{result['maxIter']:10} | "
        f"{result['regParam']:8.2f} | "
        f"{result['precision_at_5']:.4f}       | "
        f"{result['recall_at_5']:.4f}"
    )


# ==================================================
# 10. Select best configuration
# ==================================================

best_result = max(
    results,
    key=lambda x: (
        x["precision_at_5"],
        x["recall_at_5"]
    )
)


print("\n")
print("==============================================")
print("        SELECTED ALS CONFIGURATION")
print("==============================================")

print(
    f"Configuration : {best_result['configuration']}"
)

print(
    f"Rank          : {best_result['rank']}"
)

print(
    f"Max Iter      : {best_result['maxIter']}"
)

print(
    f"Reg Param     : {best_result['regParam']}"
)

print(
    f"Precision@5   : "
    f"{best_result['precision_at_5']:.4f}"
)

print(
    f"Recall@5      : "
    f"{best_result['recall_at_5']:.4f}"
)

print("==============================================")


# ==================================================
# 11. Save tuning results
# ==================================================

output_file = (
    "outputs/als_tuning_results.csv"
)

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "configuration",
        "rank",
        "maxIter",
        "regParam",
        "precision_at_5",
        "recall_at_5"
    ])

    for result in results:

        writer.writerow([
            result["configuration"],
            result["rank"],
            result["maxIter"],
            result["regParam"],
            result["precision_at_5"],
            result["recall_at_5"]
        ])


print(
    f"\n💾 Tuning results saved to: "
    f"{output_file}"
)


# ==================================================
# 12. Stop Spark
# ==================================================

training_data.unpersist()
testing_data.unpersist()

spark.stop()

print("\n🛑 Spark stopped!")
print("✅ ALS hyperparameter tuning completed!")