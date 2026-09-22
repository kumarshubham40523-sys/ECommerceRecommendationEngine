import streamlit as st
import uuid
import os
import pandas as pd
from datetime import datetime
import html


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ShopSmart Checkout",
    page_icon="💳",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html("""
<style>

.checkout-title {
    font-size: 34px;
    font-weight: 800;
    color: #172337;
    margin-bottom: 4px;
}

.checkout-subtitle {
    color: #666666;
    font-size: 15px;
    margin-bottom: 20px;
}

.section-title {
    font-size: 21px;
    font-weight: 800;
    color: #172337;
    margin-bottom: 14px;
}

.order-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 17px 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.product-name {
    color: #172337;
    font-size: 17px;
    font-weight: 750;
    margin-bottom: 7px;
}

.category-badge {
    display: inline-block;
    background: #e8f1ff;
    color: #2874f0;
    padding: 5px 10px;
    border-radius: 14px;
    font-size: 12px;
    font-weight: 700;
}

.product-price {
    color: #1b5e20;
    font-size: 21px;
    font-weight: 800;
    text-align: right;
}

.summary-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    margin-top: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.summary-row {
    display: flex;
    justify-content: space-between;
    color: #555555;
    font-size: 14px;
    margin-bottom: 11px;
}

.summary-total {
    display: flex;
    justify-content: space-between;
    border-top: 1px solid #eeeeee;
    padding-top: 15px;
    margin-top: 12px;
    color: #172337;
    font-size: 22px;
    font-weight: 800;
}

.green-price {
    color: #1b5e20;
}

.info-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.security-card {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-left: 4px solid #2874f0;
    border-radius: 9px;
    padding: 13px 15px;
    color: #555555;
    font-size: 13px;
    line-height: 1.55;
}

.checkout-user {
    color: #172337;
    font-size: 18px;
    font-weight: 800;
}

.detail-label {
    color: #777777;
    font-size: 13px;
    margin-bottom: 4px;
}

.detail-value {
    color: #172337;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 18px;
}

.payable {
    color: #1b5e20;
    font-size: 28px;
    font-weight: 850;
}

.ready-title {
    color: #172337;
    font-size: 20px;
    font-weight: 800;
}

.ready-subtitle {
    color: #666666;
    font-size: 13px;
    margin-top: 4px;
}

</style>
""")


# ============================================================
# GET CHECKOUT STATE
# ============================================================

buy_now_product = st.session_state.get(
    "buy_now_product"
)

selected_user = st.session_state.get(
    "selected_user"
)


# ============================================================
# GET USER CART
# ============================================================

if selected_user is not None:

    cart_items = st.session_state.get(
        "user_carts",
        {}
    ).get(
        selected_user,
        []
    )

else:

    cart_items = []


# ============================================================
# DETERMINE CHECKOUT ITEMS
# ============================================================

if buy_now_product:

    checkout_items = [buy_now_product]

else:

    checkout_items = cart_items


# ============================================================
# EMPTY CHECKOUT
# ============================================================

if not checkout_items:

    st.html("""
    <div style="
        text-align:center;
        padding:55px 20px;
    ">

        <div style="font-size:58px;">
            🛒
        </div>

        <div style="
            font-size:28px;
            font-weight:800;
            color:#172337;
            margin-top:10px;
        ">
            Your checkout is empty
        </div>

        <div style="
            color:#666666;
            font-size:15px;
            margin-top:8px;
        ">
            Add a product to your cart before proceeding.
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
# HEADER
# ============================================================

st.html("""
<div class="checkout-title">
    💳 Checkout
</div>

<div class="checkout-subtitle">
    Review your order and complete your purchase securely.
</div>
""")


if buy_now_product:

    st.info(
        "⚡ You are checking out this product using Buy Now."
    )

else:

    st.caption(
        f"👤 Checkout for User {selected_user}"
    )


st.divider()


# ============================================================
# CALCULATE TOTAL
# ============================================================

subtotal = sum(
    float(item["price"])
    for item in checkout_items
)

delivery_charge = 0.0

total_amount = (
    subtotal + delivery_charge
)


# ============================================================
# MAIN LAYOUT
# ============================================================

left_column, right_column = st.columns(
    [1.35, 0.65],
    gap="large"
)


# ============================================================
# LEFT COLUMN
# ============================================================

with left_column:

    # ========================================================
    # ORDER SUMMARY
    # ========================================================

    st.html("""
    <div class="section-title">
        🛍️ Order Summary
    </div>
    """)

    for item in checkout_items:

        product_name = html.escape(
            str(item["product_name"])
        )

        category = html.escape(
            str(item["category"])
        )

        item_price = float(
            item["price"]
        )

        st.html(
            f"""
            <div class="order-card">

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
                        ₹{item_price:,.2f}
                    </div>

                </div>

            </div>
            """
        )


    # ========================================================
    # PRICE SUMMARY
    # ========================================================

    st.html(
        f"""
        <div class="summary-card">

            <div class="summary-row">
                <span>Subtotal</span>
                <span>₹{subtotal:,.2f}</span>
            </div>

            <div class="summary-row">
                <span>Delivery</span>

                <span style="color:#1b5e20;">
                    FREE
                </span>
            </div>

            <div class="summary-total">

                <span>
                    Total Amount
                </span>

                <span class="green-price">
                    ₹{total_amount:,.2f}
                </span>

            </div>

        </div>
        """
    )


    # ========================================================
    # DELIVERY DETAILS
    # ========================================================

    st.write("")

    st.html("""
    <div class="section-title">
        📦 Delivery Details
    </div>
    """)

    name = st.text_input(
        "Full Name",
        placeholder="Enter your full name",
        key="checkout_name"
    )

    address = st.text_area(
        "Delivery Address",
        placeholder=(
            "House/Flat No., Street, City, "
            "State, PIN Code"
        ),
        key="checkout_address",
        height=110
    )

    phone = st.text_input(
        "Phone Number",
        placeholder="Enter your 10-digit phone number",
        key="checkout_phone"
    )


    # ========================================================
    # PAYMENT METHOD
    # ========================================================

    st.write("")

    st.html("""
    <div class="section-title">
        💰 Payment Method
    </div>
    """)

    payment_method = st.selectbox(
        "Choose payment method",
        [
            "Cash on Delivery",
            "UPI",
            "Credit / Debit Card"
        ],
        key="checkout_payment"
    )

    st.html("""
    <div class="security-card">
        🔒 <b>Demo Payment Environment:</b>
        This academic project does not process real payments.
        Payment selection is recorded only as part of the
        simulated checkout workflow.
    </div>
    """)


# ============================================================
# RIGHT COLUMN
# ============================================================

with right_column:

    st.html("""
    <div class="section-title">
        🧾 Order Details
    </div>
    """)

    payment_display = html.escape(
        str(payment_method)
    )

    st.html(
        f"""
        <div class="info-card">

            <div class="detail-label">
                Customer
            </div>

            <div class="checkout-user">
                User {selected_user}
            </div>

            <br>

            <div class="detail-label">
                Items
            </div>

            <div class="detail-value">
                {len(checkout_items)} item(s)
            </div>

            <div class="detail-label">
                Payment
            </div>

            <div class="detail-value">
                {payment_display}
            </div>

            <div style="
                border-top:1px solid #eeeeee;
                padding-top:16px;
            ">

                <div class="detail-label">
                    Amount Payable
                </div>

                <div class="payable">
                    ₹{total_amount:,.2f}
                </div>

            </div>

        </div>
        """
    )


    # ========================================================
    # SECURITY
    # ========================================================

    st.html("""
    <div class="security-card">

        🛡️ <b>Secure Checkout</b>

        <br><br>

        Your order information is handled within the
        ShopSmart application for this academic
        demonstration.

    </div>
    """)


# ============================================================
# PLACE ORDER AREA
# ============================================================

st.write("")

st.divider()

st.html(
    f"""
    <div style="
        margin-bottom:14px;
    ">

        <div class="ready-title">
            Ready to place your order?
        </div>

        <div class="ready-subtitle">
            Total payable: ₹{total_amount:,.2f}
        </div>

    </div>
    """
)


# ============================================================
# PLACE ORDER
# ============================================================

if st.button(
    "🛍️ Place Order",
    type="primary",
    use_container_width=True
):

    # ========================================================
    # VALIDATE CUSTOMER DETAILS
    # ========================================================

    clean_name = name.strip()
    clean_address = address.strip()
    clean_phone = phone.strip()

    if not clean_name:

        st.error(
            "Please enter your full name."
        )

    elif len(clean_name) < 2:

        st.error(
            "Please enter a valid name."
        )

    elif not clean_address:

        st.error(
            "Please enter your delivery address."
        )

    elif len(clean_address) < 10:

        st.error(
            "Please enter a complete delivery address."
        )

    elif not clean_phone:

        st.error(
            "Please enter your phone number."
        )

    elif (
        not clean_phone.isdigit()
        or len(clean_phone) != 10
    ):

        st.error(
            "Please enter a valid 10-digit phone number."
        )

    else:

        # ====================================================
        # RECORD PURCHASE INTERACTIONS
        # ====================================================

        search_log_file = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                )
            ),
            "data",
            "user_searches.csv"
        )

        selected_user = st.session_state.get(
            "selected_user"
        )

        if selected_user is not None:

            purchase_records = pd.DataFrame([
                {
                    "user_id": int(selected_user),

                    "product_id": int(
                        item["product_id"]
                    ),

                    "event_type": "purchase",

                    "query": "",

                    "timestamp": pd.Timestamp.now()
                }

                for item in checkout_items
            ])

            if os.path.exists(
                search_log_file
            ):

                existing_records = pd.read_csv(
                    search_log_file,
                    encoding="utf-8-sig"
                )

                updated_records = pd.concat(
                    [
                        existing_records,
                        purchase_records
                    ],
                    ignore_index=True
                )

            else:

                updated_records = purchase_records

            updated_records.to_csv(
                search_log_file,
                index=False,
                encoding="utf-8-sig"
            )


        # ====================================================
        # GENERATE ORDER ID
        # ====================================================

        order_id = (
            "SS-"
            + uuid.uuid4().hex[:8].upper()
        )


        # ====================================================
        # SAVE ORDER
        # ====================================================

        st.session_state[
            "last_order"
        ] = {

            "order_id": order_id,

            "items": checkout_items,

            "total": total_amount,

            "name": clean_name,

            "address": clean_address,

            "phone": clean_phone,

            "payment_method": payment_method,

            "timestamp": datetime.now()
        }


        # ====================================================
        # CLEAR USER CART
        # ====================================================

        if (
            selected_user is not None
            and not buy_now_product
        ):

            st.session_state[
                "user_carts"
            ][
                selected_user
            ] = []


        # ====================================================
        # CLEAR BUY NOW
        # ====================================================

        st.session_state.pop(
            "buy_now_product",
            None
        )


        # ====================================================
        # GO TO CONFIRMATION
        # ====================================================

        st.switch_page(
            "pages/order_confirmation.py"
        )