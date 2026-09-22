import streamlit as st
import uuid
import os
import pandas as pd
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ShopSmart Checkout",
    page_icon="💳",
    layout="wide"
)


# ============================================================
# GET CHECKOUT PRODUCT
# ============================================================

buy_now_product = st.session_state.get(
    "buy_now_product"
)

selected_user = st.session_state.get(
    "selected_user"
)

if selected_user is not None:

    cart_items = st.session_state["user_carts"].get(
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


if not checkout_items:

    st.warning("Your checkout is empty.")

    if st.button("← Continue Shopping"):
        st.switch_page("app.py")

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("💳 Checkout")
st.caption("Complete your order securely.")

st.divider()


# ============================================================
# ORDER SUMMARY
# ============================================================

st.subheader("🛍️ Order Summary")

total_amount = 0

for item in checkout_items:

    product_col, price_col = st.columns(
        [4, 1]
    )

    with product_col:

        st.markdown(
            f"### {item['product_name']}"
        )

        st.caption(
            f"{item['category']}"
        )

    with price_col:

        item_price = float(
            item["price"]
        )

        st.write(
            f"₹{item_price:,.2f}"
        )

        total_amount += item_price


st.divider()

st.subheader(
    f"Total: ₹{total_amount:,.2f}"
)


# ============================================================
# CUSTOMER DETAILS
# ============================================================

st.subheader("📦 Delivery Details")

name = st.text_input(
    "Full Name",
    placeholder="Enter your name",
    key="checkout_name"
)

address = st.text_area(
    "Delivery Address",
    placeholder="Enter your delivery address",
    key="checkout_address"
)

phone = st.text_input(
    "Phone Number",
    placeholder="Enter your phone number",
    key="checkout_phone"
)

# ============================================================
# PAYMENT METHOD
# ============================================================

st.subheader("💰 Payment Method")

payment_method = st.selectbox(
    "Choose payment method",
    [
        "Cash on Delivery",
        "UPI",
        "Credit / Debit Card"
    ]
)


# ============================================================
# PLACE ORDER
# ============================================================

if st.button(
    "🛍️ Place Order",
    use_container_width=True
):

    if not name.strip():

        st.error(
            "Please enter your name."
        )

    elif not address.strip():

        st.error(
            "Please enter your delivery address."
        )

    elif not phone.strip():

        st.error(
            "Please enter your phone number."
        )

    else:

        # ============================================================
        # RECORD PURCHASE INTERACTIONS
        # ============================================================

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
                    "product_id": int(item["product_id"]),
                    "event_type": "purchase",
                    "query": "",
                    "timestamp": pd.Timestamp.now()
                }
                for item in checkout_items
            ])

            if os.path.exists(search_log_file):

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


        # ============================================================
        # GENERATE DEMO ORDER ID
        # ============================================================

        order_id = (
            "SS-"
            + uuid.uuid4().hex[:8].upper()
        )

        # Save order information
        st.session_state[
            "last_order"
        ] = {
            "order_id": order_id,
            "items": checkout_items,
            "total": total_amount,
            "name": name,
            "address": address,
            "phone": phone,
            "payment_method": payment_method,
            "timestamp": datetime.now()
        }

        # Clear the selected user's cart after successful order
        if selected_user is not None and not buy_now_product:

            st.session_state["user_carts"][selected_user] = []

        # Clear Buy Now state
        st.session_state.pop(
            "buy_now_product",
            None
        )

        # Move to confirmation page
        st.switch_page(
            "pages/order_confirmation.py"
        )