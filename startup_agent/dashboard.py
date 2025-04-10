#!/usr/bin/env python
"""
Streamlit dashboard for exploring startup data
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from startup_agent.config import DATA_DIR
from startup_agent.utils.helpers import get_latest_data_file, load_json_data, load_json_file
from startup_agent.utils.pdf_generator import PDFReportGenerator
from startup_agent.agents.startup_collector import StartupCollector

# Page configuration
st.set_page_config(
    page_title="Venture Watch Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4285f4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #5f6368;
        margin-bottom: 1rem;
    }
    .company-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .company-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4285f4;
    }
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .tag {
        background-color: #f1f1f1;
        border-radius: 15px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        white-space: nowrap;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #5f6368;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #202124;
    }
    .key-info {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data() -> Tuple[List[Dict[str, Any]], str]:
    """
    Load the most recent startup data
    
    Returns:
        Tuple of (data, data_source)
    """
    # Find the most recent analyzed data file
    data_file = get_latest_data_file(prefix="funding_data_", suffix="_analyzed.json")
    
    if not data_file:
        # Try to load example data if no real data is available
        example_file = DATA_DIR / "example_funding_data_analyzed.json"
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                return json.load(f), f"Example data (no real data found)"
        else:
            return [], "No data found"
    
    # Load the data
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            source = f"Data from {data_file.name}"
            return data, source
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return [], f"Error: {str(e)}"

def create_company_card(company: Dict[str, Any]):
    """Create a company card with detailed information"""
    with st.container():
        st.markdown(f'<div class="company-card">', unsafe_allow_html=True)
        
        # Company name and funding
        st.markdown(f'<div class="company-name">{company.get("company_name", "Unknown")}</div>', unsafe_allow_html=True)
        
        # Key information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f'<div class="metric-label">Funding Round</div>'
                f'<div class="metric-value">{company.get("funding_round", "Unknown")}</div>', 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f'<div class="metric-label">Amount</div>'
                f'<div class="metric-value">{company.get("funding_amount", 0):,} {company.get("funding_currency", "USD")}</div>', 
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                f'<div class="metric-label">Location</div>'
                f'<div class="metric-value">{company.get("location", "Unknown")}</div>', 
                unsafe_allow_html=True
            )
        
        # Description
        st.markdown("### 🔍 Description")
        st.write(company.get("description", "No description available"))
        
        # Website
        st.markdown("### 🔗 Website")
        st.write(company.get("website", "None"))
        
        # Two columns for categories and tech stack
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧩 Categories")
            categories = company.get("categories", [])
            if categories:
                st.markdown(
                    f'<div class="tag-container">' + 
                    ''.join([f'<span class="tag">{cat}</span>' for cat in categories]) + 
                    '</div>', 
                    unsafe_allow_html=True
                )
            else:
                st.write("None specified")
        
        with col2:
            st.markdown("### 💻 Tech Stack")
            tech_stack = company.get("tech_stack", [])
            if tech_stack:
                st.markdown(
                    f'<div class="tag-container">' + 
                    ''.join([f'<span class="tag">{tech}</span>' for tech in tech_stack]) + 
                    '</div>', 
                    unsafe_allow_html=True
                )
            else:
                st.write("None specified")
        
        # Hiring needs
        st.markdown("### 👥 Hiring Needs")
        hiring_needs = company.get("hiring_needs", [])
        if hiring_needs:
            st.markdown(
                f'<div class="tag-container">' + 
                ''.join([f'<span class="tag">{role}</span>' for role in hiring_needs]) + 
                '</div>', 
                unsafe_allow_html=True
            )
        else:
            st.write("None specified")
        
        # Product focus
        st.markdown("### 🎯 Product Focus")
        st.write(company.get("product_focus", "Unknown"))
        
        st.markdown('</div>', unsafe_allow_html=True)

def generate_sample_data():
    """Generate sample data for demonstration purposes."""
    collector = StartupCollector()
    return collector._generate_sample_data()

def format_currency(amount):
    """Format the amount as a currency string."""
    if amount is None:
        return "Unknown"
    
    # Convert to float if it's a string
    if isinstance(amount, str):
        try:
            amount = float(amount.replace("$", "").replace(",", ""))
        except:
            return amount
    
    # Format as currency
    if amount >= 1000:
        return f"${amount/1000:.1f}B"
    else:
        return f"${amount:.1f}M"

def main():
    # Header
    st.markdown('<div class="main-header">🚀 Venture Watch Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Explore recently funded startups that match your skills</div>', unsafe_allow_html=True)
    
    # Load data
    data, data_source = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    if not data:
        st.warning("No startup data available. Please run the data collection pipeline first.")
        return
    
    st.sidebar.caption(f"Data source: {data_source}")
    
    # Convert to DataFrame for easier filtering and visualization
    df = pd.DataFrame(data)
    
    # Ensure all required columns exist
    required_columns = ["company_name", "funding_amount", "funding_round", "industry", "location"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = "Unknown"
    
    # Clean up funding_amount if needed
    if "funding_amount" in df.columns:
        # Convert to float if possible
        df["funding_amount"] = pd.to_numeric(df["funding_amount"], errors="coerce")
        # Replace NaN with 0
        df["funding_amount"].fillna(0, inplace=True)
    
    # Industry filter
    industries = ["All"] + sorted(df["industry"].dropna().unique().tolist())
    selected_industry = st.sidebar.selectbox("Industry", industries)
    
    # Funding round filter
    rounds = ["All"] + sorted(df["funding_round"].dropna().unique().tolist())
    selected_round = st.sidebar.selectbox("Funding Round", rounds)
    
    # Location filter
    locations = ["All"] + sorted(df["location"].dropna().unique().tolist())
    selected_location = st.sidebar.selectbox("Location", locations)
    
    # Minimum funding filter
    if "funding_amount" in df.columns:
        min_funding = st.sidebar.slider(
            "Minimum Funding ($ Million)", 
            min_value=0.0, 
            max_value=float(df["funding_amount"].max()) + 5.0, 
            value=0.0,
            step=1.0
        )
    else:
        min_funding = 0.0
    
    # Apply filters
    filtered_df = df.copy()
    if selected_industry != "All":
        filtered_df = filtered_df[filtered_df["industry"] == selected_industry]
    if selected_round != "All":
        filtered_df = filtered_df[filtered_df["funding_round"] == selected_round]
    if selected_location != "All":
        filtered_df = filtered_df[filtered_df["location"] == selected_location]
    if "funding_amount" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["funding_amount"] >= min_funding]
    
    # Dashboard sections
    tabs = st.tabs(["Overview", "Companies", "Analytics", "Export Options"])
    
    # Overview tab
    with tabs[0]:
        # Key metrics
        st.markdown("## 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Startups", len(filtered_df))
        
        with col2:
            total_funding = filtered_df["funding_amount"].sum()
            st.metric("Total Funding", format_currency(total_funding))
        
        with col3:
            avg_funding = total_funding / len(filtered_df) if filtered_df.size > 0 else 0
            st.metric("Avg. Funding", format_currency(avg_funding))
        
        with col4:
            if "industry" in filtered_df.columns:
                top_industry = filtered_df["industry"].value_counts().idxmax() if not filtered_df.empty else "None"
                st.metric("Top Industry", top_industry)
            else:
                st.metric("Top Industry", "Unknown")
        
        # Top categories and tech
        st.markdown("## 🏷️ Top Categories and Technologies")
        col1, col2 = st.columns(2)
        
        with col1:
            # Count category occurrences
            category_counts = {}
            for company in filtered_df:
                for category in company.get("categories", []):
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            if category_counts:
                categories_df = pd.DataFrame({
                    "Category": list(category_counts.keys()),
                    "Count": list(category_counts.values())
                }).sort_values("Count", ascending=False).head(10)
                
                fig = px.bar(categories_df, x="Count", y="Category", orientation="h",
                            title="Top 10 Categories",
                            color="Count", color_continuous_scale="blues")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category data available")
        
        with col2:
            # Count tech stack occurrences
            tech_counts = {}
            for company in filtered_df:
                for tech in company.get("tech_stack", []):
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
            
            if tech_counts:
                tech_df = pd.DataFrame({
                    "Technology": list(tech_counts.keys()),
                    "Count": list(tech_counts.values())
                }).sort_values("Count", ascending=False).head(10)
                
                fig = px.bar(tech_df, x="Count", y="Technology", orientation="h",
                            title="Top 10 Technologies",
                            color="Count", color_continuous_scale="reds")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No tech stack data available")
    
    # Companies tab
    with tabs[1]:
        st.markdown("## 🏢 Startup Companies")
        st.markdown(f"Showing {len(filtered_df)} startups")
        
        if not filtered_df.empty:
            for company in filtered_df:
                create_company_card(company)
        else:
            st.info("No companies match your filters. Try adjusting your criteria.")
    
    # Analytics tab
    with tabs[2]:
        st.markdown("## 📈 Analytics")
        
        # Funding rounds distribution
        st.markdown("### Funding Rounds Distribution")
        funding_counts = {}
        for company in filtered_df:
            round_type = company.get("funding_round", "Unknown")
            funding_counts[round_type] = funding_counts.get(round_type, 0) + 1
        
        if funding_counts:
            funding_df = pd.DataFrame({
                "Round": list(funding_counts.keys()),
                "Count": list(funding_counts.values())
            })
            
            fig = px.pie(funding_df, values="Count", names="Round", 
                        title="Distribution of Funding Rounds",
                        color_discrete_sequence=px.colors.sequential.Blues)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No funding round data available")
        
        # Hiring needs analysis
        st.markdown("### Hiring Needs Analysis")
        role_counts = {}
        for company in filtered_df:
            for role in company.get("hiring_needs", []):
                role_counts[role] = role_counts.get(role, 0) + 1
        
        if role_counts:
            roles_df = pd.DataFrame({
                "Role": list(role_counts.keys()),
                "Count": list(role_counts.values())
            }).sort_values("Count", ascending=False).head(15)
            
            fig = px.bar(roles_df, x="Role", y="Count",
                        title="Top 15 In-Demand Roles",
                        color="Count", color_continuous_scale="greens")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hiring needs data available")
    
    # Export tab
    with tabs[3]:
        st.markdown("## 📤 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Export to PDF")
            st.write("Generate a PDF report with the filtered startup data")
            
            if st.button("Generate PDF Report"):
                with st.spinner("Generating PDF report..."):
                    generator = PDFReportGenerator()
                    pdf_path = generator.generate_pdf_report(filtered_df)
                    st.success(f"PDF report generated: {pdf_path}")
                    
                    # Create a download button
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="Download PDF Report",
                            data=f.read(),
                            file_name=f"startup_report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
        
        with col2:
            st.markdown("### Export to CSV")
            st.write("Export the filtered startup data to a CSV file")
            
            if st.button("Generate CSV"):
                # Convert the data to a DataFrame
                rows = []
                for company in filtered_df:
                    row = {
                        "Company Name": company.get("company_name", ""),
                        "Description": company.get("description", ""),
                        "Website": company.get("website", ""),
                        "Location": company.get("location", ""),
                        "Funding Date": company.get("funding_date", ""),
                        "Funding Amount": company.get("funding_amount", ""),
                        "Funding Currency": company.get("funding_currency", ""),
                        "Funding Round": company.get("funding_round", ""),
                        "Categories": ", ".join(company.get("categories", [])),
                        "Tech Stack": ", ".join(company.get("tech_stack", [])),
                        "Hiring Needs": ", ".join(company.get("hiring_needs", [])),
                        "Product Focus": company.get("product_focus", ""),
                        "Industry": company.get("industry", "Unknown"),
                        "Source": company.get("source", "Unknown")
                    }
                    rows.append(row)
                
                df = pd.DataFrame(rows)
                
                # Convert to CSV
                csv = df.to_csv(index=False).encode('utf-8')
                
                # Create download button
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"startup_data_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main() 