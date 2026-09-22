import pandas as pd
import matplotlib.pyplot as plt
import os

# Load recommendation results
file_path = "outputs/recommendations.csv"
df = pd.read_csv(file_path)

# Select one sample user
sample_user = 1

user_data = df[df["user_id"] == sample_user].copy()

# Sort by recommendation score
user_data = user_data.sort_values(
    "recommendation_score",
    ascending=True
)

# Create output directory
os.makedirs("outputs/graphs", exist_ok=True)

# Create graph
plt.figure(figsize=(10, 6))

plt.barh(
    user_data["product_name"],
    user_data["recommendation_score"]
)

plt.xlabel("Recommendation Score")
plt.ylabel("Product")
plt.title(f"Top 5 Recommended Products for User {sample_user}")

plt.tight_layout()

# Save graph
output_path = "outputs/graphs/user_1_recommendations.png"
plt.savefig(output_path, dpi=300)

print(f"✅ Graph saved to: {output_path}")

plt.show()

# --------------------------------------------------
# Graph 2: Recommended Products by Category
# --------------------------------------------------

category_counts = user_data["category"].value_counts()

plt.figure(figsize=(9, 6))

plt.bar(
    category_counts.index,
    category_counts.values
)

plt.xlabel("Product Category")
plt.ylabel("Number of Recommended Products")
plt.title(f"Recommended Products by Category for User {sample_user}")

plt.xticks(rotation=30)
plt.tight_layout()

output_path = "outputs/graphs/user_1_category_distribution.png"
plt.savefig(output_path, dpi=300)

print(f"✅ Category graph saved to: {output_path}")

plt.show()

# --------------------------------------------------
# Graph 3: Average Recommendation Score by User
# --------------------------------------------------

user_scores = (
    df[df["user_id"].between(1, 10)]
    .groupby("user_id")["recommendation_score"]
    .mean()
)

plt.figure(figsize=(10, 6))

plt.bar(
    user_scores.index.astype(str),
    user_scores.values
)

plt.xlabel("User ID")
plt.ylabel("Average Recommendation Score")
plt.title("Average Recommendation Score for Sample Users (1–10)")

plt.tight_layout()

output_path = "outputs/graphs/sample_users_average_scores.png"
plt.savefig(output_path, dpi=300)

print(f"✅ User comparison graph saved to: {output_path}")

plt.show()