import os
import re
import html
import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ShopSmart",
    page_icon="🛒",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PRODUCT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "products.csv"
)

RECOMMENDATION_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "recommendations.csv"
)

AI_DESCRIPTION_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "gpt_product_descriptions_clean.csv"
)
SEARCH_LOG_FILE = os.path.join(
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
# CATEGORY IMAGE MAPPING
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
# SESSION STATE - CART
# ============================================================

# ============================================================
# USER-SPECIFIC CART
# ============================================================

if "user_carts" not in st.session_state:
    st.session_state["user_carts"] = {}

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN PAGE
       ===================================================== */

    .stApp {
        background: #f1f3f6;
        color: #212121;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }


    /* =====================================================
       HEADINGS
       ===================================================== */

    h1,
    h2,
    h3 {
        color: #172337 !important;
        font-weight: 750 !important;
    }


    /* =====================================================
    PRODUCT CARD VISUALS
    ===================================================== */

    .product-card-image {
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 8px;
    }

    .product-card-title {
        font-size: 17px;
        font-weight: 750;
        color: #172337;
        line-height: 1.35;
        min-height: 48px;
        margin: 6px 0 8px 0;
    }

    .category-badge {
        display: inline-block;
        background: #e8f1ff;
        color: #2874f0;
        padding: 4px 10px;
        border-radius: 14px;
        font-size: 12px;
        font-weight: 650;
        margin-bottom: 8px;
    }

    .product-price {
        color: #1b5e20;
        font-size: 23px;
        font-weight: 800;
        margin: 6px 0 10px 0;
    }

    .recommendation-banner {
        background: #ffffff;
        border-left: 4px solid #2874f0;
        padding: 12px 15px;
        border-radius: 8px;
        color: #555555;
        font-size: 14px;
        margin-bottom: 15px;
        box-shadow: 0 2px 7px rgba(0,0,0,0.05);
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        width: 100%;

        background: #ff9f00;
        color: #212121;

        border: none;
        border-radius: 8px;

        font-weight: 700;

        padding: 0.65rem 1rem;

        transition: all 0.2s ease;

        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.10);
    }

    .stButton > button:hover {
        background: #ffc200;
        color: #212121;

        transform: translateY(-2px);

        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }

    .stButton > button:active {
        transform: translateY(0);
    }


    /* =====================================================
       SELECT BOX
       ===================================================== */

    div[data-baseweb="select"] > div {
        background: #ffffff;

        border: 1px solid #d0d0d0;

        border-radius: 8px;
    }


    /* =====================================================
       METRICS
       ===================================================== */

    div[data-testid="stMetric"] {
        background: #ffffff;

        border: 1px solid #e0e0e0;

        border-radius: 10px;

        padding: 1rem;
    }

    div[data-testid="stMetricValue"] {
        color: #172337 !important;
        font-weight: 800;
    }

    div[data-testid="stMetricLabel"] {
        color: #757575 !important;
    }


    /* =====================================================
       AI DESCRIPTION
       ===================================================== */

    .ai-description {
        background: #ffffff;

        border-left: 5px solid #2874f0;

        padding: 18px;

        border-radius: 10px;

        line-height: 1.7;

        color: #424242;

        margin-top: 10px;

        box-shadow:
            0 2px 8px rgba(0, 0, 0, 0.06);
    }

        /* =====================================================
       HIDE STREAMLIT AUTO PAGE NAVIGATION
       ===================================================== */

    [data-testid="stSidebarNav"] {
        display: none;
    }


    /* =====================================================
       CART SIDEBAR
       ===================================================== */

    /* Cart sidebar styling */
    [data-testid="stSidebar"] {
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 1.3rem;
        font-weight: 700;
    }

    [data-testid="stSidebar"] .stButton > button {
        border-radius: 8px;
    }
    .cart-item {
        background: #f8f9fa;

        border: 1px solid #e0e0e0;

        border-radius: 10px;

        padding: 10px;

        margin-bottom: 8px;
    }

    .cart-total {
        background: #172337;

        color: #ffffff;

        padding: 14px;

        border-radius: 10px;

        font-size: 18px;

        font-weight: 800;

        margin-top: 12px;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .shopsmart-footer {
        text-align: center;

        color: #757575;

        font-size: 13px;

        margin-top: 35px;

        padding: 15px;
    }


    /* =====================================================
       DIVIDER
       ===================================================== */

    hr {
        border-color: #dddddd;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    products = pd.read_csv(
        PRODUCT_FILE,
        encoding="utf-8-sig"
    )

    recommendations = pd.read_csv(
        RECOMMENDATION_FILE,
        encoding="utf-8-sig"
    )

    ai_descriptions = pd.read_csv(
        AI_DESCRIPTION_FILE,
        encoding="utf-8-sig"
    )

except Exception as error:

    st.error(
        f"Unable to load project data: {error}"
    )

    st.stop()


# ============================================================
# DATA TYPE CLEANUP
# ============================================================

products["product_id"] = (
    pd.to_numeric(
        products["product_id"],
        errors="coerce"
    )
    .astype("Int64")
)

recommendations["user_id"] = (
    pd.to_numeric(
        recommendations["user_id"],
        errors="coerce"
    )
    .astype("Int64")
)

recommendations["product_id"] = (
    pd.to_numeric(
        recommendations["product_id"],
        errors="coerce"
    )
    .astype("Int64")
)

ai_descriptions["product_id"] = (
    pd.to_numeric(
        ai_descriptions["product_id"],
        errors="coerce"
    )
    .astype("Int64")
)


# ============================================================
# AI DESCRIPTION CLEANING
# ============================================================

ANSI_ESCAPE = re.compile(
    r"\x1B(?:[@-_]|\[[0-?]*[ -/]*[@-~])"
)


def clean_display_text(text):

    if pd.isna(text):
        return ""

    text = str(text)

    # Remove ANSI terminal escape sequences
    text = ANSI_ESCAPE.sub(
        "",
        text
    )

    # Remove ESC characters
    text = text.replace(
        "\x1b",
        ""
    )

    # Remove control characters
    text = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        text
    )

    # Fix encoding problems
    text = text.replace(
        "â‚¹",
        "₹"
    )

    text = text.replace(
        "Â₹",
        "₹"
    )

    # Remove replacement character
    text = text.replace(
        "�",
        ""
    )

    # Remove known terminal/model artifacts
    text = re.sub(
        r"[A-Za-z]*\d+DK",
        "",
        text
    )

    text = re.sub(
        r"\b\d+K\b",
        "",
        text
    )

    # Remove standalone accidental K
    text = re.sub(
        r"\sK\s",
        " ",
        text
    )

    # Remove excessive spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()
# ============================================================
# SEARCH INTERACTION LOGGING
# ============================================================

def log_search(user_id, query):

    query = query.strip()

    if not query:
        return

    new_record = pd.DataFrame([
        {
            "user_id": int(user_id),
            "event_type": "search",
            "query": query,
            "timestamp": pd.Timestamp.now()
        }
    ])

    if os.path.exists(SEARCH_LOG_FILE):

        existing_records = pd.read_csv(
            SEARCH_LOG_FILE,
            encoding="utf-8-sig"
        )

        updated_records = pd.concat(
            [
                existing_records,
                new_record
            ],
            ignore_index=True
        )

    else:

        updated_records = new_record

    updated_records.to_csv(
        SEARCH_LOG_FILE,
        index=False,
        encoding="utf-8-sig"
    )

# ============================================================
# SHOPSMART HEADER
# ============================================================

st.html(
    """
    <div style="
        background:linear-gradient(135deg,#172337,#243b55);
        padding:24px 30px;
        border-radius:14px;
        display:flex;
        align-items:center;
        justify-content:space-between;
        box-shadow:0 5px 16px rgba(0,0,0,0.16);
        margin-bottom:12px;
    ">

        <div>

            <div style="
                color:#ffffff;
                font-size:34px;
                font-weight:850;
                letter-spacing:0.2px;
            ">
                🛒 ShopSmart
            </div>

            <div style="
                color:#cfd8e3;
                font-size:14px;
                margin-top:5px;
            ">
                Personalized shopping powered by data & AI
            </div>

        </div>

        <div style="
            text-align:right;
        ">

            <div style="
                color:#ffffff;
                font-size:15px;
                font-weight:700;
            ">
                Smart Recommendations
            </div>

            <div style="
                color:#ffb300;
                font-size:13px;
                margin-top:5px;
            ">
                SparkML • AI • Real-Time Behavior
            </div>

        </div>

    </div>
    """
)


# ============================================================
# BLUE SUBTITLE
# ============================================================

st.html(
    """
    <div style="
        background:#2874f0;
        color:#ffffff;
        padding:11px 18px;
        border-radius:8px;
        font-size:16px;
        font-weight:600;
        margin-bottom:10px;
        box-shadow:0 2px 8px rgba(40,116,240,0.25);
    ">
        Personalized recommendations using SparkML ALS, AI & real-time user behavior
    </div>
    """
)
# ============================================================
# USER SELECTION
# ============================================================

st.html(
    """
    <div style="
        color:#172337;
        font-size:21px;
        font-weight:800;
        margin-top:8px;
        margin-bottom:4px;
    ">
        👤 Personalize Your Shopping
    </div>

    <div style="
        color:#666666;
        font-size:14px;
        margin-bottom:10px;
    ">
        Select a user profile to view personalized recommendations.
    </div>
    """
)

available_users = sorted(
    recommendations["user_id"]
    .dropna()
    .unique()
    .tolist()
)


# ============================================================
# PERSISTENT USER SELECTION
# ============================================================

if "selected_user" not in st.session_state:

    st.session_state["selected_user"] = available_users[0]


previous_user = st.session_state["selected_user"]


selected_user = st.selectbox(
    "Customer Profile",
    available_users,
    index=available_users.index(
        st.session_state["selected_user"]
    ),
    format_func=lambda user: f"User {user}"
)


# ============================================================
# HANDLE USER CHANGE
# ============================================================

if selected_user != previous_user:

    st.session_state["selected_user"] = selected_user

    st.session_state.pop(
        "active_search",
        None
    )

    st.session_state.pop(
        "selected_product_id",
        None
    )

    st.session_state.pop(
        "search_query",
        None
    )

    st.rerun()


st.session_state["selected_user"] = selected_user


# ============================================================
# USER-SPECIFIC CART
# ============================================================

if selected_user not in st.session_state["user_carts"]:

    st.session_state["user_carts"][selected_user] = []


cart = st.session_state["user_carts"][selected_user]


# ============================================================
# CART COUNTER
# ============================================================

cart_count = len(
    st.session_state["user_carts"][selected_user]
)

st.markdown(
    f"""
    <div style="
        display:flex;
        justify-content:flex-end;
        margin:10px 0 15px 0;
    ">
        <div style="
            background:#ffffff;
            border:1px solid #e0e0e0;
            border-radius:20px;
            padding:7px 16px;
            color:#172337;
            font-weight:700;
            font-size:14px;
            box-shadow:0 2px 6px rgba(0,0,0,0.08);
        ">
            🛒 {cart_count} item(s) in cart
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ============================================================
# CART SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🛒 Your Cart")

    cart_items = st.session_state["user_carts"][selected_user]

    # --------------------------------------------------------
    # EMPTY CART
    # --------------------------------------------------------

    if not cart_items:

        st.info(
            "Your cart is empty."
        )

        st.write(
            "Add products from the recommendation section."
        )

    # --------------------------------------------------------
    # CART WITH PRODUCTS
    # --------------------------------------------------------

    else:

        total_amount = sum(
            float(item["price"])
            for item in cart_items
        )

        st.caption(
            f"{len(cart_items)} item(s) in your cart"
        )

        # ----------------------------------------------------
        # CART ITEMS
        # ----------------------------------------------------

        for item in cart_items:

            st.html(
                f"""
                <div style="
                    background:#f8f9fa;
                    border:1px solid #e0e0e0;
                    border-radius:9px;
                    padding:10px 12px;
                    margin-bottom:8px;
                ">

                    <div style="
                        color:#172337;
                        font-size:14px;
                        font-weight:750;
                        line-height:1.35;
                    ">
                        {html.escape(str(item['product_name']))}
                    </div>

                    <div style="
                        color:#2874f0;
                        font-size:12px;
                        margin-top:4px;
                    ">
                        {html.escape(str(item['category']))}
                    </div>

                    <div style="
                        color:#1b5e20;
                        font-size:16px;
                        font-weight:800;
                        margin-top:6px;
                    ">
                        ₹{float(item['price']):,.2f}
                    </div>

                </div>
                """
            )

            if st.button(
                "Remove",
                key=f"remove_cart_{item['product_id']}"
            ):

                st.session_state["user_carts"][selected_user] = [
                    cart_product
                    for cart_product in st.session_state["user_carts"][selected_user]
                    if cart_product["product_id"]
                    != item["product_id"]
]

                st.rerun()

            st.divider()

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        st.subheader(
            f"Total: ₹{total_amount:,.2f}"
        )

        # ----------------------------------------------------
        # CHECKOUT
        # ----------------------------------------------------

        if st.button(
            "⚡ Proceed to Checkout",
            key="checkout_button"
        ):

            # Clear any previous Buy Now product
            st.session_state.pop(
                "buy_now_product",
                None
            )

            # Open checkout page
            st.switch_page(
                "pages/checkout.py"
            )


    
# ============================================================
# PRODUCT SEARCH
# ============================================================


st.subheader("🔎 Find Your Product")

st.caption(
    "Search by product name or category to discover products."
)

search_query = st.text_input(
    "Search",
    placeholder="Try: Java, Books, Electronics...",
    label_visibility="collapsed"
)

search_button = st.button(
    "🔎 Search Products",
    key="search_button",
    use_container_width=True
)

if search_button and search_query.strip():

    search_query = search_query.strip().lower()

    log_search(
        selected_user,
        search_query
    )

    st.session_state["active_search"] = search_query
search_query = st.session_state.get(
    "active_search",
    ""
)
# ============================================================
# SEARCH RESULTS
# ============================================================

if search_query:

    search_results = products[
        products["product_name"]
        .str.lower()
        .str.contains(
            search_query,
            na=False
        )
        |
        products["category"]
        .str.lower()
        .str.contains(
            search_query,
            na=False
        )
    ].copy()

    st.divider()

    st.subheader(
        f"🔎 Results for “{search_query}”"
    )

    st.caption(
        "Products matching your search"
    )
    if search_results.empty:

        st.warning(
            "No products found."
        )

    else:

        st.write(
            f"{len(search_results)} product(s) found."
        )

                # ====================================================
        # DISPLAY ALL SEARCH RESULTS
        # ====================================================

        for start in range(
            0,
            len(search_results),
            5
        ):

            row_products = search_results.iloc[
                start:start + 5
            ]

            search_columns = st.columns(5)

            for column, (_, product) in zip(
                search_columns,
                row_products.iterrows()
            ):

                with column:

                    category = str(
                        product["category"]
                    )

                    image_path = CATEGORY_IMAGES.get(
                        category
                    )

                    if (
                        image_path
                        and os.path.exists(image_path)
                    ):

                        st.image(
                            image_path,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "Product image unavailable"
                        )

                    st.markdown(
                        f"### {product['product_name']}"
                    )

                    st.markdown(
                        f"""
                        <div style="
                            display:inline-block;
                            background:#e8f1ff;
                            color:#2874f0;
                            padding:4px 10px;
                            border-radius:14px;
                            font-size:12px;
                            font-weight:600;
                            margin-bottom:8px;
                        ">
                            {product['category']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"""
                        <div style="
                            color:#1b5e20;
                            font-size:22px;
                            font-weight:800;
                            margin:6px 0 12px 0;
                        ">
                            ₹{float(product['price']):,.0f}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # ====================================================
                    # VIEW PRODUCT
                    # ====================================================

                    if st.button(
                        "View Product",
                        key=f"view_{product['product_id']}"
                    ):

                        # Record product click
                        new_view = pd.DataFrame([{
                            "user_id": int(selected_user),
                            "product_id": int(product["product_id"]),
                            "event_type": "click",
                            "timestamp": pd.Timestamp.now()
                        }])

                        if os.path.exists(SEARCH_LOG_FILE):

                            existing_views = pd.read_csv(
                                SEARCH_LOG_FILE,
                                encoding="utf-8-sig"
                            )

                            updated_views = pd.concat(
                                [
                                    existing_views,
                                    new_view
                                ],
                                ignore_index=True
                            )

                        else:

                            updated_views = new_view

                        updated_views.to_csv(
                            SEARCH_LOG_FILE,
                            index=False,
                            encoding="utf-8-sig"
                        )

                        # Store selected product
                        st.session_state["selected_product_id"] = int(
                            product["product_id"]
                        )

                        # Open dedicated product page
                        st.switch_page(
                            "pages/product.py"
                        )

# ============================================================
# CATEGORY-AWARE HYBRID RECOMMENDATIONS
# ============================================================

# Start with all products
user_recommendations = products[
    [
        "product_id",
        "product_name",
        "category",
        "price"
    ]
].copy()


# ============================================================
# GET ALS SCORES
# ============================================================

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


# Normalize ALS score
max_als_score = user_recommendations["recommendation_score"].max()

if max_als_score > 0:
    user_recommendations["als_score"] = (
        user_recommendations["recommendation_score"]
        / max_als_score
    )
else:
    user_recommendations["als_score"] = 0.0


# ============================================================
# READ USER INTERACTION HISTORY
# ============================================================

user_interactions = pd.DataFrame()

if os.path.exists(SEARCH_LOG_FILE):

    all_interactions = pd.read_csv(
        SEARCH_LOG_FILE,
        encoding="utf-8-sig"
    )

    user_interactions = all_interactions[
        all_interactions["user_id"] == selected_user
    ].copy()


# ============================================================
# INTERACTION WEIGHTS
# ============================================================

INTERACTION_WEIGHTS = {
    "search": 1,
    "click": 2,
    "cart": 3,
    "purchase": 5
}


# ============================================================
# INITIALIZE BEHAVIOR SCORE
# ============================================================

user_recommendations["behavior_score"] = 0.0

category_interest = {}

recent_queries = []


# ============================================================
# PROCESS USER INTERACTIONS
# ============================================================

if not user_interactions.empty:

    user_interactions["event_type"] = (
        user_interactions["event_type"]
        .astype(str)
        .str.lower()
    )

    # --------------------------------------------------------
    # RECENT SEARCHES
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # PROCESS EACH INTERACTION
    # --------------------------------------------------------

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


        # ====================================================
        # SEARCH INTERACTION
        # ====================================================

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

                # Search → moderate influence
                user_recommendations.loc[
                    name_match,
                    "behavior_score"
                ] += 0.08 * weight

                user_recommendations.loc[
                    category_match,
                    "behavior_score"
                ] += 0.04 * weight


        # ====================================================
        # PRODUCT INTERACTIONS
        # CLICK / CART / PURCHASE
        # ====================================================

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
                ] == interaction_product_id
            )

            user_recommendations.loc[
                direct_match,
                "behavior_score"
            ] += 0.15 * weight


            # ------------------------------------------------
            # Category interest
            # ------------------------------------------------

            matched_product = products[
                products["product_id"]
                == interaction_product_id
            ]

            if not matched_product.empty:

                interacted_category = str(
                    matched_product.iloc[0][
                        "category"
                    ]
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

                # Give related products a boost
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


# ============================================================
# CATEGORY INTEREST FROM SEARCHES
# ============================================================

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


# ============================================================
# NORMALIZE BEHAVIOR SCORE
# ============================================================

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


# ============================================================
# FINAL HYBRID SCORE
# ============================================================

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


# ============================================================
# CREATE CATEGORY MIX
# ============================================================

if category_interest:

    # Keep the strongest categories
    category_interest = dict(
        sorted(
            category_interest.items(),
            key=lambda item: item[1],
            reverse=True
        )[:5]
    )

    total_interest = sum(category_interest.values())

    # Initial allocation of 5 recommendation slots
    category_slots = {}

    for category, interest in category_interest.items():

        category_slots[category] = int(
            (interest / total_interest) * 5
        )

    # Make sure every detected category gets at least 1 slot
    for category in category_slots:

        if category_slots[category] == 0:
            category_slots[category] = 1

    # If we have more than 5 slots, remove from weakest categories
    while sum(category_slots.values()) > 5:

        weakest_category = min(
            category_slots,
            key=category_interest.get
        )

        if category_slots[weakest_category] > 1:
            category_slots[weakest_category] -= 1
        else:
            break

    # If fewer than 5 slots, give extras to strongest categories
    while sum(category_slots.values()) < 5:

        strongest_category = max(
            category_interest,
            key=category_interest.get
        )

        category_slots[strongest_category] += 1


    # ========================================================
    # SELECT PRODUCTS FROM EACH CATEGORY
    # ========================================================

    selected_products = []

    for category, slots in category_slots.items():

        category_products = user_recommendations[
            user_recommendations["category"] == category
        ].copy()

        category_products = (
            category_products
            .sort_values(
                "final_score",
                ascending=False
            )
            .head(slots)
        )

        selected_products.append(category_products)


    if selected_products:

        user_recommendations = pd.concat(
            selected_products,
            ignore_index=True
        )

    # Final ordering
    user_recommendations = (
        user_recommendations
        .sort_values(
            "final_score",
            ascending=False
        )
        .head(5)
    )

else:

    # No search history → normal ALS recommendations
    user_recommendations = (
        user_recommendations
        .sort_values(
            "final_score",
            ascending=False
        )
        .head(5)
    )


# ============================================================
# PREPARE RECOMMENDED PRODUCTS
# ============================================================

recommended_products = user_recommendations.copy()


# ============================================================
# RECOMMENDATION SECTION
# ============================================================

st.divider()

st.subheader(
    f"🎯 Personalized Recommendations for User {selected_user}"
)

st.html(
    """
    <div class="recommendation-banner">
        🤖 Personalized using
        <b>SparkML ALS</b> collaborative filtering
        and <b>real-time user behavior</b>.
    </div>
    """
)


# ============================================================
# PRODUCT CARDS
# ============================================================

columns = st.columns(5)


for column, (_, product) in zip(
    columns,
    recommended_products.iterrows()
):

    with column:

        # ----------------------------------------------------
        # PRODUCT IMAGE
        # ----------------------------------------------------

        category = str(
            product["category"]
        )

        image_path = CATEGORY_IMAGES.get(
            category
        )

        if (
            image_path
            and os.path.exists(image_path)
        ):

            st.image(
                image_path,
                use_container_width=True
            )

        else:

            st.info(
                "Product image unavailable"
            )


        # ----------------------------------------------------
        # PRODUCT NAME
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                font-size:17px;
                font-weight:750;
                color:#172337;
                line-height:1.35;
                min-height:48px;
                margin:6px 0 8px 0;
            ">
                {product['product_name']}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                display:inline-block;
                background:#e8f1ff;
                color:#2874f0;
                padding:4px 10px;
                border-radius:14px;
                font-size:12px;
                font-weight:600;
                margin-bottom:8px;
            ">
                {product['category']}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                color:#1b5e20;
                font-size:24px;
                font-weight:800;
                margin:6px 0;
            ">
                ₹{float(product['price']):,.0f}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # RECOMMENDATION SCORE
        # ----------------------------------------------------

        score = float(product["final_score"])

        if score >= 0.75:
            badge = "🔥 Highly Recommended"
        elif score >= 0.50:
            badge = "⭐ Recommended"
        else:
            badge = "👍 Suggested"

        st.markdown(
            f"""
            <div style="
                background:#e8f5e9;
                color:#1b5e20;
                padding:6px 10px;
                border-radius:8px;
                font-size:13px;
                font-weight:700;
                text-align:center;
                margin:8px 0;
            ">
                {badge}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(min(score, 1.0))

        st.caption(f"Match Score: {score:.2f}")


        # ----------------------------------------------------
        # VIEW PRODUCT BUTTON
        # ----------------------------------------------------

        if st.button(
            "View Product",
            key=f"recommended_view_{product['product_id']}"
        ):
            # Record product view
            new_view = pd.DataFrame([{
                "user_id": int(selected_user),
                "product_id": int(product["product_id"]),
                "event_type": "click",
                "timestamp": pd.Timestamp.now()
            }])

            if os.path.exists(SEARCH_LOG_FILE):
                existing_views = pd.read_csv(
                    SEARCH_LOG_FILE,
                    encoding="utf-8-sig"
                )
                updated_views = pd.concat(
                    [existing_views, new_view],
                    ignore_index=True
                )
            else:
                updated_views = new_view

            updated_views.to_csv(
                SEARCH_LOG_FILE,
                index=False,
                encoding="utf-8-sig"
            )

            # Open product details
            # Open dedicated product page
            st.session_state["selected_product_id"] = int(
                product["product_id"]
            )

            st.switch_page(
                "pages/product.py"
            )





# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div style="
        text-align:center;
        color:#757575;
        font-size:13px;
        margin-top:35px;
        padding:15px;
    ">
        ShopSmart • E-Commerce Recommendation Engine
        <br>
        SparkML ALS • Local LLM • AWS S3
    </div>
    """
)