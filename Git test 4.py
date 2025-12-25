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

# Custom CSS for #da7373 Background and White Cards
st.markdown("""
    <style>
    /* 1. Main Background Color */
    .stApp {
        background-color: #da7373;
    }

    /* 2. Text Colors on the Red Background */
    h1, h2, h3, .main-header {
        color: white !important;
        text-shadow: 0px 1px 2px rgba(0,0,0,0.2);
    }
    p, label, .stMarkdown {
        color: white;
    }
    
    /* 3. Card Styling (The White Boxes) */
    /* This targets Streamlit containers with borders to make them white cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    
    /* 4. Text INSIDE the White Cards (Must be black/dark) */
    div[data-testid="stVerticalBlockBorderWrapper"] * {
        color: #1a1a1a !important;
        text-shadow: none !important;
    }
    
    /* 5. Button Styling */
    .stButton>button {
        background-color: #1a1a1a;
        color: white !important;
        border-radius: 6px;
        border: none;
        font-weight: bold;
        width: 100%;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: white !important;
    }

    /* Metric Styling inside cards */
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 800 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem !important; }
    
    /* Input Fields (Make them pop against red) */
    .stSelectbox label, .stTextInput label, .stTextArea label {
        font-weight: bold;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LAYER (MOCK DATABASE) ---

def get_date_offset(days):
    today = datetime.date.today()
    target = today + datetime.timedelta(days=days)
    return target

SERVICES = {
    "Oil Change (Synthetic)": "oil",
    "Brake Pad Replacement": "brakes",
    "Wheel Alignment": "align",
    "AC Recharge": "ac",
    "Tire Rotation": "tires"
}

VEHICLES = {
    "Honda": ["Civic", "Accord", "CR-V", "Pilot"],
    "Toyota": ["Corolla", "Camry", "RAV4", "Tacoma"],
    "Ford": ["F-150", "Mustang", "Explorer", "Focus"],
    "BMW": ["3 Series", "5 Series", "X3", "X5"],
    "Tesla": ["Model 3", "Model Y", "Model S"]
}

@st.cache_data
def get_shops():
    shop_names = [
        "Midas Touch Auto", "Budget Fix Garage", "Prestige German Auto", 
        "QuickLane Services", "Tire & Tech Center", "Downtown Auto Pros",
        "Sparky's Electric", "Master Mechanic", "Pit Stop Crew", "Luxe Auto Spa"
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
        dist = round(random.uniform(0.5, 15.0), 1)
        rating = round(random.uniform(3.5, 5.0), 1)
        delay = random.randint(0, 7)
        
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

if 'selected_shop' not in st.session_state:
    st.session_state.selected_shop = None

shops_data = get_shops()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🚗 Your Vehicle")
    # Using markdown to force white text in sidebar isn't needed as sidebar is gray by default in Streamlit
    
    col_yr, col_mk = st.columns(2)
    with col_yr:
        year = st.selectbox("Year", range(2026, 1995, -1))
    with col_mk:
        make = st.selectbox("Make", list(VEHICLES.keys()))
        
    model = st.selectbox("Model", VEHICLES[make])
    
    st.markdown("---")
    st.info(f"Vehicle Set: **{year} {make} {model}**")

# --- 4. MAIN PAGE ---

st.title("CURB SIDE")
st.markdown("### Radical Transparency in Auto Repair.")

# TABS for Switching Modes
tab_book, tab_estimate = st.tabs(["📖 Book Service", "📝 Get Estimate"])

# ================= TAB 1: MARKETPLACE (BOOK) =================
with tab_book:
    
    # Service Selector
    col_svc, col_sort = st.columns([2, 1])
    with col_svc:
        selected_service_label = st.selectbox("Service Needed", list(SERVICES.keys()))
    with col_sort:
        sort_option = st.selectbox("Sort By", ["Earliest Availability", "Price: Low to High", "Rating: High to Low"])
        
    selected_service_key = SERVICES[selected_service_label]

    # Process Data
    display_list = []
    for shop in shops_data:
        shop_display = shop.copy()
        shop_display['current_price'] = shop['prices'][selected_service_key]
        display_list.append(shop_display)

    if sort_option == "Price: Low to High":
        display_list.sort(key=lambda x: x['current_price'])
    elif sort_option == "Rating: High to Low":
        display_list.sort(key=lambda x: x['rating'], reverse=True)
    else:
        display_list.sort(key=lambda x: x['availability_days'])

    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    # Render Cards
    for shop in display_list:
        # The 'border=True' here triggers our custom CSS to make it a White Card
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            
            with c1:
                st.subheader(shop['name'])
                st.caption(f"{shop['distance']} km • {shop['phone']}")
                st.markdown(f"⭐ **{shop['rating']}**")

            with c2:
                date_str = shop['availability_date'].strftime("%b %d")
                if shop['availability_days'] == 0:
                    avail_text = "Tomorrow"
                    color = "green"
                elif shop['availability_days'] < 3:
                    avail_text = "This Week"
                    color = "orange"
                else:
                    avail_text = "Next Week"
                    color = "gray"
                    
                st.metric("Availability", date_str, delta=avail_text)

            with c3:
                price_val = f"${shop['current_price']:.2f}"
                st.metric("Estimate", price_val)
                
                # Button Logic
                if st.button("Book Now", key=f"btn_{shop['id']}"):
                    st.session_state.selected_shop = shop
        
        # Expandable Booking Section (Inside the loop to appear under the card)
        if st.session_state.selected_shop and st.session_state.selected_shop['id'] == shop['id']:
            # We use a nested container for the form
            with st.container(border=True):
                st.markdown(f"**Confirm Booking at {shop['name']}**")
                st.info(f"Service: {selected_service_label} | Price: ${shop['current_price']:.2f}")
                
                with st.form(key=f"book_form_{shop['id']}"):
                    email = st.text_input("Email Address")
                    submitted = st.form_submit_button("Confirm Booking")
                    if submitted:
                        st.success("✅ Booking Confirmed! Check your email.")

# ================= TAB 2: BULK ESTIMATE =================
with tab_estimate:
    st.markdown("### Request Custom Quotes")
    st.markdown("Not sure what's wrong? Describe the issue and notify multiple shops at once.")
    
    with st.container(border=True):
        # 1. Description
        issue_desc = st.text_area("Describe your issue", height=150, 
                                  placeholder="e.g. My car creates a grinding noise when I brake at high speeds...")
        
        # 2. Select Shops
        all_shop_names = [s['name'] for s in shops_data]
        selected_shops = st.multiselect("Select Shops to Notify", all_shop_names, default=all_shop_names[:3])
        
        # 3. Submit
        if st.button("Send Bulk Inquiry", type="primary"):
            if len(issue_desc) < 10:
                st.error("Please describe your issue in more detail.")
            elif not selected_shops:
                st.error("Please select at least one shop.")
            else:
                with st.spinner("Sending inquiries..."):
                    time.sleep(1.5)
                st.balloons()
                st.success(f"✅ Inquiry successfully sent to {len(selected_shops)} shops!")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; opacity:0.8;'>© 2025 Curb Side Inc.</p>", unsafe_allow_html=True)