import pandas as pd
import re

INPUT_FILE = "outputs/gpt_product_descriptions.csv"
OUTPUT_FILE = "outputs/gpt_product_descriptions_clean.csv"

df = pd.read_csv(INPUT_FILE)

def clean_text(text):
    text = str(text)

    # Fix currency encoding
    text = text.replace("â‚¹", "₹")

    # Remove common hallucinated/material/specification phrases
    replacements = [
        (r"Made from \[material\],?\s*", ""),
        (r"Made from various materials,?\s*", ""),
        (r"Made from a durable material,?\s*", ""),
        (r"Made from durable materials,?\s*", ""),
        (r"made from a specific material,?\s*", ""),
        (r"features a secure fastening system at the back\.?\s*", ""),
        (r"features a classic design that can be easily packed and carried\.?\s*", ""),
        (r"94-inch length", ""),
        (r"104 high-quality tennis balls", "tennis balls"),
        (r"high-quality ", ""),
        (r"high quality ", ""),
        (r"premium option", ""),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Remove excessive spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    return text


df["generated_description"] = df["generated_description"].apply(clean_text)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 60)
print("AI DESCRIPTION CLEANUP COMPLETED")
print("=" * 60)

print(f"Input rows  : {len(df)}")
print(f"Output rows : {len(df)}")
print(f"Output file : {OUTPUT_FILE}")

print("\nSample cleaned descriptions:")
for _, row in df.head(5).iterrows():
    print(f"\nProduct {row['product_id']}:")
    print(row["generated_description"])

print("\n" + "=" * 60)