import csv
import subprocess
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/products.csv"
OUTPUT_FILE = "outputs/gpt_product_descriptions.csv"

MODEL_NAME = "llama3.2:3b"

# ------------------------------------------------------------
# TEST MODE
# ------------------------------------------------------------
# We are testing only 3 products first.
# After the output is verified, change this to:
#
# TEST_PRODUCTS = None
#
# to process all 200 products.
# ------------------------------------------------------------

TEST_PRODUCTS = None


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

Path("outputs").mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# BUILD STRICT PRODUCT DESCRIPTION PROMPT
# ============================================================

def build_prompt(product):

    return f"""
You are an e-commerce copywriter.

Your task is to write a short product description.

IMPORTANT RULES:

1. Use ONLY the information explicitly provided below.
2. Do NOT invent specifications.
3. Do NOT invent features.
4. Do NOT invent materials.
5. Do NOT invent battery life.
6. Do NOT invent connectivity types such as 4G, 5G,
   Bluetooth, Wi-Fi, etc.
7. Do NOT invent camera specifications.
8. Do NOT invent warranties or certifications.
9. Do NOT invent performance claims.
10. Do NOT assume accessories are included.
11. Do NOT assume technical capabilities.
12. Do NOT mention information that is not provided.
13. Do NOT mention the price unless it is useful.
14. Do NOT use exaggerated marketing claims.
15. Do NOT address the customer directly.
16. Return ONLY the description.
17. Do NOT include a title.
18. Do NOT include labels such as "Description:".
19. Keep the description between 50 and 70 words.

AVAILABLE PRODUCT INFORMATION:

Product name:
{product["product_name"]}

Category:
{product["category"]}

Price:
₹{product["price"]}

Because detailed specifications are not provided,
focus on the product's general purpose and category.

For example:

A laptop can be described as a computing device
suitable for general computing tasks.

Do NOT claim processor type, RAM, storage,
battery capacity, operating system, or connectivity
unless those details are explicitly provided.

Now write the product description.
""".strip()


# ============================================================
# CLEAN AI OUTPUT
# ============================================================

def clean_description(text):

    text = text.strip()

    # Remove common labels if the model adds them.
    unwanted_prefixes = [
        "Description:",
        "Product Description:",
        "Product description:"
    ]

    for prefix in unwanted_prefixes:

        if text.startswith(prefix):

            text = text[len(prefix):].strip()

    return text


# ============================================================
# GENERATE DESCRIPTION USING OLLAMA
# ============================================================

def generate_description(product):

    prompt = build_prompt(product)

    result = subprocess.run(

        [
            "ollama",
            "run",
            MODEL_NAME,
            prompt
        ],

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="replace"
    )


    if result.returncode != 0:

        error_message = result.stderr.strip()

        raise RuntimeError(
            error_message
            if error_message
            else "Ollama returned an unknown error."
        )


    description = clean_description(
        result.stdout
    )

    if not description:

        raise RuntimeError(
            "The AI model returned an empty description."
        )


    return description


# ============================================================
# LOAD PRODUCTS
# ============================================================

print("=" * 65)
print("LOCAL AI PRODUCT DESCRIPTION GENERATOR")
print("=" * 65)

print()

print(
    f"AI Model : {MODEL_NAME}"
)

print(
    f"Input    : {INPUT_FILE}"
)

print()


with open(

    INPUT_FILE,

    "r",

    newline="",

    encoding="utf-8"

) as file:

    reader = csv.DictReader(file)

    products = list(reader)


print(
    f"Products loaded : {len(products)}"
)


# ============================================================
# SELECT PRODUCTS
# ============================================================

if TEST_PRODUCTS is None:

    selected_products = products

else:

    selected_products = products[
        :TEST_PRODUCTS
    ]


print(
    f"Products for test : "
    f"{len(selected_products)}"
)


# ============================================================
# GENERATE DESCRIPTIONS
# ============================================================

results = []


for index, product in enumerate(

    selected_products,

    start=1

):

    print()

    print(
        f"[{index}/{len(selected_products)}] "
        f"Generating description for "
        f"Product {product['product_id']}..."
    )


    try:

        description = generate_description(
            product
        )


        results.append(

            {
                "product_id":
                    product["product_id"],

                "product_name":
                    product["product_name"],

                "category":
                    product["category"],

                "price":
                    product["price"],

                "generated_description":
                    description
            }

        )


        print(
            "Status: SUCCESS"
        )


    except Exception as error:

        print(
            "Status: FAILED"
        )

        print(
            f"Error: {error}"
        )


# ============================================================
# SAVE RESULTS
# ============================================================

with open(

    OUTPUT_FILE,

    "w",

    newline="",

    encoding="utf-8"

) as file:

    fieldnames = [

        "product_id",

        "product_name",

        "category",

        "price",

        "generated_description"

    ]


    writer = csv.DictWriter(

        file,

        fieldnames=fieldnames

    )


    writer.writeheader()

    writer.writerows(results)


# ============================================================
# SUMMARY
# ============================================================

print()

print("=" * 65)

print(
    "AI GENERATION TEST COMPLETED"
)

print("=" * 65)

print()

print(
    f"Descriptions generated : "
    f"{len(results)}"
)

print(
    f"Output file             : "
    f"{OUTPUT_FILE}"
)

print()

print(
    "AI provider : Ollama"
)

print(
    "Local model: Llama 3.2 3B"
)

print(
    "API key     : Not required"
)

print(
    "API payment : Not required"
)

print()

print("=" * 65)