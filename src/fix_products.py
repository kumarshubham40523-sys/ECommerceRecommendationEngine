import csv
import random
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

NUM_PRODUCTS = 200
PRODUCTS_PER_GROUP = 10
NUM_GROUPS = 20

OUTPUT_FILE = "data/products.csv"

random.seed(42)


# ============================================================
# PRODUCT CATEGORIES
# ============================================================

categories = [
    "Electronics",
    "Fashion",
    "Books",
    "Home",
    "Sports",
    "Beauty"
]


# ============================================================
# PRODUCT NAMES
# ============================================================

product_names = {

    "Electronics": [
        "Smartphone",
        "Laptop",
        "Wireless Headphones",
        "Smartwatch",
        "Tablet",
        "Digital Camera",
        "Mechanical Keyboard",
        "Wireless Mouse",
        "Computer Monitor",
        "Bluetooth Speaker"
    ],

    "Fashion": [
        "Cotton T-Shirt",
        "Slim Fit Jeans",
        "Casual Jacket",
        "Running Sneakers",
        "Pullover Hoodie",
        "Travel Backpack",
        "Wrist Watch",
        "Sunglasses",
        "Casual Shoes",
        "Baseball Cap"
    ],

    "Books": [
        "Python Programming Book",
        "Data Science Book",
        "Machine Learning Book",
        "AI Fundamentals Book",
        "Database Systems Book",
        "Operating Systems Book",
        "Computer Networks Book",
        "Java Programming Book",
        "Algorithms Book",
        "Cloud Computing Book"
    ],

    "Home": [
        "Table Lamp",
        "Ergonomic Office Chair",
        "Cotton Bed Sheet",
        "Window Curtains",
        "Wall Clock",
        "Storage Organizer",
        "Decorative Cushion",
        "Desk Organizer",
        "Steel Water Bottle",
        "Home Decor Set"
    ],

    "Sports": [
        "Football",
        "Cricket Bat",
        "Badminton Racket",
        "Tennis Ball Set",
        "Gym Gloves",
        "Yoga Mat",
        "Skipping Rope",
        "Sports Shoes",
        "Adjustable Dumbbells",
        "Fitness Band"
    ],

    "Beauty": [
        "Face Wash",
        "Moisturizer",
        "Shampoo",
        "Perfume",
        "Sunscreen",
        "Lip Balm",
        "Hair Oil",
        "Body Lotion",
        "Face Cream",
        "Beauty Care Kit"
    ]
}


# ============================================================
# CATEGORY PRICE RANGES
# ============================================================

price_ranges = {

    "Electronics": (1500, 80000),
    "Fashion": (300, 8000),
    "Books": (250, 2500),
    "Home": (300, 12000),
    "Sports": (400, 10000),
    "Beauty": (200, 5000)
}


# ============================================================
# CREATE PRODUCTS
# ============================================================

products = []


for product_id in range(
    1,
    NUM_PRODUCTS + 1
):

    # Every 10 products form one interest group.
    group_id = (
        (product_id - 1)
        // PRODUCTS_PER_GROUP
    )

    # Rotate categories between groups.
    category = categories[
        group_id % len(categories)
    ]

    name_index = (
        (product_id - 1)
        % PRODUCTS_PER_GROUP
    )

    product_name = product_names[
        category
    ][name_index]

    minimum_price, maximum_price = price_ranges[
        category
    ]

    price = round(
        random.uniform(
            minimum_price,
            maximum_price
        ),
        2
    )

    products.append(
        {
            "product_id": product_id,
            "product_name": (
                f"{product_name} {product_id}"
            ),
            "category": category,
            "price": price
        }
    )


# ============================================================
# CREATE DATA DIRECTORY
# ============================================================

Path("data").mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# WRITE PRODUCTS CSV
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "product_id",
            "product_name",
            "category",
            "price"
        ]
    )

    writer.writeheader()

    writer.writerows(products)


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("=" * 65)
print("PRODUCT CATALOG UPDATED SUCCESSFULLY")
print("=" * 65)

print()
print(f"Total products : {len(products)}")

print()
print("Category distribution:")

category_counts = {}

for product in products:

    category = product["category"]

    category_counts[category] = (
        category_counts.get(category, 0) + 1
    )


for category in categories:

    print(
        f"{category:<15} : "
        f"{category_counts.get(category, 0)}"
    )


print()
print("Sample products:")

for product in products[:12]:

    print(
        f"{product['product_id']:>3} | "
        f"{product['product_name']:<32} | "
        f"{product['category']:<12} | "
        f"₹{product['price']:.2f}"
    )


print()
print(f"Updated file : {OUTPUT_FILE}")

print("=" * 65)