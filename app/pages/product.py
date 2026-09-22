import os
import re
import html
import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ShopSmart Product",
    page_icon="🛍️",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

PRODUCTS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "products.csv"
)

AI_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "gpt_product_descriptions_clean.csv"
)
USER_SEARCHES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "user_searches.csv"
)

IMAGE_DIR = os.path.join(
    BASE_DIR,
    "app",
    "assets",
    "products"
)


# ============================================================
# CATEGORY IMAGES
# ============================================================

CATEGORY_IMAGES = {

    "Electronics": os.path.join(
        IMAGE_DIR,
        "electronics.png"
    ),

    "Fashion": os.path.join(
        IMAGE_DIR,
        "fashion.png"
    ),

    "Books": os.path.join(
        IMAGE_DIR,
        "books.png"
    ),

    "Home": os.path.join(
        IMAGE_DIR,
        "home.png"
    ),

    "Sports": os.path.join(
        IMAGE_DIR,
        "sports.png"
    ),

    "Beauty": os.path.join(
        IMAGE_DIR,
        "beauty.png"
    )
}


# ============================================================
# USER-SPECIFIC CART INITIALIZATION
# ============================================================

if "user_carts" not in st.session_state:

    st.session_state["user_carts"] = {}


# ============================================================
# GET SELECTED USER
# ============================================================

selected_user = st.session_state.get(
    "selected_user"
)

if selected_user is None:

    st.error(
        "No user selected. Please return to the shop."
    )

    if st.button("← Back to Shop"):

        st.switch_page(
            "app.py"
        )

    st.stop()


# Create cart for this user if needed
if selected_user not in st.session_state["user_carts"]:

    st.session_state["user_carts"][selected_user] = []


# ============================================================
# LOAD DATA
# ============================================================

products = pd.read_csv(
    PRODUCTS_FILE,
    encoding="utf-8-sig"
)

ai_descriptions = pd.read_csv(
    AI_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# GET SELECTED PRODUCT
# ============================================================

product_id = st.session_state.get(
    "selected_product_id"
)

if product_id is None:

    st.error(
        "Product not found."
    )

    if st.button("← Back to Shop"):

        st.switch_page(
            "app.py"
        )

    st.stop()


product_id = int(product_id)


# ============================================================
# FIND PRODUCT
# ============================================================

product = products[
    products["product_id"] == product_id
]

if product.empty:

    st.error(
        "Product not found."
    )

    if st.button("← Back to Shop"):

        st.switch_page(
            "app.py"
        )

    st.stop()


product = product.iloc[0]


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .product-title {
        font-size: 36px;
        font-weight: 800;
        color: #172337;
        line-height: 1.2;
        margin-bottom: 12px;
    }

    .product-category {
        display: inline-block;
        background: #e8f1ff;
        color: #2874f0;
        padding: 5px 12px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .product-price {
        color: #1b5e20;
        font-size: 32px;
        font-weight: 800;
        margin-top: 14px;
        margin-bottom: 20px;
    }

    .ai-description {
        background: #ffffff;
        border-left: 5px solid #2874f0;
        padding: 18px 20px;
        border-radius: 10px;
        margin-top: 12px;
        line-height: 1.7;
        color: #424242;
        font-size: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    /* =====================================================
    SHOPPING ACTION BUTTONS
    ===================================================== */

    .stButton > button {
        width: 100%;
        min-height: 48px;

        border-radius: 10px;
        border: 1px solid #d9d9d9;

        font-size: 15px;
        font-weight: 700;

        background: #ffffff;
        color: #172337;

        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #f5f7fa;
        border-color: #2874f0;
        color: #2874f0;

        transform: translateY(-2px);

        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.10);
    }
    /* =====================================================
    PRODUCT IMAGE CARD
    ===================================================== */

    .product-image-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    }
    

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BACK BUTTON
# ============================================================

if st.button(
    "← Back to Shop",
    use_container_width=True
):

    st.switch_page(
        "app.py"
    )


st.divider()


# ============================================================
# PRODUCT DISPLAY
# ============================================================

image_path = CATEGORY_IMAGES.get(
    str(product["category"])
)

image_column, details_column = st.columns(
    [1, 1]
)


# ============================================================
# PRODUCT IMAGE
# ============================================================

with image_column:

    if (
        image_path
        and os.path.exists(image_path)
    ):

        st.markdown(
            '<div class="product-image-card">',
            unsafe_allow_html=True
        )

        st.image(
            image_path,
            use_container_width=True,
            output_format="PNG"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )
    else:

        st.info(
            "Product image unavailable"
        )

st.markdown(
    """
    <div style="
        color:#172337;
        font-size:18px;
        font-weight:700;
        margin-bottom:12px;
    ">
        Product Details
    </div>
    """,
    unsafe_allow_html=True
)
# ============================================================
# PRODUCT INFORMATION
# ============================================================

with details_column:

    st.markdown(
        f"""
        <div class="product-title">
            {html.escape(str(product["product_name"]))}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="product-category">
            {html.escape(str(product["category"]))}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="product-price">
            ₹{float(product["price"]):,.2f}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="
            display:inline-block;
            background:#e8f5e9;
            color:#1b5e20;
            padding:6px 12px;
            border-radius:16px;
            font-size:13px;
            font-weight:700;
            margin-bottom:15px;
        ">
            ✓ In Stock
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# AI PRODUCT DESCRIPTION
# ============================================================

description = ai_descriptions[
    ai_descriptions["product_id"] == product_id
]


if not description.empty:

    description_columns = [
        column
        for column in description.columns
        if "description" in column.lower()
    ]

    if description_columns:

        ai_text = str(
            description.iloc[0][
                description_columns[0]
            ]
        )

        # ----------------------------------------------------
        # CLEAN TERMINAL / ENCODING ARTIFACTS
        # ----------------------------------------------------

        ANSI_ESCAPE = re.compile(
            r"\x1B(?:[@-_]|\[[0-?]*[ -/]*[@-~])"
        )

        # Remove ANSI terminal sequences
        ai_text = ANSI_ESCAPE.sub("", ai_text)

        # Remove ESC/control characters
        ai_text = ai_text.replace("\x1b", "")

        ai_text = re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
            "",
            ai_text
        )

        # ----------------------------------------------------
        # FIX COMMON UTF-8 / WINDOWS ENCODING ARTIFACTS
        # ----------------------------------------------------

        encoding_replacements = {
            "â‚¹": "₹",
            "Â₹": "₹",
            "â€™": "'",
            "â€œ": '"',
            "â€": '"',
            "â€“": "–",
            "â€”": "—",
            "â€¦": "...",
            "Â": "",
            "�": ""
        }

        for bad_text, correct_text in encoding_replacements.items():

            ai_text = ai_text.replace(
                bad_text,
                correct_text
            )
        # ----------------------------------------------------
        # REMOVE LLM-GENERATED ARTIFACTS
        # ----------------------------------------------------

        # Remove corrupted fragments such as:
        # in2DK, thei4DK, belon5DK, use3DK, etc.
        ai_text = re.sub(
            r"\b[A-Za-z]*\d+DK\b",
            "",
            ai_text
        )

        # Remove artifacts such as ₹103DK
        ai_text = re.sub(
            r"₹?\d+DK\b",
            "",
            ai_text
        )

        # Remove standalone accidental K tokens
        ai_text = re.sub(
            r"\bK\b",
            "",
            ai_text
        )

        # Clean spacing created after removing artifacts
        ai_text = re.sub(
            r"\s+",
            " ",
            ai_text
        ).strip()

        # Try to repair remaining UTF-8 mojibake
        try:

            repaired_text = ai_text.encode(
                "latin1"
            ).decode(
                "utf-8"
            )

            # Only use repaired text if it looks valid
            if "�" not in repaired_text:

                ai_text = repaired_text

        except (UnicodeEncodeError, UnicodeDecodeError):

            pass

        # Remove accidental extra spaces
        ai_text = re.sub(
            r"\s{2,}",
            " ",
            ai_text
        ).strip()

    else:

        ai_text = (
            "AI product description unavailable."
        )

    st.markdown(
        "### 🤖 AI Product Description"
    )
    st.caption(
        "Generated using a local Llama 3.2 model via Ollama."
    )

    st.markdown(
        f"""
        <div class="ai-description">
            {html.escape(ai_text)}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="
            background:#f8f9fa;
            border:1px solid #e0e0e0;
            padding:12px 15px;
            border-radius:9px;
            margin-top:12px;
            color:#666666;
            font-size:13px;
        ">
            💡 Product information is enhanced using a local AI model
            and integrated with the ShopSmart recommendation system.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SHOPPING ACTIONS
# ============================================================

st.write("")

st.markdown(
    """
    <div style="
        background:#172337;
        color:#ffffff;
        padding:12px 16px;
        border-radius:10px;
        font-size:18px;
        font-weight:700;
        margin:22px 0 12px 0;
    ">
        🛒 Shopping Actions
    </div>
    """,
    unsafe_allow_html=True
)

action_col1, action_col2 = st.columns(2)


# ============================================================
# ADD TO CART
# ============================================================

with action_col1:

    if st.button(
        "🛒 Add to Cart",
        use_container_width=True
    ):

        user_cart = (
            st.session_state["user_carts"]
            [selected_user]
        )

        # Check whether product is already present
        already_in_cart = any(
            item["product_id"] == product_id
            for item in user_cart
        )

        if already_in_cart:

            st.warning(
                "This product is already in your cart."
            )

        else:

            st.session_state[
                "user_carts"
            ][
                selected_user
            ].append(
                {
                    "product_id": product_id,

                    "product_name": str(
                        product["product_name"]
                    ),

                    "category": str(
                        product["category"]
                    ),

                    "price": float(
                        product["price"]
                    )
                }
            )

                        # Record cart interaction
            new_cart_event = pd.DataFrame([{
                "user_id": int(selected_user),
                "event_type": "cart",
                "query": str(product["product_name"]),
                "timestamp": pd.Timestamp.now(),
                "product_id": int(product_id)
            }])

            if os.path.exists(USER_SEARCHES_FILE):

                new_cart_event.to_csv(
                    USER_SEARCHES_FILE,
                    mode="a",
                    header=False,
                    index=False,
                    encoding="utf-8-sig"
                )

            else:

                new_cart_event.to_csv(
                    USER_SEARCHES_FILE,
                    mode="w",
                    header=True,
                    index=False,
                    encoding="utf-8-sig"
                )

            st.success(
                "Product added to your cart!"
            )
            


# ============================================================
# BUY NOW
# ============================================================

with action_col2:

    if st.button(
        "⚡ Buy Now",
        use_container_width=True
    ):

        st.session_state[
            "buy_now_product"
        ] = {

            "product_id": product_id,

            "product_name": str(
                product["product_name"]
            ),

            "category": str(
                product["category"]
            ),

            "price": float(
                product["price"]
            )
        }

        st.switch_page(
            "pages/checkout.py"
        )