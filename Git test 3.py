import streamlit as st
import pandas as pd
import datetime
import random
import time

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Curb Side | Auto Marketplace",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for the "Air Canada" / Corporate Vibe
st.markdown("""
    <style>
    /* Headers */
    h1, h2, h3 { font-family: 'Helvetica', 'Arial', sans-serif; font-weight: 700; color: #1a1a1a; }
    .main-header { color: #CD202C; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; font-weight: bold; }
    
    /* Buttons */
    .stButton>button {
        background-color: #CD202C;
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #8B0000;
        color: white;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] { font-size: 1.2rem; color: #1a1a1a; }
    div[data-testid="stMetricLabel"] { font-size: 0.8rem; color: #666; }
    
    /* Containers */
    .shop-container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LAYER (MOCK DATABASE) ---

# Helper to get dates relative to today (2025 context)
def get_date_offset(days):
    today = datetime.date.today()
    target = today + datetime.timedelta(days=days)
    return target

# Services and base prices
SERVICES = {
    "Oil Change (Synthetic)": "oil",
    "Brake Pad Replacement": "brakes",
    "Wheel Alignment": "align",
    "AC Recharge": "ac",
    "Tire Rotation": "tires"
}

# Vehicle Data
VEHICLES = {
    "Honda": ["Civic", "Accord", "CR-V", "Pilot"],
    "Toyota": ["Corolla", "Camry", "RAV4", "Tacoma"],
    "Ford": ["F-150", "Mustang", "Explorer", "Focus"],
    "BMW": ["3 Series", "5 Series", "X3", "X5"],
    "Tesla": ["Model 3", "Model Y", "Model S"]
}

# Generate 10 Mock Shops
@st.cache_data
def get_shops():
    shop_names = [
        "Midas Touch Auto", "Budget Fix Garage", "Prestige German Auto", 
        "QuickLane Services", "Tire & Tech Center", "Downtown Auto Pros",
        "Sparky's Electric & Hybrid", "Master Mechanic", "Pit Stop Crew", "Luxe Auto Spa"
    ]
    
    descriptions = [
        "Certified technicians specializing in imports.",
        "No frills, just honest repairs for less.",
        "High-end service for luxury vehicles.",
        "Get in and out in under 30 minutes.",
        "Suspension and wheel experts.",
        "Conveniently located in the heart of the city.",
        "Specialists in EV and Hybrid systems.",
        "ASE Certified with 30 years experience.",
        "Family owned and operated since 1995.",
        "Premium service with a complimentary wash."
    ]

    shops = []
    for i, name in enumerate(shop_names):
        # Randomized logic for variety
        dist = round(random.uniform(0.5, 15.0), 1)
        rating = round(random.uniform(3.5, 5.0), 1)
        delay = random.randint(0, 7) # Days until available
        
        # Pricing logic: Randomize slightly around a base
        prices = {
            "oil": round(random.uniform(49, 129), 2),
            "brakes": round(random.uniform(150, 400), 2),
            "align": round(random.uniform(89, 159), 2),
            "ac": round(random.uniform(99, 199), 2),
            "tires": round(random.uniform(29, 69), 2),
        }

        shops.append({
            "id": i,
            "name": name,
            "desc": descriptions[i],
            "distance": dist,
            "rating": rating,
            "availability_days": delay,
            "availability_date": get_date_offset(delay),
            "prices": prices,
            "phone": f"(555) {random.randint(100,999)}-{random.randint(1000,9999)}"
        })
    return shops

# Initialize Session State for Booking
if 'selected_shop' not in st.session_state:
    st.session_state.selected_shop = None
if 'booking_status' not in st.session_state:
    st.session_state.booking_status = None

shops_data = get_shops()

# --- 3. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.title("🚗 My Vehicle")
    
    col_yr, col_mk = st.columns(2)
    with col_yr:
        year = st.selectbox("Year", range(2026, 1995, -1))
    with col_mk:
        make = st.selectbox("Make", list(VEHICLES.keys()))
        
    model = st.selectbox("Model", VEHICLES[make])
    
    st.markdown("---")
    st.title("🛠️ Service")
    selected_service_label = st.selectbox("Service Needed", list(SERVICES.keys()))
    selected_service_key = SERVICES[selected_service_label]
    
    st.info(f"Searching for **{selected_service_label}** for a **{year} {make} {model}**.")

# --- 4. MAIN PAGE ---

# Hero Header
st.markdown('<p class="main-header">CURB SIDE MARKETPLACE</p>', unsafe_allow_html=True)
st.title("Radical Transparency.")
st.markdown("Compare local shops by real-time price, availability, and rating.")

st.markdown("---")

# Sort Controls
col_sort1, col_sort2 = st.columns([3, 1])
with col_sort1:
    st.subheader(f"Results for: {selected_service_label}")
with col_sort2:
    sort_option = st.selectbox("Sort By", ["Earliest Availability", "Price: Low to High", "Rating: High to Low"])

# --- 5. DATA PROCESSING & SORTING ---

# Create a display list containing only relevant info
display_list = []
for shop in shops_data:
    shop_display = shop.copy()
    shop_display['current_price'] = shop['prices'][selected_service_key]
    display_list.append(shop_display)

# Sorting Logic
if sort_option == "Price: Low to High":
    display_list.sort(key=lambda x: x['current_price'])
elif sort_option == "Rating: High to Low":
    display_list.sort(key=lambda x: x['rating'], reverse=True)
else: # Earliest Availability
    display_list.sort(key=lambda x: x['availability_days'])

# --- 6. RESULTS RENDERING ---

for shop in display_list:
    
    # Card Container
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 2])
        
        # Col 1: Shop Info
        with c1:
            st.markdown(f"### {shop['name']}")
            st.markdown(f"*{shop['desc']}*")
            st.caption(f"📍 {shop['distance']} km away • 📞 {shop['phone']}")
            
            # Star Rating Visuals
            stars = "⭐" * int(shop['rating'])
            st.markdown(f"{stars} **{shop['rating']}/5.0**")

        # Col 2: Availability
        with c2:
            date_str = shop['availability_date'].strftime("%a, %b %d")
            
            if shop['availability_days'] == 0:
                avail_color = "green"
                avail_text = "Available Tomorrow"
            elif shop['availability_days'] < 3:
                avail_color = "orange"
                avail_text = "This Week"
            else:
                avail_color = "gray"
                avail_text = "Next Week"
                
            st.metric(label="Earliest Slot", value=date_str, delta=avail_text, delta_color="normal")

        # Col 3: Price & Action
        with c3:
            st.markdown(f"<h2 style='text-align: right; color: #1a1a1a;'>${shop['current_price']:.2f}</h2>", unsafe_allow_html=True)
            
            # Selection Logic
            if st.button("Select Shop", key=f"btn_{shop['id']}"):
                st.session_state.selected_shop = shop
                st.session_state.booking_status = None # Reset previous booking status

    # --- 7. ESTIMATE / BOOKING SECTION (Conditional) ---
    # This renders immediately below the specific card if selected, 
    # OR we can render it at the top/bottom. 
    # For a cleaner UI, we usually check if this specific shop is the selected one.
    
    if st.session_state.selected_shop and st.session_state.selected_shop['id'] == shop['id']:
        with st.expander("📝 Request Estimate & Booking", expanded=True):
            st.markdown(f"**Contacting: {shop['name']}**")
            
            with st.form(key=f"form_{shop['id']}"):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    customer_email = st.text_input("Your Email")
                    customer_phone = st.text_input("Your Phone")
                with col_f2:
                    issue_desc = st.text_area("Describe your issue details", 
                                            value=f"I need a {selected_service_label} for my {year} {make} {model}.",
                                            height=100)
                
                submit_btn = st.form_submit_button(label="Send Inquiry")
                
                if submit_btn:
                    if not customer_email or not customer_phone:
                        st.error("Please provide contact details.")
                    else:
                        # Simulate API Call
                        with st.spinner("Sending request to shop..."):
                            time.sleep(1) 
                        st.success(f"✅ Inquiry sent to {shop['name']}! Check your email for a quote.")

# --- 8. FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 12px;'>© 2025 Curb Side Inc. <br>Radical Transparency in Auto Repair.</div>", 
    unsafe_allow_html=True
)