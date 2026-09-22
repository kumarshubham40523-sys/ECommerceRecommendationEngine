import os
import sys

# ============================================================
# PYSPARK / WINDOWS CONFIGURATION
# ============================================================

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"


# ============================================================
# IMPORTS
# ============================================================

from pyspark.sql import SparkSession

from pyspark.sql.functions import (
    col,
    when,
    sum as spark_sum,
    unix_timestamp,
    lit,
    explode,
    row_number,
    size,
    collect_set,
    array_intersect,
    avg
)

from pyspark.sql.window import Window

from pyspark.ml.recommendation import ALS


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

DATA_PATH = "data/ecommerce_interactions.csv"

NUM_PRODUCTS = 200

RANDOM_SEED = 42

# ------------------------------------------------------------
# ALS parameters selected during hyperparameter tuning
# ------------------------------------------------------------

ALS_RANK = 10
ALS_MAX_ITER = 10
ALS_REG_PARAM = 0.1


# ============================================================
# CREATE SPARK SESSION
# ============================================================

spark = (
    SparkSession.builder
    .appName("ECommerceTimeBasedEvaluation")
    .master("local[2]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


# ============================================================
# START
# ============================================================

print()
print("=" * 65)
print("TIME-BASED RECOMMENDATION ENGINE EVALUATION")
print("=" * 65)


# ============================================================
# 1. LOAD INTERACTION DATA
# ============================================================

print()
print("STEP 1: Loading interaction data...")

raw_data = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(DATA_PATH)
)

total_interactions = raw_data.count()

print(f"Total interactions loaded : {total_interactions}")


# ============================================================
# 2. CONVERT TIMESTAMP TO NUMERIC VALUE
# ============================================================
#
# Spark's approxQuantile works with numeric columns.
#
# Therefore:
#
# timestamp
#     ↓
# unix timestamp
#     ↓
# numeric value
#
# ============================================================

print()
print("STEP 2: Processing timestamps...")

data = raw_data.withColumn(
    "timestamp_unix",
    unix_timestamp(
        col("timestamp"),
        "yyyy-MM-dd HH:mm:ss"
    )
)


# ============================================================
# 3. FIND 80% TIME CUTOFF
# ============================================================
#
# The earliest 80% of interactions are used for training.
#
# The latest 20% are used for testing.
#
# This simulates a real recommendation system:
#
# Past behavior
#      ↓
# Train model
#      ↓
# Predict future behavior
#
# ============================================================

print()
print("STEP 3: Creating chronological 80/20 split...")

quantile_result = data.approxQuantile(
    "timestamp_unix",
    [0.80],
    0.0
)

timestamp_cutoff = quantile_result[0]


# Convert Unix timestamp back to readable date/time.

cutoff_timestamp = spark.sql(
    f"""
    SELECT from_unixtime({int(timestamp_cutoff)})
    AS cutoff
    """
).collect()[0]["cutoff"]


print(f"80% time cutoff : {cutoff_timestamp}")


# ------------------------------------------------------------
# Training = earliest 80%
# Testing  = latest 20%
# ------------------------------------------------------------

training_raw = data.filter(
    col("timestamp_unix") <= lit(timestamp_cutoff)
)

testing_raw = data.filter(
    col("timestamp_unix") > lit(timestamp_cutoff)
)


training_interactions = training_raw.count()
testing_interactions = testing_raw.count()


print(f"Training interactions : {training_interactions}")
print(f"Testing interactions  : {testing_interactions}")


# ============================================================
# 4. CONVERT EVENTS INTO IMPLICIT RATINGS
# ============================================================
#
# We don't have an explicit rating for every interaction.
#
# Therefore we convert user behavior into preference scores:
#
# View      = 1
# Click     = 2
# Cart      = 3
# Purchase  = 5
# Review    = 5
#
# Higher score = stronger indication of interest.
#
# ============================================================

print()
print("STEP 4: Creating implicit preference scores...")


def create_ratings(input_dataframe):

    weighted_data = input_dataframe.withColumn(
        "interaction_score",

        when(
            col("event_type") == "view",
            1.0
        )

        .when(
            col("event_type") == "click",
            2.0
        )

        .when(
            col("event_type") == "cart",
            3.0
        )

        .when(
            col("event_type") == "purchase",
            5.0
        )

        .when(
            col("event_type") == "review",
            5.0
        )

        .otherwise(0.0)
    )

    ratings = (
        weighted_data
        .groupBy(
            "user_id",
            "product_id"
        )
        .agg(
            spark_sum(
                "interaction_score"
            ).alias("rating")
        )
        .select(
            col("user_id").cast("int"),
            col("product_id").cast("int"),
            col("rating").cast("float")
        )
    )

    return ratings


training_data = create_ratings(
    training_raw
)

testing_data = create_ratings(
    testing_raw
)


training_pairs = training_data.count()
testing_pairs = testing_data.count()


print(
    f"Training user-product pairs : {training_pairs}"
)

print(
    f"Testing user-product pairs  : {testing_pairs}"
)


# ============================================================
# 5. TRAIN ALS MODEL
# ============================================================

print()
print("STEP 5: Training ALS recommendation model...")

print()
print("ALS Configuration:")
print(f"Rank        : {ALS_RANK}")
print(f"Max Iter    : {ALS_MAX_ITER}")
print(f"Reg Param   : {ALS_REG_PARAM}")
print("Implicit    : True")


als = ALS(

    # Data columns
    userCol="user_id",
    itemCol="product_id",
    ratingCol="rating",

    # Model parameters
    rank=ALS_RANK,
    maxIter=ALS_MAX_ITER,
    regParam=ALS_REG_PARAM,

    # Important for implicit feedback
    implicitPrefs=True,

    # Ignore users/items that cannot be predicted
    coldStartStrategy="drop",

    # Reproducibility
    seed=RANDOM_SEED
)


model = als.fit(
    training_data
)


print()
print("ALS model training completed successfully.")


# ============================================================
# 6. GENERATE RECOMMENDATIONS
# ============================================================
#
# IMPORTANT IMPROVEMENT:
#
# Previously we generated only 20 recommendations.
#
# Now we generate recommendations across the complete
# 200-product catalog.
#
# This gives us a much larger candidate pool.
#
# ============================================================

print()
print("STEP 6: Generating recommendation candidates...")

recommendations = model.recommendForAllUsers(
    NUM_PRODUCTS
)


# ============================================================
# 7. FLATTEN RECOMMENDATIONS
# ============================================================
#
# Spark returns:
#
# user_id | recommendations
#
# where recommendations contains structs:
#
# product_id + rating
#
# explode() converts them into individual rows.
#
# ============================================================

recommendation_candidates = (

    recommendations

    .select(
        col("user_id"),
        explode(
            col("recommendations")
        ).alias("recommendation")
    )

    .select(
        col("user_id"),

        col(
            "recommendation.product_id"
        ).alias("product_id"),

        col(
            "recommendation.rating"
        ).alias("score")
    )
)


candidate_count = recommendation_candidates.count()

print(
    f"Recommendation candidates generated : {candidate_count}"
)


# ============================================================
# 8. FIND PRODUCTS ALREADY SEEN DURING TRAINING
# ============================================================
#
# These products should not be counted as new recommendations.
#
# ============================================================

print()
print("STEP 7: Removing previously seen products...")


seen_items = (

    training_data

    .select(
        "user_id",
        "product_id"
    )

    .distinct()
)


seen_count = seen_items.count()

print(
    f"Unique training user-product pairs : {seen_count}"
)


# ============================================================
# 9. REMOVE SEEN PRODUCTS
# ============================================================
#
# left_anti keeps only rows that DON'T exist
# in the training interaction set.
#
# Result:
#
# Recommended products
#        ↓
# Remove previously seen
#        ↓
# Unseen candidates
#
# ============================================================

unseen_candidates = (

    recommendation_candidates

    .join(
        seen_items,

        on=[
            "user_id",
            "product_id"
        ],

        how="left_anti"
    )
)


unseen_count = unseen_candidates.count()

print(
    f"Unseen recommendation candidates : {unseen_count}"
)


# ============================================================
# 10. RANK UNSEEN PRODUCTS FOR EACH USER
# ============================================================
#
# Higher ALS score = stronger predicted preference.
#
# ============================================================

print()
print("STEP 8: Ranking unseen recommendations...")


ranking_window = (

    Window

    .partitionBy(
        "user_id"
    )

    .orderBy(
        col("score").desc()
    )
)


ranked_recommendations = (

    unseen_candidates

    .withColumn(
        "recommendation_rank",

        row_number().over(
            ranking_window
        )
    )
)


# ============================================================
# 11. SELECT TOP 5 UNSEEN PRODUCTS
# ============================================================

top5_recommendations = (

    ranked_recommendations

    .filter(
        col("recommendation_rank") <= 5
    )
)


top5_count = top5_recommendations.count()


print(
    f"Top-5 recommendation rows : {top5_count}"
)


# ============================================================
# 12. COLLECT ACTUAL FUTURE PRODUCTS
# ============================================================
#
# These are products that users actually interacted with
# during the testing period.
#
# ============================================================

print()
print("STEP 9: Preparing future user behavior...")


actual_items = (

    testing_data

    .groupBy(
        "user_id"
    )

    .agg(
        collect_set(
            "product_id"
        ).alias(
            "actual_products"
        )
    )
)


actual_user_count = actual_items.count()


print(
    f"Users with future interactions : {actual_user_count}"
)


# ============================================================
# 13. COLLECT PREDICTED PRODUCTS
# ============================================================

predicted_items = (

    top5_recommendations

    .groupBy(
        "user_id"
    )

    .agg(
        collect_set(
            "product_id"
        ).alias(
            "predicted_products"
        )
    )
)


predicted_user_count = predicted_items.count()


print(
    f"Users with recommendations : {predicted_user_count}"
)


# ============================================================
# 14. JOIN ACTUAL AND PREDICTED ITEMS
# ============================================================

evaluation_data = (

    actual_items

    .join(
        predicted_items,

        on="user_id",

        how="inner"
    )
)


# ============================================================
# 15. CALCULATE NUMBER OF HITS
# ============================================================
#
# A "hit" occurs when:
#
# Recommended product
#          =
# Future product actually interacted with
#
# Example:
#
# Recommended = [10, 25, 80, 91, 150]
#
# Future      = [25, 40, 91]
#
# Hits = 2
#
# ============================================================

evaluation_data = (

    evaluation_data

    .withColumn(
        "hits",

        size(
            array_intersect(
                col("predicted_products"),
                col("actual_products")
            )
        )
    )
)


# ============================================================
# 16. CALCULATE PRECISION@5
# ============================================================
#
# Formula:
#
# Precision@5 =
#
# Relevant recommendations
# -------------------------
#          5
#
# Example:
#
# 2 relevant recommendations out of 5
#
# Precision@5 = 2 / 5 = 0.40
#
# ============================================================

evaluation_data = (

    evaluation_data

    .withColumn(
        "precision_at_5",

        col("hits") / lit(5.0)
    )
)


# ============================================================
# 17. CALCULATE RECALL@5
# ============================================================
#
# Formula:
#
# Recall@5 =
#
# Relevant recommendations
# -------------------------
# Total relevant future items
#
# ============================================================

evaluation_data = (

    evaluation_data

    .withColumn(
        "recall_at_5",

        col("hits")
        /
        size(
            col("actual_products")
        )
    )
)


# ============================================================
# 18. REMOVE INVALID VALUES
# ============================================================

evaluation_data = (

    evaluation_data

    .filter(
        col("recall_at_5").isNotNull()
    )

    .filter(
        col("recall_at_5") >= 0
    )
)


# ============================================================
# 19. CALCULATE FINAL AVERAGE METRICS
# ============================================================

final_metrics = (

    evaluation_data

    .select(

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

    .collect()[0]
)


precision_at_5 = final_metrics[
    "precision_at_5"
]

recall_at_5 = final_metrics[
    "recall_at_5"
]


# ============================================================
# 20. NUMBER OF EVALUATED USERS
# ============================================================

evaluated_users = evaluation_data.count()


# ============================================================
# 21. FINAL RESULTS
# ============================================================

print()
print()
print("=" * 65)
print("FINAL TIME-BASED MODEL EVALUATION")
print("=" * 65)

print()

print(
    f"Precision@5 : {precision_at_5:.4f}"
)

print(
    f"Recall@5    : {recall_at_5:.4f}"
)

print(
    f"Evaluated users : {evaluated_users}"
)

print()

print("Interpretation:")
print(
    "Precision@5 measures how many of the top 5 "
    "recommendations were relevant."
)

print(
    "Recall@5 measures how many of the user's "
    "future relevant products were captured."
)

print()

print("=" * 65)
print("EVALUATION COMPLETED")
print("=" * 65)


# ============================================================
# 22. STOP SPARK
# ============================================================

spark.stop()