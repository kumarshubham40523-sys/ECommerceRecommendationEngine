import csv
import random
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

NUM_USERS = 1000
NUM_PRODUCTS = 200
NUM_INTERACTIONS = 50000

NUM_INTEREST_GROUPS = 20
PRODUCTS_PER_GROUP = 10

START_DATE = datetime(2026, 1, 1)

random.seed(42)


# ============================================================
# PRODUCT GROUPS
# ============================================================

# Each interest group contains 10 products.
# Group 0 -> Products 1-10
# Group 1 -> Products 11-20
# ...
# Group 19 -> Products 191-200

interest_groups = {}

for group_id in range(NUM_INTEREST_GROUPS):
    start_product = group_id * PRODUCTS_PER_GROUP + 1

    products_in_group = list(
        range(
            start_product,
            start_product + PRODUCTS_PER_GROUP
        )
    )

    interest_groups[group_id] = products_in_group


# ============================================================
# PRODUCT INFORMATION
# ============================================================

categories = [
    "Electronics",
    "Fashion",
    "Books",
    "Home",
    "Sports",
    "Beauty"
]

product_names = [
    "Smartphone",
    "Laptop",
    "Headphones",
    "Smartwatch",
    "Tablet",
    "Camera",
    "Keyboard",
    "Mouse",
    "Monitor",
    "Speaker",

    "T-Shirt",
    "Jeans",
    "Jacket",
    "Sneakers",
    "Hoodie",
    "Backpack",
    "Watch",
    "Sunglasses",
    "Shoes",
    "Cap",

    "Python Programming Book",
    "Data Science Book",
    "Machine Learning Book",
    "AI Fundamentals Book",
    "Database Book",
    "Operating Systems Book",
    "Computer Networks Book",
    "Java Programming Book",
    "Algorithms Book",
    "Cloud Computing Book",

    "Table Lamp",
    "Office Chair",
    "Bed Sheet",
    "Curtains",
    "Wall Clock",
    "Storage Box",
    "Cushion",
    "Desk Organizer",
    "Water Bottle",
    "Home Decor",

    "Football",
    "Cricket Bat",
    "Badminton Racket",
    "Tennis Ball",
    "Gym Gloves",
    "Yoga Mat",
    "Skipping Rope",
    "Sports Shoes",
    "Dumbbells",
    "Fitness Band",

    "Face Wash",
    "Moisturizer",
    "Shampoo",
    "Perfume",
    "Sunscreen",
    "Lip Balm",
    "Hair Oil",
    "Body Lotion",
    "Face Cream",
    "Beauty Kit"
]


# ============================================================
# CREATE PRODUCTS
# ============================================================

products = []

for product_id in range(1, NUM_PRODUCTS + 1):

    category = categories[(product_id - 1) % len(categories)]

    base_name = product_names[(product_id - 1) % len(product_names)]

    product = {
        "product_id": product_id,
        "product_name": f"{base_name} {product_id}",
        "category": category,
        "price": round(random.uniform(199, 99999), 2)
    }

    products.append(product)


# ============================================================
# CREATE USER PREFERENCES
# ============================================================

# Every user gets:
#
# 1. Primary group
#    Long-term/persistent interest
#
# 2. Secondary group
#    Recent or developing interest
#
# This gives the recommendation engine something
# meaningful to learn from historical interactions.

user_preferences = {}

for user_id in range(1, NUM_USERS + 1):

    primary_group = random.randint(
        0,
        NUM_INTEREST_GROUPS - 1
    )

    secondary_group = random.randint(
        0,
        NUM_INTEREST_GROUPS - 1
    )

    # Make sure primary and secondary groups differ.
    while secondary_group == primary_group:
        secondary_group = random.randint(
            0,
            NUM_INTEREST_GROUPS - 1
        )

    user_preferences[user_id] = {
        "primary_group": primary_group,
        "secondary_group": secondary_group
    }


# ============================================================
# EVENT TYPES
# ============================================================

event_types = [
    "view",
    "click",
    "cart",
    "purchase",
    "review"
]

event_weights = [
    55,
    25,
    10,
    7,
    3
]


# ============================================================
# GENERATE INTERACTIONS
# ============================================================

interactions = []

TOTAL_DAYS = 180

for _ in range(NUM_INTERACTIONS):

    # --------------------------------------------------------
    # Select user
    # --------------------------------------------------------

    user_id = random.randint(
        1,
        NUM_USERS
    )

    preferences = user_preferences[user_id]

    primary_group = preferences["primary_group"]
    secondary_group = preferences["secondary_group"]


    # --------------------------------------------------------
    # Generate timestamp
    # --------------------------------------------------------

    random_seconds = random.randint(
        0,
        TOTAL_DAYS * 24 * 60 * 60 - 1
    )

    timestamp = START_DATE + timedelta(
        seconds=random_seconds
    )

    # Convert timestamp to a fraction of the dataset timeline.
    #
    # 0.0 = beginning
    # 1.0 = end

    time_fraction = (
        random_seconds
        / (TOTAL_DAYS * 24 * 60 * 60)
    )


    # --------------------------------------------------------
    # Product preference behavior
    # --------------------------------------------------------
    #
    # EARLY PERIOD:
    #   80% primary
    #   10% secondary
    #   10% exploration
    #
    # LATER PERIOD:
    #   60% primary
    #   30% secondary
    #   10% exploration
    #
    # This creates a realistic shift in user interests.
    # --------------------------------------------------------

    if time_fraction < 0.60:

        behavior = random.choices(
            [
                "primary",
                "secondary",
                "exploration"
            ],
            weights=[
                80,
                10,
                10
            ],
            k=1
        )[0]

    else:

        behavior = random.choices(
            [
                "primary",
                "secondary",
                "exploration"
            ],
            weights=[
                60,
                30,
                10
            ],
            k=1
        )[0]


    # --------------------------------------------------------
    # Select product
    # --------------------------------------------------------

    if behavior == "primary":

        product_id = random.choice(
            interest_groups[primary_group]
        )

    elif behavior == "secondary":

        product_id = random.choice(
            interest_groups[secondary_group]
        )

    else:

        product_id = random.randint(
            1,
            NUM_PRODUCTS
        )


    # --------------------------------------------------------
    # Event type
    # --------------------------------------------------------

    event_type = random.choices(
        event_types,
        weights=event_weights,
        k=1
    )[0]


    # --------------------------------------------------------
    # Rating
    # --------------------------------------------------------

    if event_type == "review":

        rating = random.randint(
            3,
            5
        )

    else:

        rating = 0


    # --------------------------------------------------------
    # Store interaction
    # --------------------------------------------------------

    interactions.append(
        {
            "user_id": user_id,
            "product_id": product_id,
            "event_type": event_type,
            "timestamp": timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "rating": rating
        }
    )


# ============================================================
# SORT INTERACTIONS CHRONOLOGICALLY
# ============================================================

interactions.sort(
    key=lambda x: x["timestamp"]
)


# ============================================================
# WRITE PRODUCTS CSV
# ============================================================

with open(
    "data/products.csv",
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
# WRITE INTERACTIONS CSV
# ============================================================

with open(
    "data/ecommerce_interactions.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "user_id",
            "product_id",
            "event_type",
            "timestamp",
            "rating"
        ]
    )

    writer.writeheader()

    writer.writerows(interactions)


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("=" * 60)
print("E-COMMERCE DATASET GENERATED SUCCESSFULLY")
print("=" * 60)

print(f"Users              : {NUM_USERS}")
print(f"Products           : {NUM_PRODUCTS}")
print(f"Interactions       : {NUM_INTERACTIONS}")
print(f"Interest Groups    : {NUM_INTEREST_GROUPS}")
print(f"Products per Group: {PRODUCTS_PER_GROUP}")

print()
print("Preference behavior:")
print("Early period  -> 80% primary, 10% secondary, 10% exploration")
print("Later period  -> 60% primary, 30% secondary, 10% exploration")

print()
print("Files created:")
print("data/products.csv")
print("data/ecommerce_interactions.csv")

print("=" * 60)