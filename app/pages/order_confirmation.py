import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Order Confirmed",
    page_icon="✅",
    layout="wide"
)


# ============================================================
# GET LAST ORDER
# ============================================================

last_order = st.session_state.get(
    "last_order"
)


if not last_order:

    st.warning("No recent order found.")

    if st.button("← Continue Shopping"):
        st.switch_page("app.py")

    st.stop()


# ============================================================
# SUCCESS MESSAGE
# ============================================================

st.title("🎉 Order Confirmed!")

st.success(
    "Thank you for shopping with ShopSmart!"
)

st.divider()


# ============================================================
# ORDER DETAILS
# ============================================================

st.subheader("📦 Order Details")

st.write(
    f"**Order ID:** {last_order['order_id']}"
)

st.write(
    f"**Customer:** {last_order['name']}"
)

st.write(
    f"**Payment Method:** "
    f"{last_order['payment_method']}"
)

st.write(
    f"**Total Amount:** "
    f"₹{last_order['total']:,.2f}"
)


# ============================================================
# PRODUCTS
# ============================================================

st.subheader("🛍️ Purchased Products")

for item in last_order["items"]:

    col1, col2 = st.columns(
        [4, 1]
    )

    with col1:

        st.markdown(
            f"### {item['product_name']}"
        )

        st.caption(
            item["category"]
        )

    with col2:

        st.write(
            f"₹{float(item['price']):,.2f}"
        )


st.divider()


# ============================================================
# DELIVERY
# ============================================================

st.subheader("🚚 Delivery Information")

st.write(
    f"**Delivery Address:** "
    f"{last_order['address']}"
)

st.write(
    f"**Contact Number:** "
    f"{last_order['phone']}"
)


st.info(
    "Your order has been successfully placed. "
    "This is a demonstration checkout system."
)


# ============================================================
# CONTINUE SHOPPING
# ============================================================

if st.button(
    "🛒 Continue Shopping",
    use_container_width=True
):

    st.switch_page("app.py")