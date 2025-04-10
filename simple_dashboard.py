#!/usr/bin/env python
"""
Simple Streamlit dashboard for Venture-Watch
This standalone version doesn't rely on importing modules from startup_agent
"""

import streamlit as st
import os
import json
import plotly.express as px
from datetime import datetime
import pandas as pd
import sys

# Add the root directory to the path to import startup_agent modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config
st.set_page_config(
    page_title="Venture-Watch Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Sample data - in a real implementation this would come from your data files
SAMPLE_DATA = [
    {
        "name": "TechCrunch AI",
        "funding_amount": 15000000,
        "funding_round": "Series A",
        "industry": "Artificial Intelligence",
        "location": "San Francisco, CA",
        "date_funded": "2024-04-01",
        "company_size": 25,
        "tech_stack": ["Python", "TensorFlow", "AWS", "React"],
        "description": "AI-powered content creation platform for marketers",
        "website": "https://example.com/techcrunch",
        "match_score": 85
    },
    {
        "name": "DataFlow Systems",
        "funding_amount": 8000000,
        "funding_round": "Seed",
        "industry": "Data Analytics",
        "location": "Boston, MA",
        "date_funded": "2024-04-05",
        "company_size": 12,
        "tech_stack": ["Python", "Spark", "Kubernetes", "Vue.js"],
        "description": "Real-time data processing and analytics platform",
        "website": "https://example.com/dataflow",
        "match_score": 78
    },
    {
        "name": "CloudStack Enterprise",
        "funding_amount": 25000000,
        "funding_round": "Series B",
        "industry": "Cloud Infrastructure",
        "location": "Seattle, WA",
        "date_funded": "2024-03-28",
        "company_size": 50,
        "tech_stack": ["Go", "Docker", "Kubernetes", "Terraform"],
        "description": "Multi-cloud orchestration and management platform",
        "website": "https://example.com/cloudstack",
        "match_score": 62
    },
    {
        "name": "SecureAuth Systems",
        "funding_amount": 12000000,
        "funding_round": "Series A",
        "industry": "Cybersecurity",
        "location": "Austin, TX",
        "date_funded": "2024-04-03",
        "company_size": 30,
        "tech_stack": ["Rust", "Python", "AWS", "React"],
        "description": "Zero-trust authentication and authorization platform",
        "website": "https://example.com/secureauth",
        "match_score": 71
    },
    {
        "name": "HealthTech Solutions",
        "funding_amount": 18000000,
        "funding_round": "Series A",
        "industry": "Healthcare",
        "location": "Chicago, IL",
        "date_funded": "2024-03-25",
        "company_size": 35,
        "tech_stack": ["Python", "TensorFlow", "AWS", "React Native"],
        "description": "AI-powered diagnostic assistance for clinicians",
        "website": "https://example.com/healthtech",
        "match_score": 65
    }
]

# Function to load data from a JSON file
def load_stored_data():
    """Load stored startup funding data from the data directory"""
    # Try to load real data from startup_agent/data directory
    try:
        data_path = os.path.join("startup_agent", "data", "funding_data.json")
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
            if data:
                return data
    except Exception as e:
        st.sidebar.warning(f"Error loading stored data: {str(e)}")
    
    # Fallback to sample data
    return SAMPLE_DATA

def load_live_data(search_terms=None, max_days=7):
    """Get live startup funding data from Google APIs"""
    try:
        # Import startup collector
        from startup_agent.agents.startup_collector import StartupCollector
        
        with st.sidebar.status("Fetching live startup data...") as status:
            # Initialize collector
            status.update(label="Initializing search...", state="running")
            collector = StartupCollector()
            
            # If search terms are provided, use them
            if search_terms:
                status.update(label=f"Searching for: {search_terms}", state="running")
                
                # Custom search with provided terms
                if isinstance(search_terms, str):
                    search_terms = [search_terms]
                
                # Get news results
                status.update(label="Searching Google News...", state="running")
                news_results = collector.collect_from_google_news(days=max_days)
                
                # Get custom search results
                status.update(label="Searching Google Custom Search...", state="running")
                search_results = collector.collect_from_custom_search()
                
                # Combine and deduplicate results
                status.update(label="Processing results...", state="running")
                results = collector.deduplicate_results(news_results, search_results)
            else:
                # Use default search
                status.update(label="Running default search...", state="running")
                results = collector.run()
            
            if results:
                status.update(label=f"Found {len(results)} startups!", state="complete")
                return results
            else:
                status.update(label="No startups found in live search", state="error")
                return SAMPLE_DATA
    except Exception as e:
        st.sidebar.error(f"Error during live search: {str(e)}")
        return SAMPLE_DATA

def main():
    # Page header
    st.title("🚀 Venture-Watch Dashboard")
    st.subheader("Recently Funded Startups Aligned With Your Skills")
    
    # Add Groq badge
    st.sidebar.markdown("### Powered by")
    st.sidebar.markdown("![Google News API](https://img.shields.io/badge/Google_News-4285F4?style=for-the-badge&logo=google&logoColor=white) ![Groq](https://img.shields.io/badge/Groq-20232A?style=for-the-badge&logo=groq&logoColor=61DAFB)")
    
    # Add a toggle for live data
    st.sidebar.markdown("### Data Source")
    use_live_data = st.sidebar.toggle("Use live search data", value=False)
    
    # Add custom search options if live data is enabled
    search_terms = None
    max_days = 7
    
    if use_live_data:
        st.sidebar.markdown("### Live Search Options")
        custom_search = st.sidebar.checkbox("Custom search terms", value=False)
        
        if custom_search:
            search_terms = st.sidebar.text_input(
                "Search terms (comma separated)",
                value="startup funding,seed round,series A"
            ).split(",")
            
        max_days = st.sidebar.slider(
            "Days to look back", 
            min_value=1, 
            max_value=30, 
            value=7
        )
    
    # Load data based on user selection
    if use_live_data:
        startups = load_live_data(search_terms, max_days)
        data_source = "Live Search" if startups else "Sample Data (Live search found no results)"
    else:
        startups = load_stored_data()
        data_source = "Stored Data" if len(startups) > len(SAMPLE_DATA) else "Sample Data"
    
    # Display data source
    st.sidebar.markdown(f"**Source:** {data_source}")
    
    # Convert to DataFrame for easier filtering and visualization
    df = pd.DataFrame(startups)
    
    # Ensure we have company_name field
    if "name" in df.columns and "company_name" not in df.columns:
        df["company_name"] = df["name"]
    
    # Sidebar filters
    st.sidebar.markdown("### Filters")
    
    # Industry filter
    industry_col = "industry" if "industry" in df.columns else None
    if industry_col:
        industries = ["All"] + sorted(df[industry_col].dropna().unique().tolist())
        selected_industry = st.sidebar.selectbox("Industry", industries)
    else:
        selected_industry = "All"
    
    # Funding round filter
    round_col = "funding_round" if "funding_round" in df.columns else None
    if round_col:
        rounds = ["All"] + sorted(df[round_col].dropna().unique().tolist())
        selected_round = st.sidebar.selectbox("Funding Round", rounds)
    else:
        selected_round = "All"
    
    # Location filter
    location_col = "location" if "location" in df.columns else None
    if location_col:
        locations = ["All"] + sorted(df[location_col].dropna().unique().tolist())
        selected_location = st.sidebar.selectbox("Location", locations)
    else:
        selected_location = "All"
    
    # Match score filter
    score_col = "match_score" if "match_score" in df.columns else None
    if score_col:
        min_match = st.sidebar.slider("Minimum Match Score", 0, 100, 60)
    else:
        min_match = 0
    
    # Apply filters
    filtered_df = df.copy()
    if selected_industry != "All" and industry_col:
        filtered_df = filtered_df[filtered_df[industry_col] == selected_industry]
    if selected_round != "All" and round_col:
        filtered_df = filtered_df[filtered_df[round_col] == selected_round]
    if selected_location != "All" and location_col:
        filtered_df = filtered_df[filtered_df[location_col] == selected_location]
    if score_col:
        filtered_df = filtered_df[filtered_df[score_col] >= min_match]
    
    # Dashboard metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Startups", len(filtered_df))
    with col2:
        if "funding_amount" in filtered_df.columns:
            total_funding = filtered_df["funding_amount"].sum()
            if isinstance(total_funding, (int, float)):
                st.metric("Total Funding", f"${total_funding/1000000:.1f}M")
            else:
                st.metric("Total Funding", "N/A")
        else:
            st.metric("Total Funding", "N/A")
    with col3:
        if score_col:
            avg_score = filtered_df[score_col].mean()
            st.metric("Avg Match Score", f"{avg_score:.1f}%")
        elif industry_col:
            top_industry = filtered_df[industry_col].value_counts().idxmax() if not filtered_df.empty else "None"
            st.metric("Top Industry", top_industry)
        else:
            st.metric("Startups Found", f"{len(filtered_df)}")
    
    # Charts section
    st.header("Funding Overview")
    
    try:
        if len(filtered_df) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Funding by industry chart
                if industry_col and "funding_amount" in filtered_df.columns:
                    industry_funding = filtered_df.groupby(industry_col)["funding_amount"].sum().reset_index()
                    fig = px.pie(
                        industry_funding, 
                        values="funding_amount", 
                        names=industry_col,
                        title="Funding by Industry",
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Funding rounds distribution
                if round_col:
                    round_counts = filtered_df[round_col].value_counts().reset_index()
                    round_counts.columns = ["Funding Round", "Count"]
                    fig = px.bar(
                        round_counts,
                        x="Funding Round",
                        y="Count",
                        title="Startups by Funding Round",
                        color="Funding Round"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Match score visualization
            if "funding_amount" in filtered_df.columns and score_col:
                fig = px.scatter(
                    filtered_df,
                    x="funding_amount",
                    y=score_col,
                    size="funding_amount",
                    color=industry_col if industry_col else None,
                    hover_name="company_name",
                    title="Match Score vs Funding Amount",
                    labels={"funding_amount": "Funding Amount ($)", "match_score": "Match Score (%)"}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to generate charts. Add more startups or adjust your filters.")
    except Exception as e:
        st.warning(f"Error rendering charts: {str(e)}")
    
    # Startup cards
    st.header("Startup Opportunities")
    
    if filtered_df.empty:
        st.warning("No startups match your current filters. Try adjusting your search criteria.")
    else:
        for i, startup in filtered_df.iterrows():
            company_name = startup.get("company_name", startup.get("name", "Unknown Company"))
            match_score = startup.get("match_score", "N/A")
            
            with st.expander(f"{company_name} - {match_score if isinstance(match_score, (int, float)) else 'N/A'}% Match"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(company_name)
                    st.write(f"**Description:** {startup.get('description', 'N/A')}")
                    
                    if "funding_amount" in startup:
                        funding_amt = startup['funding_amount']
                        if isinstance(funding_amt, (int, float)):
                            st.write(f"**Funding:** ${funding_amt/1000000:.1f}M ({startup.get('funding_round', 'N/A')})")
                        else:
                            st.write(f"**Funding:** {funding_amt} ({startup.get('funding_round', 'N/A')})")
                    
                    st.write(f"**Location:** {startup.get('location', 'N/A')}")
                    st.write(f"**Company Size:** {startup.get('company_size', 'N/A')} employees")
                    st.write(f"**Industry:** {startup.get('industry', 'N/A')}")
                    
                    if "website" in startup:
                        st.write(f"**Website:** [{startup['website']}]({startup['website']})")
                    elif "url" in startup:
                        st.write(f"**Article:** [{startup.get('source', 'Source')}]({startup['url']})")
                
                with col2:
                    if score_col and "match_score" in startup:
                        st.metric("Match Score", f"{startup['match_score']}%")
                    
                    if "tech_stack" in startup and startup["tech_stack"]:
                        st.write("**Tech Stack:**")
                        for tech in startup["tech_stack"]:
                            st.write(f"- {tech}")
                    
                    if "growth_potential" in startup:
                        st.write(f"**Growth Potential:** {startup['growth_potential']}")
                    
                    if "published_date" in startup:
                        st.write(f"**Published:** {startup.get('published_date', 'N/A')}")
                    
                    if "investors" in startup and startup["investors"]:
                        st.write("**Investors:**")
                        for investor in startup["investors"]:
                            st.write(f"- {investor}")
    
    # Footer
    st.markdown("---")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    if use_live_data:
        st.markdown(f"© 2025 Venture-Watch | Powered by Google News API & Groq | Live data as of: {current_time}")
    else:
        st.markdown(f"© 2025 Venture-Watch | Powered by Google News API & Groq | Last updated: {current_time}")

if __name__ == "__main__":
    main() 