import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime

# Set page configuration with green theme
st.set_page_config(
    page_title="Green Grocery List Generator",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Apply green theme with custom CSS
st.markdown("""
    <style>
    :root {
        --primary: #1b5e20;  /* Darker green for better contrast */
        --primary-light: #4caf50;
        --primary-dark: #003300;
        --secondary: #ffffff;
        --background: #e8f5e9;
        --card-bg: #ffffff;
    }
    .stApp {
        background-color: var(--background);
    }
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: bold;
        border: 2px solid var(--primary-dark);
    }
    .stButton>button:hover {
        background-color: var(--primary-dark) !important;
    }
    .stDownloadButton>button {
        background-color: var(--primary-light) !important;
        border: 2px solid var(--primary);
    }
    .stFileUploader>div>div>div>button {
        background-color: var(--primary-light) !important;
        color: white !important;
        border: 2px solid var(--primary);
    }
    .css-1aumxhk {
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 20px;
        border: 2px solid var(--primary);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--card-bg) !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        margin: 0 5px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }
    .stProgress>div>div>div>div {
        background-color: var(--primary);
    }
    .st-bb {
        background-color: var(--card-bg);
    }
    .st-at {
        background-color: var(--background);
    }
    .st-bh {
        background-color: var(--background);
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: var(--card-bg);
    }
    .stNumberInput div[data-baseweb="input"] > div {
        background-color: var(--card-bg);
    }
    .stTextInput div[data-baseweb="input"] > div {
        background-color: var(--card-bg);
    }
    .footer {
        text-align: center;
        padding: 1rem;
        color: var(--primary);
        font-size: 0.8rem;
        font-weight: bold;
    }
    .green-header {
        color: var(--primary);
    }
    .add-item-form {
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 25px;
        border: 2px solid var(--primary);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }
    .form-title {
        text-align: center;
        color: var(--primary);
        font-size: 1.4rem;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .centered-form {
        display: flex;
        flex-direction: column;
        align-items: center;
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
st.title("🌿 Green Grocery List Generator")
st.markdown("""
    <div style='background-color: #ffffff; padding: 15px; border-radius: 10px; 
               border: 2px solid #1b5e20; margin-bottom: 25px;'>
    <h3 style='text-align: center; color: #1b5e20;'>Track your pantry items and generate monthly shopping lists</h3>
    </div>
""", unsafe_allow_html=True)

# Main app tabs
tab1, tab2 = st.tabs(["🏠 My Pantry", "📋 Generate Shopping List"])

with tab1:
    st.subheader("Manage Your Pantry Inventory")
    
    # Pantry management section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create a centered, prominent "Add New Item" section
        st.markdown("<div class='add-item-form'>", unsafe_allow_html=True)
        st.markdown("<div class='form-title'>➕ ADD NEW ITEM TO PANTRY</div>", unsafe_allow_html=True)
        
        with st.form("add_item_form"):
            # Center the form elements
            st.markdown("<div class='centered-form'>", unsafe_allow_html=True)
            
            item_name = st.text_input("Item Name*", placeholder="e.g., Apples", key="item_name")
            item_category = st.selectbox("Category*", CATEGORIES, key="item_category")
            
            col1, col2 = st.columns(2)
            current_amount = col1.number_input("Current Amount*", min_value=0.0, value=1.0, step=0.5, 
                                              key="current_amount")
            unit = col2.selectbox("Unit*", ["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"], 
                                 key="unit")
            
            submit_button = st.form_submit_button("ADD TO PANTRY", use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close centered-form div
            
            if submit_button:
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
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close add-item-form div

    with col2:
        # Pantry data upload
        st.markdown("<div style='background-color: #ffffff; padding: 15px; border-radius: 10px; border: 2px solid #1b5e20;'>", unsafe_allow_html=True)
        st.markdown("### Import/Export Pantry Data")
        st.markdown("Upload or download your pantry inventory")
        
        # File uploader
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="pantry_upload")
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                # Validate columns
                required_columns = ["Item", "Category", "Current Amount", "Unit"]
                if all(col in df.columns for col in required_columns):
                    st.session_state.pantry = df
                    st.success("✅ Pantry data imported successfully!")
                else:
                    st.error("CSV file must contain columns: Item, Category, Current Amount, Unit")
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Export pantry data
        if not st.session_state.pantry.empty:
            csv = st.session_state.pantry.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 EXPORT PANTRY AS CSV",
                data=csv,
                file_name=f"pantry_inventory_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                use_container_width=True
            )
        st.markdown("</div>", unsafe_allow_html=True)  # Close import/export container

    # Display current pantry
    if not st.session_state.pantry.empty:
        st.subheader("Current Pantry Inventory")
        st.markdown("<div style='background-color: #ffffff; padding: 15px; border-radius: 10px; border: 2px solid #1b5e20;'>", unsafe_allow_html=True)
        st.dataframe(st.session_state.pantry.groupby("Category").apply(lambda x: x), height=400)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Option to edit/remove items
        with st.expander("EDIT OR REMOVE ITEMS", expanded=False):
            st.markdown("<div style='background-color: #ffffff; padding: 15px; border-radius: 10px; border: 2px solid #1b5e20;'>", unsafe_allow_html=True)
            item_to_edit = st.selectbox("Select item to edit", st.session_state.pantry["Item"])
            item_data = st.session_state.pantry[st.session_state.pantry["Item"] == item_to_edit].iloc[0]
            
            with st.form("edit_item_form"):
                new_name = st.text_input("Item Name", value=item_data["Item"], key="edit_name")
                new_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(item_data["Category"]), key="edit_category")
                col1, col2 = st.columns(2)
                new_amount = col1.number_input("Current Amount", value=item_data["Current Amount"], key="edit_amount")
                new_unit = col2.selectbox("Unit", ["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"], 
                                          index=["pcs", "kg", "g", "lb", "oz", "L", "mL", "pack", "box"].index(item_data["Unit"]), 
                                          key="edit_unit")
                
                col1, col2 = st.columns(2)
                if col1.form_submit_button("UPDATE ITEM", use_container_width=True):
                    st.session_state.pantry.loc[st.session_state.pantry["Item"] == item_to_edit, :] = [new_name, new_category, new_amount, new_unit]
                    st.success(f"✅ Updated {new_name}!")
                
                if col2.form_submit_button("❌ REMOVE ITEM", use_container_width=True):
                    st.session_state.pantry = st.session_state.pantry[st.session_state.pantry["Item"] != item_to_edit]
                    st.success(f"✅ Removed {item_to_edit} from pantry!")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Your pantry is empty. Add items manually or import a CSV file.")

with tab2:
    st.subheader("Generate Monthly Shopping List")
    
    if st.session_state.pantry.empty:
        st.warning("Please add items to your pantry first in the 'My Pantry' tab.")
    else:
        # Create a copy of pantry with monthly need fields
        if 'needs_df' not in st.session_state:
            st.session_state.needs_df = st.session_state.pantry.copy()
            st.session_state.needs_df["Monthly Need"] = 0
            st.session_state.needs_df["Priority"] = "Medium"
        
        # Create editable table for setting monthly needs
        st.markdown("<div style='background-color: #ffffff; padding: 15px; border-radius: 10px; border: 2px solid #1b5e20; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("### Set Monthly Requirements")
        
        with st.form("needs_form"):
            # Group by category
            for category, group in st.session_state.needs_df.groupby("Category"):
                st.markdown(f"<div style='background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin: 10px 0;'><strong>{category}</strong></div>", unsafe_allow_html=True)
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
            
            if st.form_submit_button("CALCULATE SHOPPING LIST", use_container_width=True):
                # Calculate needed amount
                st.session_state.needs_df["Amount Needed"] = st.session_state.needs_df["Monthly Need"] - st.session_state.needs_df["Current Amount"]
                st.session_state.needs_df["Amount Needed"] = st.session_state.needs_df["Amount Needed"].apply(lambda x: max(0, x))
                
                # Create shopping list
                st.session_state.shopping_list = st.session_state.needs_df[
                    st.session_state.needs_df["Amount Needed"] > 0
                ][["Item", "Category", "Amount Needed", "Unit", "Priority"]].sort_values(["Priority", "Category"])
                
                st.success("Shopping list generated successfully!")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display shopping list
        if not st.session_state.shopping_list.empty:
            st.subheader("Your Shopping List")
            st.markdown("<div style='background-color: #ffffff; padding: 15px; border-radius: 10px; border: 2px solid #1b5e20;'>", unsafe_allow_html=True)
            
            # Group by category
            for category, group in st.session_state.shopping_list.groupby("Category"):
                with st.expander(f"{category} ({len(group)} items)", expanded=True):
                    for _, row in group.iterrows():
                        st.markdown(f"- **{row['Item']}**: {row['Amount Needed']} {row['Unit']} "
                                    f"({'⭐' if row['Priority'] == 'High' else '📌' if row['Priority'] == 'Medium' else '🔹'}{row['Priority']})")
            
            # Download button
            csv = st.session_state.shopping_list[["Item", "Category", "Amount Needed", "Unit"]].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DOWNLOAD SHOPPING LIST AS CSV",
                data=csv,
                file_name=f"shopping_list_{datetime.now().strftime('%Y%m%d')}.csv",
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
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No items needed for shopping this month! 🎉")

# Footer
st.markdown("---")
st.markdown("""
    <div class='footer'>
        Green Grocery List Generator | Data is stored locally in your browser
    </div>
""", unsafe_allow_html=True)