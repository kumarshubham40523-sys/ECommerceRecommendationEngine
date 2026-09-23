import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FILES
# ============================================================

PRODUCT_FILE = "data/products.csv"
RECOMMENDATION_FILE = "outputs/recommendations.csv"
SEARCH_LOG_FILE = "data/user_searches.csv"

GRAPH_DIR = "outputs/graphs"

os.makedirs(GRAPH_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

products = pd.read_csv(
    PRODUCT_FILE,
    encoding="utf-8-sig"
)

recommendations = pd.read_csv(
    RECOMMENDATION_FILE,
    encoding="utf-8-sig"
)

if os.path.exists(SEARCH_LOG_FILE):
    all_interactions = pd.read_csv(
        SEARCH_LOG_FILE,
        encoding="utf-8-sig"
    )
else:
    all_interactions = pd.DataFrame()


# ============================================================
# DATA TYPES
# ============================================================

products["product_id"] = pd.to_numeric(
    products["product_id"],
    errors="coerce"
)

recommendations["user_id"] = pd.to_numeric(
    recommendations["user_id"],
    errors="coerce"
)

recommendations["product_id"] = pd.to_numeric(
    recommendations["product_id"],
    errors="coerce"
)


# ============================================================
# HYBRID RECOMMENDATION FUNCTION
# Same logic as ShopSmart app
# ============================================================

def get_hybrid_recommendations(selected_user):

    # --------------------------------------------------------
    # Start with all products
    # --------------------------------------------------------

    user_recommendations = products[
        [
            "product_id",
            "product_name",
            "category",
            "price"
        ]
    ].copy()


    # --------------------------------------------------------
    # Get ALS scores
    # --------------------------------------------------------

    user_als = recommendations[
        recommendations["user_id"] == selected_user
    ][
        [
            "product_id",
            "recommendation_score"
        ]
    ].copy()

    user_recommendations = user_recommendations.merge(
        user_als,
        on="product_id",
        how="left"
    )

    user_recommendations["recommendation_score"] = (
        user_recommendations["recommendation_score"]
        .fillna(0)
    )


    # --------------------------------------------------------
    # Normalize ALS score
    # --------------------------------------------------------

    max_als_score = (
        user_recommendations["recommendation_score"].max()
    )

    if max_als_score > 0:

        user_recommendations["als_score"] = (
            user_recommendations["recommendation_score"]
            / max_als_score
        )

    else:

        user_recommendations["als_score"] = 0.0


    # --------------------------------------------------------
    # User interaction history
    # --------------------------------------------------------

    if not all_interactions.empty:

        user_interactions = all_interactions[
            all_interactions["user_id"] == selected_user
        ].copy()

    else:

        user_interactions = pd.DataFrame()


    # --------------------------------------------------------
    # Interaction weights
    # --------------------------------------------------------

    INTERACTION_WEIGHTS = {
        "search": 1,
        "click": 2,
        "cart": 3,
        "purchase": 5
    }


    # --------------------------------------------------------
    # Initialize
    # --------------------------------------------------------

    user_recommendations["behavior_score"] = 0.0

    category_interest = {}

    recent_queries = []


    # ========================================================
    # PROCESS USER INTERACTIONS
    # ========================================================

    if not user_interactions.empty:

        user_interactions["event_type"] = (
            user_interactions["event_type"]
            .astype(str)
            .str.lower()
        )


        # ----------------------------------------------------
        # Recent searches
        # ----------------------------------------------------

        search_history = user_interactions[
            user_interactions["event_type"] == "search"
        ].copy()

        if not search_history.empty:

            recent_queries = (
                search_history
                .sort_values(
                    "timestamp",
                    ascending=False
                )
                .head(10)["query"]
                .dropna()
                .astype(str)
                .str.lower()
                .tolist()
            )


        # ----------------------------------------------------
        # Process interactions
        # ----------------------------------------------------

        for _, interaction in user_interactions.iterrows():

            event_type = str(
                interaction["event_type"]
            ).lower()

            weight = INTERACTION_WEIGHTS.get(
                event_type,
                0
            )

            if weight == 0:
                continue


            # ================================================
            # SEARCH
            # ================================================

            if event_type == "search":

                query = str(
                    interaction.get(
                        "query",
                        ""
                    )
                ).lower().strip()

                if not query:
                    continue

                query_words = query.split()

                for word in query_words:

                    name_match = (
                        user_recommendations[
                            "product_name"
                        ]
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            word,
                            na=False
                        )
                    )

                    category_match = (
                        user_recommendations[
                            "category"
                        ]
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            word,
                            na=False
                        )
                    )

                    user_recommendations.loc[
                        name_match,
                        "behavior_score"
                    ] += 0.08 * weight

                    user_recommendations.loc[
                        category_match,
                        "behavior_score"
                    ] += 0.04 * weight


            # ================================================
            # CLICK / CART / PURCHASE
            # ================================================

            else:

                interaction_product_id = pd.to_numeric(
                    interaction.get(
                        "product_id",
                        None
                    ),
                    errors="coerce"
                )

                if pd.isna(
                    interaction_product_id
                ):
                    continue

                interaction_product_id = int(
                    interaction_product_id
                )


                # Direct product interest

                direct_match = (
                    user_recommendations[
                        "product_id"
                    ]
                    == interaction_product_id
                )

                user_recommendations.loc[
                    direct_match,
                    "behavior_score"
                ] += 0.15 * weight


                # Category interest

                matched_product = products[
                    products["product_id"]
                    == interaction_product_id
                ]

                if not matched_product.empty:

                    interacted_category = str(
                        matched_product.iloc[0]["category"]
                    )

                    category_interest[
                        interacted_category
                    ] = (
                        category_interest.get(
                            interacted_category,
                            0
                        )
                        + weight
                    )


                    # Related category boost

                    same_category = (
                        user_recommendations[
                            "category"
                        ]
                        == interacted_category
                    )

                    user_recommendations.loc[
                        same_category,
                        "behavior_score"
                    ] += 0.05 * weight


    # ========================================================
    # CATEGORY INTEREST FROM SEARCHES
    # ========================================================

    available_categories = (
        user_recommendations["category"]
        .dropna()
        .unique()
        .tolist()
    )

    for query in recent_queries:

        query_words = query.split()

        for category in available_categories:

            category_lower = str(
                category
            ).lower()


            # Direct category search

            if category_lower in query:

                category_interest[
                    category
                ] = (
                    category_interest.get(
                        category,
                        0
                    )
                    + 3
                )


            # Product-name based interest

            else:

                category_products = (
                    user_recommendations[
                        user_recommendations[
                            "category"
                        ] == category
                    ]
                )

                for word in query_words:

                    product_match = (
                        category_products[
                            "product_name"
                        ]
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            word,
                            na=False
                        )
                    )

                    if not product_match.empty:

                        category_interest[
                            category
                        ] = (
                            category_interest.get(
                                category,
                                0
                            )
                            + 1
                        )


    # ========================================================
    # NORMALIZE BEHAVIOR SCORE
    # ========================================================

    max_behavior_score = (
        user_recommendations[
            "behavior_score"
        ].max()
    )

    if max_behavior_score > 0:

        user_recommendations[
            "behavior_score"
        ] = (
            user_recommendations[
                "behavior_score"
            ]
            / max_behavior_score
        )

    else:

        user_recommendations[
            "behavior_score"
        ] = 0.0


    # ========================================================
    # FINAL HYBRID SCORE
    # ========================================================

    user_recommendations[
        "final_score"
    ] = (
        0.40
        * user_recommendations[
            "als_score"
        ]
        +
        0.60
        * user_recommendations[
            "behavior_score"
        ]
    )


    # ========================================================
    # CATEGORY-AWARE SELECTION
    # ========================================================

    if category_interest:

        category_interest = dict(
            sorted(
                category_interest.items(),
                key=lambda item: item[1],
                reverse=True
            )[:5]
        )

        total_interest = sum(
            category_interest.values()
        )

        category_slots = {}

        for category, interest in category_interest.items():

            category_slots[category] = int(
                (interest / total_interest) * 5
            )


        # At least one slot per detected category

        for category in category_slots:

            if category_slots[category] == 0:

                category_slots[category] = 1


        # Reduce excess slots

        while sum(
            category_slots.values()
        ) > 5:

            weakest_category = min(
                category_slots,
                key=category_interest.get
            )

            if category_slots[
                weakest_category
            ] > 1:

                category_slots[
                    weakest_category
                ] -= 1

            else:

                break


        # Add missing slots

        while sum(
            category_slots.values()
        ) < 5:

            strongest_category = max(
                category_interest,
                key=category_interest.get
            )

            category_slots[
                strongest_category
            ] += 1


        # ----------------------------------------------------
        # Select products from each category
        # ----------------------------------------------------

        selected_products = []

        for category, slots in category_slots.items():

            category_products = (
                user_recommendations[
                    user_recommendations[
                        "category"
                    ] == category
                ]
                .copy()
                .sort_values(
                    "final_score",
                    ascending=False
                )
                .head(slots)
            )

            selected_products.append(
                category_products
            )


        if selected_products:

            user_recommendations = pd.concat(
                selected_products,
                ignore_index=True
            )


        user_recommendations = (
            user_recommendations
            .sort_values(
                "final_score",
                ascending=False
            )
            .head(5)
        )

    else:

        user_recommendations = (
            user_recommendations
            .sort_values(
                "final_score",
                ascending=False
            )
            .head(5)
        )


    return user_recommendations


# ============================================================
# USER 1 RECOMMENDATIONS
# ============================================================

sample_user = 1

user_data = get_hybrid_recommendations(
    sample_user
)

print("\n" + "=" * 60)
print(f"HYBRID RECOMMENDATIONS FOR USER {sample_user}")
print("=" * 60)

print(
    user_data[
        [
            "product_id",
            "product_name",
            "category",
            "final_score"
        ]
    ].to_string(index=False)
)


# ============================================================
# GRAPH 1
# User 1 Hybrid Recommendations
# ============================================================

plot_data = (
    user_data
    .sort_values(
        "final_score",
        ascending=True
    )
)

plt.figure(
    figsize=(11, 6.5)
)

bars = plt.barh(
    plot_data["product_name"],
    plot_data["final_score"]
)

plt.xlabel(
    "Hybrid Recommendation Score",
    fontsize=11
)

plt.ylabel(
    "Product",
    fontsize=11
)

plt.title(
    "Top 5 Personalized Recommendations for User 1",
    fontsize=15,
    fontweight="bold"
)

plt.xlim(0, 1.05)

for bar, score in zip(
    bars,
    plot_data["final_score"]
):

    plt.text(
        bar.get_width() + 0.015,
        bar.get_y() + bar.get_height() / 2,
        f"{score:.2f}",
        va="center",
        fontsize=10
    )

plt.grid(
    axis="x",
    alpha=0.25
)

plt.tight_layout()

output_path = (
    f"{GRAPH_DIR}/user_1_recommendations.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"✅ Hybrid recommendation graph saved: "
    f"{output_path}"
)


# ============================================================
# GRAPH 2
# User 1 Category Distribution
# ============================================================

category_counts = (
    user_data["category"]
    .value_counts()
)

plt.figure(
    figsize=(8, 7)
)

plt.pie(
    category_counts.values,
    labels=category_counts.index,
    autopct="%1.0f%%",
    startangle=90,
    wedgeprops={
        "width": 0.45,
        "edgecolor": "white"
    }
)

plt.title(
    "Category Distribution of User 1 Recommendations",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()

output_path = (
    f"{GRAPH_DIR}/user_1_category_distribution.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"✅ Category distribution graph saved: "
    f"{output_path}"
)


# ============================================================
# GRAPH 3
# Average Hybrid Recommendation Score — Users 1–10
# ============================================================

sample_scores = []

for user_id in range(1, 11):

    user_results = get_hybrid_recommendations(
        user_id
    )

    if not user_results.empty:

        average_score = (
            user_results["final_score"]
            .mean()
        )

        sample_scores.append(
            {
                "user_id": user_id,
                "average_score": average_score
            }
        )


user_scores = pd.DataFrame(
    sample_scores
)

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    user_scores["user_id"].astype(str),
    user_scores["average_score"]
)

plt.xlabel(
    "User ID",
    fontsize=11
)

plt.ylabel(
    "Average Hybrid Recommendation Score",
    fontsize=11
)

plt.title(
    "Average Recommendation Score for Sample Users (1–10)",
    fontsize=14,
    fontweight="bold"
)

plt.ylim(0, 1.05)

for bar, score in zip(
    bars,
    user_scores["average_score"]
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{score:.2f}",
        ha="center",
        fontsize=9
    )

plt.grid(
    axis="y",
    alpha=0.25
)

plt.tight_layout()

output_path = (
    f"{GRAPH_DIR}/sample_users_average_scores.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"✅ Hybrid user comparison graph saved: "
    f"{output_path}"
)

print("\n" + "=" * 60)
print("ALL HYBRID RECOMMENDATION GRAPHS GENERATED")
print("=" * 60)