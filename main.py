import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime

# Set page configuration with green theme
st.set_page_config(
    page_title="Grocery List Generator",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Apply green theme with custom CSS
st.markdown("""
    <style>
    :root {
        --primary: #2e7d32;
        --primary-light: #60ad5e;
        --primary-dark: #005005;
        --secondary: #f5f5f5;
    }
    .stApp {
        background-color: #f0f9f0;
    }
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: var(--primary-dark) !important;
    }
    .stDownloadButton>button {
        background-color: var(--primary-light) !important;
    }
    .stFileUploader>div>div>div>button {
        background-color: var(--primary-light) !important;
        color: white !important;
    }
    .css-1aumxhk {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid var(--primary);
    }
    .stProgress>div>div>div>div {
        background-color: var(--primary);
    }
    .st-bb {
        background-color: white;
    }
    .st-at {
        background-color: #e8f5e9;
    }
    .st-bh {
        background-color: #e8f5e9;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: white;
    }
    .stNumberInput div[data-baseweb="input"] > div {
        background-color: white;
    }
    .stTextInput div[data-baseweb="input"] > div {
        background-color: white;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        color: var(--primary);
        font-size: 0.8rem;
    }
    .green-header {
        color: var(--primary);
    }
    </style>
""", unsafe_allow_html=True)

# Sample categories for grouping
CATEGORIES = [
    "Fruits & Vegetables", 
    "Dairy & Eggs", 
    "Bakery", 
    "Meat & Seafood", 
    "Pantry Staples", 
    "Frozen Foods", 
    "Beverages", 
    "Snacks", 
    "Personal Care", 
    "Cleaning Supplies"
]

# Initialize session state
if 'pantry' not in st.session_state:
    st.session_state.pantry = pd.DataFrame(columns=["Item", "Category", "Current Amount", "Unit"])
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = pd.DataFrame(columns=["Item", "Category", "Amount Needed", "Unit"])

# App title and description
st.title("🌿 EcoPantry - Green Grocery List Generator")
st.markdown("""
    <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32;'>
    Reduce food waste and shop sustainably! Track your pantry items, set monthly needs, 
    and generate eco-friendly shopping lists.
    </div>
""", unsafe_allow_html=True)

# Main app tabs
tab1, tab2, tab3 = st.tabs(["🏠 My Pantry", "📋 Generate Shopping List", "📊 Insights & Tips"])

with tab1:
    st.subheader("Manage Your Pantry Inventory")
    st.markdown("Track what you have at home to avoid over-purchasing and reduce waste.")
    
    # Pantry management section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Manual item addition form
        with st.expander("➕ Add New Item to Pantry", expanded=True):
            with st.form("add_item_form"):
                item_name = st.text_input("Item Name*", placeholder="e.g., Organic Apples")
                item_category = st.selectbox("Category*", CATEGORIES)
                col1, col2 = st.columns(2)
                current_amount = col1.number_input("Current Amount*", min_value=0.0, value=1.0, step=0.5)
                unit = col2.selectbox("Unit*", ["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"])
                
                if st.form_submit_button("Add to Pantry", use_container_width=True):
                    if item_name and item_category:
                        new_item = pd.DataFrame({
                            "Item": [item_name],
                            "Category": [item_category],
                            "Current Amount": [current_amount],
                            "Unit": [unit]
                        })
                        st.session_state.pantry = pd.concat([st.session_state.pantry, new_item], ignore_index=True)
                        st.success(f"✅ Added {item_name} to pantry!")
                    else:
                        st.warning("Please fill in all required fields (*)")

    with col2:
        # Pantry data upload
        st.markdown("### Import Pantry Data")
        st.markdown("Upload a CSV file with your existing pantry items")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="pantry_upload")
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                # Validate columns
                required_columns = ["Item", "Category", "Current Amount", "Unit"]
                if all(col in df.columns for col in required_columns):
                    st.session_state.pantry = df
                    st.success("✅ Pantry data imported successfully!")
                    st.dataframe(st.session_state.pantry.head(3))
                else:
                    st.error("CSV file must contain columns: Item, Category, Current Amount, Unit")
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Export pantry data
        if not st.session_state.pantry.empty:
            csv = st.session_state.pantry.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Pantry as CSV",
                data=csv,
                file_name=f"pantry_inventory_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                use_container_width=True
            )

    # Display current pantry
    if not st.session_state.pantry.empty:
        st.subheader("Current Pantry Inventory")
        st.dataframe(st.session_state.pantry.groupby("Category").apply(lambda x: x), height=400)
        
        # Option to edit/remove items
        with st.expander("Edit or Remove Items"):
            item_to_edit = st.selectbox("Select item to edit", st.session_state.pantry["Item"])
            item_data = st.session_state.pantry[st.session_state.pantry["Item"] == item_to_edit].iloc[0]
            
            with st.form("edit_item_form"):
                new_name = st.text_input("Item Name", value=item_data["Item"])
                new_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(item_data["Category"]))
                col1, col2 = st.columns(2)
                new_amount = col1.number_input("Current Amount", value=item_data["Current Amount"])
                new_unit = col2.selectbox("Unit", ["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"], 
                                          index=["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"].index(item_data["Unit"]))
                
                col1, col2 = st.columns(2)
                if col1.form_submit_button("Update Item", use_container_width=True):
                    st.session_state.pantry.loc[st.session_state.pantry["Item"] == item_to_edit, :] = [new_name, new_category, new_amount, new_unit]
                    st.success(f"✅ Updated {new_name}!")
                
                if col2.form_submit_button("❌ Remove Item", use_container_width=True):
                    st.session_state.pantry = st.session_state.pantry[st.session_state.pantry["Item"] != item_to_edit]
                    st.success(f"✅ Removed {item_to_edit} from pantry!")
    else:
        st.info("Your pantry is empty. Add items manually or import a CSV file.")

with tab2:
    st.subheader("Generate Monthly Shopping List")
    st.markdown("Set your monthly needs and generate a sustainable shopping list")
    
    if st.session_state.pantry.empty:
        st.warning("Please add items to your pantry first in the 'My Pantry' tab.")
    else:
        # Create a copy of pantry with monthly need fields
        if 'needs_df' not in st.session_state:
            st.session_state.needs_df = st.session_state.pantry.copy()
            st.session_state.needs_df["Monthly Need"] = 0
            st.session_state.needs_df["Priority"] = "Medium"
        
        # Create editable table for setting monthly needs
        with st.form("needs_form"):
            st.markdown("### Set Monthly Requirements")
            
            # Group by category
            for category, group in st.session_state.needs_df.groupby("Category"):
                st.markdown(f"**{category}**")
                for idx, row in group.iterrows():
                    cols = st.columns([3, 2, 2, 1])
                    item_name = cols[0].text_input("Item", value=row["Item"], key=f"item_{idx}", label_visibility="collapsed", disabled=True)
                    monthly_need = cols[1].number_input("Monthly Need", min_value=0.0, value=row["Monthly Need"], 
                                                       step=0.5, key=f"need_{idx}", label_visibility="collapsed")
                    unit = cols[2].selectbox("Unit", ["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"], 
                                           index=["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"].index(row["Unit"]), 
                                           key=f"unit_{idx}", label_visibility="collapsed")
                    priority = cols[3].selectbox("Priority", ["High", "Medium", "Low"], 
                                               index=["High", "Medium", "Low"].index(row["Priority"]), 
                                               key=f"priority_{idx}", label_visibility="collapsed")
                    
                    # Update values
                    st.session_state.needs_df.at[idx, "Monthly Need"] = monthly_need
                    st.session_state.needs_df.at[idx, "Unit"] = unit
                    st.session_state.needs_df.at[idx, "Priority"] = priority
            
            if st.form_submit_button("Calculate Shopping List", use_container_width=True):
                # Calculate needed amount
                st.session_state.needs_df["Amount Needed"] = st.session_state.needs_df["Monthly Need"] - st.session_state.needs_df["Current Amount"]
                st.session_state.needs_df["Amount Needed"] = st.session_state.needs_df["Amount Needed"].apply(lambda x: max(0, x))
                
                # Create shopping list
                st.session_state.shopping_list = st.session_state.needs_df[
                    st.session_state.needs_df["Amount Needed"] > 0
                ][["Item", "Category", "Amount Needed", "Unit", "Priority"]].sort_values(["Priority", "Category"])
                
                st.success("Shopping list generated successfully!")
        
        # Display shopping list
        if not st.session_state.shopping_list.empty:
            st.subheader("Your Eco-Friendly Shopping List")
            st.markdown("Items grouped by category for efficient shopping:")
            
            # Group by category
            for category, group in st.session_state.shopping_list.groupby("Category"):
                with st.expander(f"{category} ({len(group)} items)", expanded=True):
                    for _, row in group.iterrows():
                        st.markdown(f"- **{row['Item']}**: {row['Amount Needed']} {row['Unit']} "
                                    f"({'⭐' if row['Priority'] == 'High' else '📌' if row['Priority'] == 'Medium' else '🔹'}{row['Priority']})")
            
            # Download button
            csv = st.session_state.shopping_list[["Item", "Category", "Amount Needed", "Unit"]].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Shopping List as CSV",
                data=csv,
                file_name=f"eco_shopping_list_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                use_container_width=True
            )
            
            # Print-friendly version
            st.markdown("---")
            st.subheader("Print-Friendly List")
            printable_list = ""
            for category, group in st.session_state.shopping_list.groupby("Category"):
                printable_list += f"\n\n**{category}**\n"
                for _, row in group.iterrows():
                    printable_list += f"- {row['Item']}: {row['Amount Needed']} {row['Unit']}\n"
            
            st.markdown(printable_list)
        else:
            st.info("No items needed for shopping this month! 🎉")

with tab3:
    st.subheader("Sustainability Insights & Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 Your Environmental Impact")
        if not st.session_state.pantry.empty:
            # Calculate some stats
            total_items = len(st.session_state.pantry)
            waste_reduction = min(100, total_items * 5)  # Fake metric for demo
            co2_reduction = min(1000, total_items * 15)  # Fake metric for demo
            
            st.metric("Items Tracked", f"{total_items} items")
            st.metric("Estimated Waste Reduction", f"{waste_reduction}%")
            st.metric("Estimated CO₂ Reduction", f"{co2_reduction} kg/year")
            
            # Progress bars
            st.progress(waste_reduction / 100)
            st.caption("Waste reduction progress")
            st.progress(min(1, co2_reduction / 1000))
            st.caption("CO₂ reduction progress")
        else:
            st.info("Add items to your pantry to see your environmental impact")
    
    with col2:
        st.markdown("### 💡 Eco-Friendly Shopping Tips")
        tips = [
            "🛒 **Plan meals around what you already have** to reduce food waste",
            "📅 **Shop with a list** to avoid impulse buys and unnecessary purchases",
            "🌱 **Choose seasonal produce** for lower carbon footprint",
            "🥦 **Buy imperfect produce** to help reduce food waste",
            "🔄 **Bring reusable bags** and containers to the store",
            "🚲 **Walk or bike** to the store when possible",
            "📦 **Buy in bulk** for items you use frequently to reduce packaging",
            "🏷️ **Check expiration dates** to ensure you can use items before they expire"
        ]
        
        for tip in tips:
            st.markdown(f"- {tip}")
    
    st.markdown("---")
    st.markdown("### 📈 Food Waste Statistics")
    st.markdown("""
        - Approximately 1/3 of all food produced globally is wasted
        - If food waste were a country, it would be the 3rd largest emitter of greenhouse gases
        - The average household throws away about $1,500 worth of food each year
        - Reducing food waste is one of the most effective ways to fight climate change
    """)
    
    # Resources section
    st.markdown("### 📚 Sustainable Living Resources")
    resources = [
        ["Love Food Hate Waste", "https://www.lovefoodhatewaste.com/"],
        ["EPA Food Recovery Hierarchy", "https://www.epa.gov/sustainable-management-food/food-recovery-hierarchy"],
        ["Zero Waste Home", "https://zerowastehome.com/"],
        ["Seasonal Food Guide", "https://www.seasonalfoodguide.org/"]
    ]
    
    for name, url in resources:
        st.markdown(f"- [{name}]({url})")

# Footer
st.markdown("---")
st.markdown("""
    <div class='footer'>
        🌿 EcoPantry - Helping you shop sustainably and reduce food waste 🌎<br>
        Made with ♻️ | Data is stored locally in your browser
    </div>
""", unsafe_allow_html=True)