import pandas as pd
import re

INPUT_FILE = "outputs/gpt_product_descriptions.csv"
OUTPUT_FILE = "outputs/gpt_product_descriptions_clean.csv"

df = pd.read_csv(INPUT_FILE)


def clean_text(text):
    text = str(text)

    # ---------------------------------------------------------
    # Fix currency / encoding artifacts
    # ---------------------------------------------------------
    text = text.replace("â‚¹", "₹")
    text = text.replace("Â₹", "₹")
    text = text.replace("�", "")

    # ---------------------------------------------------------
    # Remove common hallucinated/material/specification phrases
    # ---------------------------------------------------------
    replacements = [
        (r"Made from\s*\*{0,2}\[material\]\*{0,2},?\s*", ""),
        (r"Made from various materials,?\s*", ""),
        (r"Made from a durable material,?\s*", ""),
        (r"Made from durable materials,?\s*", ""),
        (r"made from a specific material,?\s*", ""),
        (
            r"features a secure fastening system at the back\.?\s*",
            ""
        ),
        (
            r"features a classic design that can be easily packed and carried\.?\s*",
            ""
        ),
        (r"94-inch length", ""),
        (r"104 high-quality tennis balls", "tennis balls"),
        (r"high-quality\s+", ""),
        (r"high quality\s+", ""),
        (r"premium option", ""),
    ]

    for pattern, replacement in replacements:
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    # ---------------------------------------------------------
    # Fix words accidentally joined during previous cleanup
    # ---------------------------------------------------------
    text = re.sub(r"\bfallsunder\b", "falls under", text, flags=re.IGNORECASE)
    text = re.sub(r"\btothe\b", "to the", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthecategory\b", "the category", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthego\b", "the go", text, flags=re.IGNORECASE)

    # ---------------------------------------------------------
    # Remove ANSI / terminal display artifacts
    # ---------------------------------------------------------
    text = re.sub(
        r"\x1B(?:[@-_]|\[[0-?]*[ -/]*[@-~])",
        "",
        text
    )

    # Remove corrupted ANSI remnants such as:
    # i1DK, Availab7DK, hea3DK, entert6DK
    text = re.sub(
        r"\b[A-Za-z]*\d+DK\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove standalone ANSI remnant "K"
    text = re.sub(
        r"\s+K\s+",
        " ",
        text
    )

    # Remove remaining control characters
    text = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        text
    )

    # ---------------------------------------------------------
    # Repair words damaged by encoding / terminal artifacts
    # ---------------------------------------------------------
    text = re.sub(r"\bItfalls\b", "It falls", text, flags=re.IGNORECASE)
    text = re.sub(r"\bItbelongs\b", "It belongs", text, flags=re.IGNORECASE)

    text = re.sub(r"\bAvailab\s+Available\b", "Available", text)

    text = re.sub(r"\bhea\s+health\b", "health", text)
    text = re.sub(r"\bentert\s+entertainment\b", "entertainment", text)

    text = re.sub(r"\bi\s+ideal\b", "ideal", text)

    text = re.sub(r"\bpodcasts,and\b", "podcasts, and", text)
    text = re.sub(r"\baswell\b", "as well", text)
    # ---------------------------------------------------------
    # Normalize whitespace
    # ---------------------------------------------------------
    text = re.sub(r"\s+", " ", text).strip()

    # ---------------------------------------------------------
    # Remove spaces before punctuation
    # ---------------------------------------------------------
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    # ---------------------------------------------------------
    # Fix repeated punctuation
    # ---------------------------------------------------------
    text = re.sub(r"\.{2,}", ".", text)

    return text.strip()


# Apply cleanup
df["generated_description"] = (
    df["generated_description"]
    .apply(clean_text)
)

# Save cleaned output
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