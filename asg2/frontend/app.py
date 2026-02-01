import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Food Delivery", layout="wide")
st.title("Food Delivery")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = None

if not st.session_state.user_id:
    menu = st.sidebar.selectbox("Menu", ["Signup", "Login"])
elif st.session_state.role == "admin":
    menu = st.sidebar.selectbox("Menu", ["Admin Panel"])
else:
    menu = st.sidebar.selectbox("Menu", ["Browse Restaurants", "Cart", "Orders"])

if menu == "Signup":
    st.header("Signup")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Signup"):
        r = requests.post(API + "/signup", params={"username": u, "password": p})
        st.success("Signup successful. Login now.")

elif menu == "Login":
    st.header("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        r = requests.post(API + "/login", params={"username": u, "password": p})
        if r.status_code == 200:
            data = r.json()
            st.session_state.user_id = data["user_id"]
            st.session_state.role = data["role"]
            st.success("Logged in")
            st.rerun()
        else:
            st.error("Invalid credentials")

elif menu == "Browse Restaurants":

    st.header("Browse Restaurants")

    col1, col2 = st.columns(2)

    with col1:
        search = st.text_input("Search by restaurant name")

    with col2:
        cuisine = st.text_input("Filter by cuisine")

    r = requests.get(
        API + "/restaurants",
        params={
            "search": search if search else None,
            "cuisine": cuisine if cuisine else None
        }
    )

    if r.status_code != 200:
        st.error("Failed to fetch restaurants")
        st.stop()

    restaurants = r.json()

    if not restaurants:
        st.info("No restaurants found")
        st.stop()

    for res in restaurants:
        st.subheader(f"{res['name']} ({res['cuisine']})")

        menu_items = requests.get(
            API + f"/menu/{res['id']}"
        ).json()

        if not menu_items:
            st.write("No menu items available")
            st.divider()
            continue

        for item in menu_items:

            col1, col2, col3 = st.columns([4, 2, 1])

            with col1:
                st.write(f"**{item['name']}** — ₹{item['price']}")

            with col2:
                qty = st.number_input(
                    "Qty",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"qty_{item['id']}"
                )

            with col3:
                if st.button("Add", key=f"add_{item['id']}"):
                    requests.post(
                        API + "/cart/add",
                        params={
                            "user_id": st.session_state.user_id,
                            "menu_item_id": item["id"],
                            "quantity": qty
                        }
                    )
                    st.success("Added to cart")

        st.divider()

elif menu == "Cart":
    st.header("Your Cart")

    cart = requests.get(API + f"/cart/{st.session_state.user_id}").json()

    if not cart:
        st.info("Cart is empty")
    else:
        total = 0
        restaurant_id = None

        for item in cart:
            total += item["total"]
            restaurant_id = item["restaurant_id"]

            col1, col2, col3, col4 = st.columns([4,2,2,1])

            with col1:
                st.write(f"{item['item_name']} ({item['restaurant_name']})")

            with col2:
                new_qty = st.number_input(
                    "Qty",
                    min_value=0,
                    value=item["quantity"],
                    key=f"qty{item['cart_id']}"
                )
                if new_qty != item["quantity"]:
                    requests.post(API + "/cart/update", params={
                        "cart_id": item["cart_id"],
                        "quantity": new_qty
                    })
                    st.rerun()

            with col3:
                st.write(f"₹ {item['total']}")

            with col4:
                if st.button("❌", key=f"del{item['cart_id']}"):
                    requests.delete(API + f"/cart/{item['cart_id']}")
                    st.rerun()

        st.subheader(f"Total Bill: ₹{total}")

        if st.button("Place Order"):
            requests.post(API + "/orders/place", params={
                "user_id": st.session_state.user_id,
                "restaurant_id": restaurant_id
            })
            st.success("Order placed")
            st.rerun()

elif menu == "Orders":
    st.header("Order History")

    orders = requests.get(API + f"/orders/history/{st.session_state.user_id}").json()

    for o in orders:
        st.subheader(f"Order {o['order_id']} | {o['restaurant']}")

        for i in o["items"]:
            st.write(f"- {i['item_name']} x {i['quantity']} = ₹{i['price']}")

        st.write(f"Status: {o['status']} | Payment: {o['payment_status']}")
        st.write(f"Total Paid: ₹{o['total_paid']}")

        if o["status"] != "delivered":
            if st.button("Cancel Order", key=f"cancel{o['order_id']}"):
                requests.post(API + f"/orders/{o['order_id']}/cancel")
                st.rerun()

        st.divider()

elif menu == "Admin Panel":

    st.header("Admin Panel")

    admin_choice = st.selectbox(
        "Choose Admin Action",
        [
            "Add Restaurant",
            "Delete Restaurant",
            "Add Menu Item",
            "Delete Menu Item",
            "Manage Orders"
        ]
    )

    if admin_choice == "Add Restaurant":
        st.subheader("Add Restaurant")

        name = st.text_input("Restaurant Name")
        cuisine = st.text_input("Cuisine")

        if st.button("Create Restaurant"):
            r = requests.post(
                API + "/restaurants",
                params={
                    "name": name,
                    "cuisine": cuisine,
                    "user_id": st.session_state.user_id
                }
            )

            if r.status_code == 200:
                st.success("Restaurant added successfully")
                st.rerun()
            else:
                st.error(r.text)

    elif admin_choice == "Delete Restaurant":
        st.subheader("Delete Restaurant")

        restaurants = requests.get(API + "/restaurants").json()

        if not restaurants:
            st.info("No restaurants available")
            st.stop()

        rest_map = {
            f"{r['name']} (ID {r['id']})": r["id"]
            for r in restaurants
        }

        selected = st.selectbox("Select Restaurant", rest_map.keys())

        if st.button("Delete Restaurant"):
            requests.delete(API + f"/restaurants/{rest_map[selected]}")
            st.success("Restaurant deleted")
            st.rerun()

    elif admin_choice == "Add Menu Item":
        st.subheader("Add Menu Item")

        restaurants = requests.get(API + "/restaurants").json()

        if not restaurants:
            st.warning("Create a restaurant first")
            st.stop()

        rest_map = {
            f"{r['name']} (ID {r['id']})": r["id"]
            for r in restaurants
        }

        rest_selected = st.selectbox("Restaurant", rest_map.keys())
        restaurant_id = rest_map[rest_selected]

        item_name = st.text_input("Item Name")
        price = st.number_input("Price", min_value=1.0)

        if st.button("Add Item"):
            r = requests.post(
                API + "/menu",
                params={
                    "name": item_name,
                    "price": price,
                    "restaurant_id": restaurant_id,
                    "user_id": st.session_state.user_id
                }
            )

            if r.status_code == 200:
                st.success(f"Menu item added (ID: {r.json()['id']})")
                st.rerun()
            else:
                st.error(r.text)

        st.divider()
        st.subheader("Existing Menu")

        menu_items = requests.get(API + f"/menu/{restaurant_id}").json()
        for m in menu_items:
            st.write(f"{m['id']} | {m['name']} | ₹{m['price']}")

    elif admin_choice == "Delete Menu Item":
        st.subheader("Delete Menu Item")

        restaurants = requests.get(API + "/restaurants").json()
        rest_map = {r["name"]: r["id"] for r in restaurants}
        rest = st.selectbox("Restaurant", rest_map.keys())

        menu_items = requests.get(
            API + f"/menu/{rest_map[rest]}"
        ).json()

        if not menu_items:
            st.info("No menu items to delete")
            st.stop()

        item_map = {
            f"{m['name']} (ID {m['id']})": m["id"]
            for m in menu_items
        }

        selected_item = st.selectbox("Menu Item", item_map.keys())

        if st.button("Delete Item"):
            requests.delete(API + f"/menu/{item_map[selected_item]}")
            st.success("Menu item deleted")
            st.rerun()

    elif admin_choice == "Manage Orders":
        st.subheader("Manage Orders")

        orders = requests.get(API + "/admin/orders").json()

        if not orders:
            st.info("No orders yet")
            st.stop()

        for o in orders:
            st.markdown(
                f"""
                **Order ID:** {o['id']}  
                **User ID:** {o['user_id']}  
                **Restaurant ID:** {o['restaurant_id']}  
                **Status:** {o['status']}  
                **Payment:** {o['payment_status']}
                """
            )

            col1, col2 = st.columns(2)

            with col1:
                new_status = st.selectbox(
                    "Update Status",
                    ["placed", "preparing", "packed", "ready", "delivered"],
                    index=["placed", "preparing", "packed", "ready", "delivered"].index(o["status"]),
                    key=f"status_{o['id']}"
                )

                if st.button("Update Status", key=f"st_{o['id']}"):
                    requests.post(
                        API + f"/orders/{o['id']}/status",
                        params={"status": new_status}
                    )
                    st.success("Status updated")
                    st.rerun()

            with col2:
                new_payment = st.selectbox(
                    "Payment Status",
                    ["pending", "paid"],
                    index=["pending", "paid"].index(o["payment_status"]),
                    key=f"pay_{o['id']}"
                )

                if st.button("Update Payment", key=f"paybtn_{o['id']}"):
                    requests.post(
                        API + f"/orders/{o['id']}/payment",
                        params={"payment_status": new_payment}
                    )
                    st.success("Payment updated")
                    st.rerun()

            st.divider()
