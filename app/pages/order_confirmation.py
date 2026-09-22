import streamlit as st
import html


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Order Confirmed",
    page_icon="✅",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html("""
<style>

.confirmation-wrapper {
    text-align: center;
    padding: 25px 20px 10px 20px;
}

.success-icon {
    font-size: 62px;
    margin-bottom: 5px;
}

.success-title {
    color: #172337;
    font-size: 36px;
    font-weight: 850;
    margin-bottom: 8px;
}

.success-subtitle {
    color: #666666;
    font-size: 15px;
}

.order-id {
    display: inline-block;
    background: #e8f5e9;
    color: #1b5e20;
    padding: 8px 15px;
    border-radius: 18px;
    font-size: 14px;
    font-weight: 750;
    margin-top: 15px;
}

.section-title {
    color: #172337;
    font-size: 21px;
    font-weight: 800;
    margin-bottom: 14px;
}

.info-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}

.detail-label {
    color: #777777;
    font-size: 13px;
    margin-bottom: 5px;
}

.detail-value {
    color: #172337;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 18px;
}

.total-label {
    color: #777777;
    font-size: 13px;
    margin-bottom: 4px;
}

.total-value {
    color: #1b5e20;
    font-size: 29px;
    font-weight: 850;
}

.product-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: 0 2px 7px rgba(0,0,0,0.04);
}

.product-name {
    color: #172337;
    font-size: 16px;
    font-weight: 750;
    margin-bottom: 7px;
}

.category-badge {
    display: inline-block;
    background: #e8f1ff;
    color: #2874f0;
    padding: 4px 10px;
    border-radius: 14px;
    font-size: 12px;
    font-weight: 700;
}

.product-price {
    color: #1b5e20;
    font-size: 19px;
    font-weight: 800;
    text-align: right;
}

.delivery-card {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-left: 4px solid #2874f0;
    border-radius: 9px;
    padding: 15px 17px;
    color: #555555;
    line-height: 1.6;
}

.success-note {
    background: #e8f5e9;
    border: 1px solid #c8e6c9;
    border-radius: 10px;
    padding: 14px 16px;
    color: #2e5d32;
    font-size: 14px;
    margin-top: 15px;
}

</style>
""")


# ============================================================
# GET LAST ORDER
# ============================================================

last_order = st.session_state.get(
    "last_order"
)


if not last_order:

    st.html("""
    <div style="
        text-align:center;
        padding:60px 20px;
    ">

        <div style="font-size:55px;">
            📦
        </div>

        <div style="
            font-size:28px;
            font-weight:800;
            color:#172337;
            margin-top:10px;
        ">
            No Recent Order
        </div>

        <div style="
            color:#666666;
            margin-top:8px;
        ">
            We couldn't find a recent order in this session.
        </div>

    </div>
    """)

    if st.button(
        "← Continue Shopping",
        use_container_width=True
    ):

        st.switch_page("app.py")

    st.stop()


# ============================================================
# CLEAN / ESCAPE DATA
# ============================================================

order_id = html.escape(
    str(last_order["order_id"])
)

customer_name = html.escape(
    str(last_order["name"])
)

payment_method = html.escape(
    str(last_order["payment_method"])
)

address = html.escape(
    str(last_order["address"])
)

phone = html.escape(
    str(last_order["phone"])
)

total_amount = float(
    last_order["total"]
)


# ============================================================
# SUCCESS HEADER
# ============================================================

st.html(
    f"""
    <div class="confirmation-wrapper">

        <div class="success-icon">
            🎉
        </div>

        <div class="success-title">
            Order Confirmed!
        </div>

        <div class="success-subtitle">
            Thank you for shopping with ShopSmart.
            Your order has been successfully placed.
        </div>

        <div class="order-id">
            Order ID: {order_id}
        </div>

    </div>
    """
)


st.divider()


# ============================================================
# MAIN CONTENT
# ============================================================

left_column, right_column = st.columns(
    [1.25, 0.75],
    gap="large"
)


# ============================================================
# LEFT COLUMN
# ============================================================

with left_column:

    # ========================================================
    # PURCHASED PRODUCTS
    # ========================================================

    st.html("""
    <div class="section-title">
        🛍️ Purchased Products
    </div>
    """)

    for item in last_order["items"]:

        product_name = html.escape(
            str(item["product_name"])
        )

        category = html.escape(
            str(item["category"])
        )

        price = float(
            item["price"]
        )

        st.html(
            f"""
            <div class="product-card">

                <div class="product-name">
                    {product_name}
                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:20px;
                ">

                    <div class="category-badge">
                        {category}
                    </div>

                    <div class="product-price">
                        ₹{price:,.2f}
                    </div>

                </div>

            </div>
            """
        )


    # ========================================================
    # DELIVERY INFORMATION
    # ========================================================

    st.write("")

    st.html("""
    <div class="section-title">
        🚚 Delivery Information
    </div>
    """)

    st.html(
        f"""
        <div class="delivery-card">

            <div style="
                font-weight:750;
                color:#172337;
                margin-bottom:4px;
            ">
                Delivery Address
            </div>

            <div style="
                margin-bottom:15px;
            ">
                {address}
            </div>

            <div style="
                font-weight:750;
                color:#172337;
                margin-bottom:4px;
            ">
                Contact Number
            </div>

            <div>
                {phone}
            </div>

        </div>
        """
    )


# ============================================================
# RIGHT COLUMN
# ============================================================

with right_column:

    # ========================================================
    # ORDER DETAILS
    # ========================================================

    st.html("""
    <div class="section-title">
        🧾 Order Details
    </div>
    """)

    st.html(
        f"""
        <div class="info-card">

            <div class="detail-label">
                Order ID
            </div>

            <div class="detail-value">
                {order_id}
            </div>

            <div class="detail-label">
                Customer
            </div>

            <div class="detail-value">
                {customer_name}
            </div>

            <div class="detail-label">
                Payment Method
            </div>

            <div class="detail-value">
                {payment_method}
            </div>

            <div class="detail-label">
                Products
            </div>

            <div class="detail-value">
                {len(last_order["items"])} item(s)
            </div>

            <div style="
                border-top:1px solid #eeeeee;
                padding-top:16px;
            ">

                <div class="total-label">
                    Total Amount
                </div>

                <div class="total-value">
                    ₹{total_amount:,.2f}
                </div>

            </div>

        </div>
        """
    )


    # ========================================================
    # ORDER STATUS
    # ========================================================

    st.html("""
    <div class="success-note">

        ✅ <b>Order Successfully Placed</b>

        <br><br>

        Your purchase has been recorded in the
        ShopSmart demonstration system.

    </div>
    """)


# ============================================================
# TIMESTAMP
# ============================================================

if last_order.get("timestamp"):

    timestamp = last_order["timestamp"]

    try:

        formatted_time = timestamp.strftime(
            "%d %B %Y, %I:%M %p"
        )

    except AttributeError:

        formatted_time = str(timestamp)

    st.caption(
        f"🕐 Order placed on {formatted_time}"
    )


# ============================================================
# CONTINUE SHOPPING
# ============================================================

st.write("")

st.divider()

if st.button(
    "🛒 Continue Shopping",
    type="primary",
    use_container_width=True
):

    st.switch_page(
        "app.py"
    )