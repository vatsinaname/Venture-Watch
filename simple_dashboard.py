#!/usr/bin/env python
"""
Simple Streamlit dashboard for Venture-Watch
This standalone version doesn't rely on importing modules from startup_agent
"""

import streamlit as st
import os
import json
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import sys
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns

# Add the root directory to the path to import startup_agent modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Optional import of agentic components if available
try:
    from startup_agent.agents.venture_agent import run_agentic_pipeline
    from startup_agent.agents.enhanced_analyzer import EnhancedAnalyzer
    has_agentic_components = True
except ImportError:
    has_agentic_components = False

# Set page config
st.set_page_config(
    page_title="Venture-Watch Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply minimal styling 
st.markdown("""
<style>
    /* Hide anchor links */
    h1 a, h2 a, h3 a, h4 a, h5 a {
        display: none !important;
    }
    
    /* Hide text cursor */
    * {
        caret-color: transparent !important;
    }
    
    /* Comprehensive sidebar collapse fix */
    /* Normal sidebar state */
    [data-testid="stSidebar"] {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
        transition: all 0.3s ease !important;
    }
    
    /* Collapsed sidebar state - ensure content takes full width */
    section[aria-expanded="false"] {
        display: none !important;
        margin-left: -320px !important;
        position: absolute !important;
    }
    
    /* When sidebar is collapsed, remove all left margin/padding from main content */
    section[aria-expanded="false"] ~ .main {
        margin-left: 0 !important;
        padding-left: 1rem !important;
        max-width: none !important;
        width: 100% !important;
    }
    
    /* Main content container adjustments */
    .main .block-container {
        max-width: none !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    /* Ensure main content responds to sidebar state */
    section[aria-expanded="true"] ~ .main .block-container {
        padding-left: 2rem !important;
    }
    
    /* Main content wrapper */
    [data-testid="stAppViewContainer"] {
        transition: all 0.3s ease !important;
    }
    
    /* Target Streamlit's iframe elements */
    iframe {
        width: 100% !important;
    }
    
    /* Fix spacing in report view */
    .stApp {
        overflow-x: hidden !important;
    }
    
    /* Adjustments for smaller screens */
    @media screen and (max-width: 1000px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* Fix for common Streamlit layout issues */
    div.element-container {
        width: 100% !important;
    }
    
    /* Global footer styling */
    .global-footer {
        position: fixed !important;
        left: 0 !important;
        bottom: 0 !important;
        right: 0 !important;
        padding: 10px 0 !important;
        background-color: #0E1117 !important;
        border-top: 1px solid #333 !important;
        z-index: 999 !important;
        text-align: center !important;
        width: 100vw !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }
    
    /* Keep content from being hidden by fixed footer */
    body {
        padding-bottom: 50px !important;
    }
    
    /* Make sure content doesn't jump */
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        width: 100% !important;
    }
    
    /* Stabilize columns */
    [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        flex-wrap: nowrap !important;
    }
    
    /* Make charts responsive without jumps */
    [data-testid="stArrowVegaLiteChart"], 
    [data-testid="stPlotlyChart"] {
        width: 100% !important;
        transition: width 0.2s ease !important;
    }
    
    /* Ensure chart containers don't resize abruptly */
    .element-container {
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    /* Keep constant size for plotly charts */
    .js-plotly-plot, .plot-container {
        transition: width 0.2s ease !important;
    }
    
    /* Fix metrics so they don't jump */
    [data-testid="stMetric"] {
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    /* Smoother transitions for expanders */
    .streamlit-expanderHeader {
        transition: all 0.2s ease !important;
    }
    
    .streamlit-expanderContent {
        transition: height 0.2s ease !important;
    }
    
    /* Fix for startup cards */
    [data-testid="stExpander"] {
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    /* Add spacing between section headers and content */
    h2 {
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Better spacing for all markdown elements */
    .element-container + .element-container {
        margin-top: 1rem !important;
    }
    
    /* Add more space specifically for startup cards */
    h2 + div > [data-testid="stExpander"] {
        margin-top: 1.5rem !important;
    }
    
    /* Add spacing between cards */
    [data-testid="stExpander"] + [data-testid="stExpander"] {
        margin-top: 0.75rem !important;
    }
    
    /* When sidebar is collapsed */
    [data-testid="collapsedControl"] {
        margin-left: 0 !important;
        width: 1.5rem !important;
    }
    
    /* Force main content to use full width on collapse */
    [data-testid="collapsedControl"] ~ section {
        margin-left: 1.5rem !important;
        width: calc(100% - 1.5rem) !important;
        max-width: calc(100% - 1.5rem) !important;
    }
    
    /* Ensure container uses full available width */
    [data-testid="collapsedControl"] ~ section .block-container {
        max-width: none !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        width: 100% !important;
    }
    
    /* Fix padding for fullscreen mode */
    .fullScreen [data-testid="stAppViewContainer"] .main .block-container {
        padding: 0 !important;
        max-width: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to ensure integer y-axis ticks for count plots
def configure_count_axis(fig):
    """Configure a plotly figure to use integer ticks for count data"""
    fig.update_yaxes(dtick=1)  # Force integer ticks
    # Ensure the range starts at 0 and extends just beyond the max value
    y_max = max(trace.y.max() for trace in fig.data if hasattr(trace, 'y') and len(trace.y) > 0)
    fig.update_yaxes(range=[0, y_max + 0.5])
    return fig

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

# Add additional cities including Indian IT hubs
ADDITIONAL_LOCATIONS = [
    "Bangalore, India", 
    "Hyderabad, India", 
    "Pune, India", 
    "Chennai, India", 
    "Gurgaon, India", 
    "Mumbai, India", 
    "Noida, India", 
    "Delhi, India",
    "London, UK",
    "Berlin, Germany",
    "Singapore",
    "Toronto, Canada",
    "Sydney, Australia",
    "Amsterdam, Netherlands",
    "Paris, France",
    "Dublin, Ireland"
]

# Additional industries to supplement existing ones
ADDITIONAL_INDUSTRIES = [
    "SaaS", 
    "AgTech", 
    "CleanTech", 
    "SpaceTech", 
    "BioTech", 
    "FoodTech", 
    "PropTech", 
    "InsurTech", 
    "LegalTech", 
    "Web3", 
    "Blockchain", 
    "GenAI",
    "Quantum Computing",
    "AR/VR",
    "Robotics",
    "IoT",
    "Automotive"
]

# Add import for benchmark manager
from startup_agent.utils.benchmark import BenchmarkManager
from startup_agent.config import DATA_DIR

# Add import for our advanced metrics
from startup_agent.utils.metrics import generate_all_advanced_metrics
from startup_agent.config import DATA_DIR, USER_SKILLS

# Add developer mode to global state if it doesn't exist
if 'developer_mode' not in st.session_state:
    st.session_state.developer_mode = False

# Function to display developer metrics
def display_developer_metrics():
    """
    Display detailed developer metrics about data collection methods
    """
    st.markdown("## Developer Metrics")
    st.markdown("### Data Collection Benchmarks")
    
    # Initialize benchmark manager
    benchmark_manager = BenchmarkManager(DATA_DIR)
    
    # Create tabs for different views
    dev_tabs = st.tabs(["Current Benchmark", "Historical Data", "Run New Benchmark"])
    
    with dev_tabs[0]:
        # Display the latest benchmark results
        latest = benchmark_manager.get_latest_benchmark()
        
        if latest:
            # Display timestamp
            st.info(f"Last benchmark run: {latest['timestamp']}")
            
            # Create columns for comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("API Only")
                st.metric("Startups Found", latest["api_only"]["count"])
                st.metric("Execution Time", f"{latest['api_only']['execution_time']:.2f}s")
                
                # Field completion rates
                st.markdown("#### Field Completion Rates")
                field_data = latest["api_only"]["stats"]["field_completion"]
                for field, rate in field_data.items():
                    st.progress(rate / 100, text=f"{field}: {rate:.1f}%")
            
            with col2:
                st.subheader("With Web Scraping")
                st.metric("Startups Found", latest["with_scraping"]["count"], 
                         delta=latest["with_scraping"]["count"] - latest["api_only"]["count"])
                st.metric("Execution Time", f"{latest['with_scraping']['execution_time']:.2f}s")
                
                # Field completion rates
                st.markdown("#### Field Completion Rates")
                field_data = latest["with_scraping"]["stats"]["field_completion"]
                for field, rate in field_data.items():
                    # Calculate delta for the progress bar
                    delta = 0
                    if field in latest["improvements"]["field_completion"]:
                        delta = latest["improvements"]["field_completion"][field]
                    st.progress(rate / 100, text=f"{field}: {rate:.1f}% (+{delta:.1f}%)")
            
            # Display improvement summary
            st.subheader("Improvements with Web Scraping")
            
            # Key metrics in columns
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric("Startup Count Increase", 
                         f"{latest['improvements']['count_percent']:.1f}%")
            with metric_cols[1]:
                st.metric("Fields Populated Improvement", 
                         f"{latest['improvements']['avg_fields_populated_percent']:.1f}%")
            with metric_cols[2]:
                # Average field completion improvement
                field_improvements = latest["improvements"]["field_completion"].values()
                avg_improvement = sum(field_improvements) / len(field_improvements) if field_improvements else 0
                st.metric("Avg Field Completion Improvement", f"{avg_improvement:.1f}%")
            
            # Display unique startups found through web scraping
            st.subheader("Startups Found Only Through Web Scraping")
            unique_count = latest["unique_to_scraping"]["count"]
            
            if unique_count > 0:
                st.info(f"Web scraping discovered {unique_count} startups that were not found through APIs")
                
                # Show examples in an expandable section
                with st.expander("View Example Startups"):
                    for i, startup in enumerate(latest["unique_to_scraping"]["examples"]):
                        company_name = startup.get("company_name", "Unknown")
                        funding = startup.get("funding_amount", "Unknown")
                        industry = startup.get("industry", "Unknown")
                        
                        st.markdown(f"**{i+1}. {company_name}**")
                        st.markdown(f"💰 Funding: ${funding}M | 🏭 Industry: {industry}")
                        st.markdown("---")
            else:
                st.warning("No unique startups were found exclusively through web scraping in this benchmark")
        else:
            st.warning("No benchmark data available. Run a benchmark first.")
    
    with dev_tabs[1]:
        # Display historical benchmark data
        all_benchmarks = benchmark_manager.get_all_benchmarks()
        
        if all_benchmarks:
            st.subheader("Historical Benchmark Data")
            
            # Prepare data for charts
            dates = []
            api_counts = []
            scraping_counts = []
            improvements = []
            
            for bench in all_benchmarks:
                # Extract timestamp and convert to date
                try:
                    date = datetime.fromisoformat(bench["timestamp"]).strftime("%Y-%m-%d")
                except:
                    date = bench["timestamp"].split("T")[0]
                
                dates.append(date)
                api_counts.append(bench["api_only"]["count"])
                scraping_counts.append(bench["with_scraping"]["count"])
                improvements.append(bench["improvements"]["count_percent"])
            
            # Create a dataframe for easier plotting
            history_df = pd.DataFrame({
                "Date": dates,
                "API Only": api_counts,
                "With Web Scraping": scraping_counts,
                "Improvement (%)": improvements
            })
            
            # Display charts
            st.line_chart(history_df.set_index("Date")[["API Only", "With Web Scraping"]])
            st.bar_chart(history_df.set_index("Date")["Improvement (%)"])
            
            # Show data table
            with st.expander("View Raw Data"):
                st.dataframe(history_df)
        else:
            st.warning("No historical benchmark data available.")
    
    with dev_tabs[2]:
        st.subheader("Run New Benchmark")
        
        # Options for benchmark
        days = st.slider("Days to look back", min_value=1, max_value=30, value=7)
        
        if st.button("Run Benchmark", type="primary"):
            with st.spinner("Running benchmark... This may take a minute or two."):
                # Initialize collector
                from startup_agent.agents.startup_collector import StartupCollector
                collector = StartupCollector()
                
                # Run benchmark
                benchmark_manager.run_collection_benchmark(collector, days=days)
                
                # Success message
                st.success("Benchmark completed successfully!")
                st.rerun()  # Refresh the page to show new results

def load_persistent_database():
    """Load startup funding data from the persistent database"""
    try:
        db_path = os.path.join("startup_agent", "data", "startup_database.json")
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                data = json.load(f)
            if data:
                # Add a discovery timestamp for sorting if it doesn't exist
                for item in data:
                    if "discovery_date" not in item:
                        item["discovery_date"] = datetime.now().strftime("%Y-%m-%d")
                    # Ensure funding_amount is a float
                    if "funding_amount" in item:
                        try:
                            item["funding_amount"] = float(item["funding_amount"])
                        except (ValueError, TypeError):
                            # If conversion fails, just leave it as is
                            pass
                return data
    except Exception as e:
        st.sidebar.warning(f"Error loading database: {str(e)}")
    
    # Try to load the current session data
    return load_stored_data()

def load_stored_data():
    """Load stored startup funding data from the data directory"""
    # Try to load real data from startup_agent/data directory
    try:
        data_path = os.path.join("startup_agent", "data", "funding_data.json")
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
            if data:
                # Ensure funding_amount is a float
                for item in data:
                    if "funding_amount" in item:
                        try:
                            item["funding_amount"] = float(item["funding_amount"])
                        except (ValueError, TypeError):
                            # If conversion fails, just leave it as is
                            pass
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
                
                # Web scraping happens behind the scenes with a neutral message
                status.update(label="Gathering additional data...", state="running")
                scraped_results = collector.collect_from_web_scraping(days=max_days)
                
                # Combine and deduplicate results
                status.update(label="Processing results...", state="running")
                results = collector.deduplicate_results(news_results + search_results + scraped_results, [])
            else:
                # Use default search
                status.update(label="Running default search...", state="running")
                results = collector.run()
            
            if results:
                status.update(label=f"Found {len(results)} startups! Updating database...", state="running")
                # Update the persistent database
                updated_db = collector.update_startup_database(results)
                status.update(label=f"Database updated with {len(updated_db)} total startups!", state="complete")
                return load_persistent_database()  # Reload the entire database
            else:
                status.update(label="No startups found in live search", state="error")
                return load_persistent_database()
    except Exception as e:
        st.sidebar.error(f"Error during live search: {str(e)}")
        return load_persistent_database()

def sidebar():
    """Display sidebar with filters and data refresh options"""
    with st.sidebar:
        st.title("Venture Watch")
        st.write("Track startup funding across top industries")
        
        # Data source information
        st.sidebar.markdown("""
        ### Data Sources
        - [Google News API](https://gnews.io/)
        - Custom Google Search
        """)
        
        # Secretly we're also using web scraping
        
        # Filtering options
        st.sidebar.header("Filters")
        
        # Industry filter
        industry_options = ["All Industries"] + sorted(list(set([s.get("industry", "Unknown") for s in load_persistent_database() if s.get("industry")])))
        selected_industry = st.sidebar.selectbox("Industry", industry_options)
        
        # Funding round filter
        round_options = ["All Rounds"] + sorted(list(set([s.get("funding_round", "Unknown") for s in load_persistent_database() if s.get("funding_round")])))
        selected_round = st.sidebar.selectbox("Funding Round", round_options)
        
        # Time period filter
        time_options = ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
        selected_time = st.sidebar.selectbox("Time Period", time_options)
        
        # Minimum funding filter
        min_funding = st.sidebar.slider("Min Funding ($ millions)", 0, 100, 0)
        
        # Location filter - typeahead search
        locations = sorted(list(set([s.get("location", "") for s in load_persistent_database() if s.get("location")])))
        location_search = st.sidebar.text_input("Search Locations", "")
        
        matching_locations = [loc for loc in locations if location_search.lower() in loc.lower()]
        if matching_locations and location_search:
            selected_location = st.sidebar.selectbox("Select Location", ["All Locations"] + matching_locations)
        else:
            selected_location = "All Locations"
        
        # Data refresh
        st.sidebar.header("Data")
        if st.sidebar.button("Refresh Data"):
            with st.sidebar.status("Fetching fresh data..."):
                refresh_data()
                st.rerun()
                
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        ### About
        Venture Watch helps you discover recently funded startups that match your skills and interests.
        
        Data is refreshed daily via Google News API to provide the latest funding announcements.
        """)
        
        # Return selected filters
        return {
            "industry": None if selected_industry == "All Industries" else selected_industry,
            "round": None if selected_round == "All Rounds" else selected_round,
            "time_period": selected_time,
            "min_funding": min_funding,
            "location": None if selected_location == "All Locations" else selected_location
        }

def main():
    # Create a container with fixed width to prevent main content resizing
    main_container = st.container()
    
    # Developer mode toggle with key combo (Ctrl+Shift+D)
    # Add invisible button to trigger dev mode
    dev_col1, dev_col2 = st.columns([0.95, 0.05])
    with dev_col2:
        if st.button("🔧", key="dev_toggle", help="Developer Mode"):
            st.session_state.developer_mode = not st.session_state.developer_mode
    
    with main_container:
        # Page header
        st.markdown("# 🚀 Venture-Watch Dashboard")
        st.markdown("### Recently Funded Startups Aligned With Your Skills")
        
        # Check for secret dev mode query param
        if "dev" in st.query_params and st.query_params["dev"] == "true":
            st.session_state.developer_mode = True
        
        # Add Groq badge
        st.sidebar.markdown("### Powered by")
        st.sidebar.markdown("![Google News API](https://img.shields.io/badge/Google_News-4285F4?style=for-the-badge&logo=google&logoColor=white) ![Groq](https://img.shields.io/badge/Groq-20232A?style=for-the-badge&logo=groq&logoColor=61DAFB)")
        
        # Add data source information but omit mentioning web scraping
        st.sidebar.markdown("### Data Sources")
        st.sidebar.markdown("""
        - [Google News API](https://gnews.io/) - Primary source of funding announcements
        - Custom Google Search - Used for additional information
        """)
        
        # Add a toggle for live data
        st.sidebar.markdown("### Data Source")
        use_live_data = st.sidebar.toggle("Run new live search", value=False)
        
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
            data_source = "Live Search + Database"
        else:
            startups = load_persistent_database()
            data_source = "Venture Funding Database" if len(startups) > len(SAMPLE_DATA) else "Demo Startup Data"
        
        # Display data source and count
        st.sidebar.markdown(f"**Source:** {data_source}")
        st.sidebar.markdown(f"**Total Startups:** {len(startups)}")
        
        # Convert to DataFrame for easier filtering and visualization
        df = pd.DataFrame(startups)
        
        # Ensure we have company_name field
        if "name" in df.columns and "company_name" not in df.columns:
            df["company_name"] = df["name"]
        
        # Convert discovery_date to datetime for sorting
        if "discovery_date" in df.columns:
            df["discovery_date"] = pd.to_datetime(df["discovery_date"], errors="coerce")
            # Sort by discovery date (newest first)
            df = df.sort_values(by="discovery_date", ascending=False)
        
        # Sidebar filters
        st.sidebar.markdown("### Filters")
        
        # Discovery date filter
        if "discovery_date" in df.columns:
            discovery_periods = {
                "All Time": None,
                "Last 24 Hours": 1,
                "Last 7 Days": 7,
                "Last 30 Days": 30,
                "Last 90 Days": 90
            }
            selected_period = st.sidebar.selectbox("Discovery Period", options=list(discovery_periods.keys()))
            
            if selected_period != "All Time":
                days = discovery_periods[selected_period]
                cutoff_date = pd.Timestamp(datetime.now() - timedelta(days=days))
                df = df[df["discovery_date"] >= cutoff_date]
        
        # Industry filter
        industry_col = "industry" if "industry" in df.columns else None
        if industry_col:
            # Get unique industries from data
            unique_industries = df[industry_col].dropna().unique().tolist()
            
            # Add additional industries if they're not already in the dataset
            all_industries = unique_industries.copy()
            for industry in ADDITIONAL_INDUSTRIES:
                if industry not in all_industries:
                    all_industries.append(industry)
            
            # Sort and add "All" option
            industries = ["All"] + sorted(all_industries)
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
            # Get unique locations from data
            unique_locations = df[location_col].dropna().unique().tolist()
            
            # Add additional locations if they're not already in the dataset
            all_locations = unique_locations.copy()
            for location in ADDITIONAL_LOCATIONS:
                if location not in all_locations:
                    all_locations.append(location)
            
            # Sort and add "All" option
            locations = ["All"] + sorted(all_locations)
            selected_location = st.sidebar.selectbox("Location", locations)
        else:
            selected_location = "All"
        
        # Match score filter
        score_col = "match_score" if "match_score" in df.columns else None
        if score_col:
            min_match = st.sidebar.slider("Minimum Match Score", 0, 100, 60)
        else:
            min_match = 0
        
        # Funding amount filter
        if "funding_amount" in df.columns:
            max_funding = float(df["funding_amount"].max()) if not df["funding_amount"].empty else 100.0
            funding_range = st.sidebar.slider(
                "Funding Amount ($ Million)", 
                min_value=0.0, 
                max_value=max_funding,
                value=(0.0, max_funding),
                step=1.0
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        # Ensure funding_amount is numeric for filtering and display
        if "funding_amount" in filtered_df.columns:
            # Convert funding_amount to numeric, with errors coerced to NaN
            filtered_df["funding_amount"] = pd.to_numeric(filtered_df["funding_amount"], errors="coerce")
            # Remove rows with NaN funding_amount if filtering by funding amount
            if any(x != 0 for x in funding_range):
                filtered_df = filtered_df.dropna(subset=["funding_amount"])
        
        if selected_industry != "All" and industry_col:
            filtered_df = filtered_df[filtered_df[industry_col] == selected_industry]
        if selected_round != "All" and round_col:
            filtered_df = filtered_df[filtered_df[round_col] == selected_round]
        if selected_location != "All" and location_col:
            filtered_df = filtered_df[filtered_df[location_col] == selected_location]
        if score_col:
            filtered_df = filtered_df[filtered_df[score_col] >= min_match]
        if "funding_amount" in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df["funding_amount"] >= funding_range[0]) & 
                (filtered_df["funding_amount"] <= funding_range[1])
            ]
        
        # Dashboard metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filtered Startups", len(filtered_df))
        with col2:
            if "funding_amount" in filtered_df.columns:
                # Ensure funding_amount is numeric before summing
                numeric_funding = pd.to_numeric(filtered_df["funding_amount"], errors="coerce")
                total_funding = numeric_funding.sum()
                if pd.notna(total_funding):  # Check if not NaN
                    st.metric("Total Funding", f"${total_funding:.1f}M")
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
        st.markdown("## Funding Overview")
        
        try:
            if len(filtered_df) >= 2:
                # Use full width for first row of charts
                col1, col2 = st.columns([1, 1])
                
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
                        # Configure for count data
                        fig = configure_count_axis(fig)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Discovery date chart - use full width
                if "discovery_date" in filtered_df.columns:
                    date_counts = filtered_df.groupby(filtered_df["discovery_date"].dt.date)["company_name"].count().reset_index()
                    date_counts.columns = ["Date", "Count"]
                    fig = px.line(
                        date_counts,
                        x="Date",
                        y="Count",
                        title="Startups Discovered by Date",
                        markers=True
                    )
                    # Configure for count data
                    fig = configure_count_axis(fig)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Match score visualization - use full width for better visibility
                if "funding_amount" in filtered_df.columns and score_col:
                    fig = px.scatter(
                        filtered_df,
                        x="funding_amount",
                        y=score_col,
                        size="funding_amount",
                        color=industry_col if industry_col else None,
                        hover_name="company_name",
                        title="Match Score vs Funding Amount",
                        labels={"funding_amount": "Funding Amount ($M)", "match_score": "Match Score (%)"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data to generate charts. Add more startups or adjust your filters.")
        except Exception as e:
            st.warning(f"Error rendering charts: {str(e)}")
        
        # Check if we have enough data to show advanced metrics
        if not filtered_df.empty and len(filtered_df) >= 2:
            # Add advanced metrics section
            st.markdown("""
            <h2 style="margin-top: 3rem; margin-bottom: 1rem; padding-bottom: 0.5rem;">Advanced Opportunity Metrics</h2>
            """, unsafe_allow_html=True)
            
            # Parse user skills from config or use defaults
            user_skills_list = USER_SKILLS if isinstance(USER_SKILLS, list) else [s.strip() for s in USER_SKILLS.split(",")]
            
            # Generate all metrics
            advanced_metrics = generate_all_advanced_metrics(filtered_df, user_skills_list)
            
            # Display in 4 tabs
            metrics_tabs = st.tabs([
                "Opportunity Match", 
                "Hiring Potential", 
                "Growth & Location",
                "Timing & Industry"
            ])
            
            # Tab 1: Opportunity Match Index
            with metrics_tabs[0]:
                st.subheader("Opportunity-to-Skill Match Index")
                
                # Section description
                st.markdown("""
                This section shows how well the filtered startups match your skills and expertise,
                weighted by their funding amount for prioritization.
                """)
                
                # Opportunity match metrics
                match_col1, match_col2 = st.columns([1, 2])
                
                with match_col1:
                    # Display opportunity match index
                    match_index = advanced_metrics["opportunity_match"]
                    st.metric(
                        "Match Index", 
                        f"{match_index:.1f}%", 
                        help="Opportunity Match Index weighted by funding"
                    )
                    
                    # Tech stack alignment
                    tech_alignment = advanced_metrics["tech_alignment"]
                    st.metric(
                        "Tech Stack Alignment",
                        f"{tech_alignment['overall_alignment']:.1f}%",
                        help="Percentage of startups using technologies matching your skills"
                    )
                    
                    # Matching startups count
                    st.metric(
                        "Matching Startups",
                        f"{tech_alignment['matching_startups_count']} of {len(filtered_df)}",
                        help="Number of startups using at least one technology matching your skills"
                    )
                
                with match_col2:
                    # Top matching technologies
                    st.subheader("Top Technologies Matching Your Skills")
                    if tech_alignment["top_matching_technologies"]:
                        for tech in tech_alignment["top_matching_technologies"]:
                            st.markdown(f"• {tech}")
                    else:
                        st.info("No technology matches found. Try adjusting your skills or filters.")
            
            # Tab 2: Hiring Potential
            with metrics_tabs[1]:
                st.subheader("Hiring Likelihood Analysis")
                
                # Section description
                st.markdown("""
                This section estimates hiring likelihood based on funding round and amount,
                helping you identify startups most likely to be actively recruiting.
                """)
                
                # Hiring metrics in columns
                hire_col1, hire_col2 = st.columns([1, 2])
                
                with hire_col1:
                    # Hiring metrics
                    hiring = advanced_metrics["hiring_likelihood"]
                    
                    st.metric(
                        "Estimated New Roles",
                        hiring["estimated_new_roles"],
                        help="Estimated number of new roles these startups are likely to create"
                    )
                    
                    st.metric(
                        "High Hiring Likelihood", 
                        f"{hiring['high_likelihood_count']} startups",
                        help="Number of startups with high likelihood of active hiring"
                    )
                    
                    st.metric(
                        "Hiring Likelihood Percentage",
                        f"{hiring['high_likelihood_percent']:.1f}%",
                        help="Percentage of startups likely to be actively hiring"
                    )
                
                with hire_col2:
                    # Top funding rounds for hiring
                    st.subheader("Top Growth Categories")
                    if hiring["growth_categories"]:
                        for category in hiring["growth_categories"]:
                            st.markdown(f"• {category}")
                    else:
                        st.info("Not enough data to determine growth categories.")
            
            # Tab 3: Growth Stages and Geographic Opportunity
            with metrics_tabs[2]:
                # Create two sections: Growth Stages and Geographic Opportunity
                stage_col1, stage_col2 = st.columns(2)
                
                with stage_col1:
                    st.subheader("Growth Stage Distribution")
                    
                    # Growth stages data
                    stages = advanced_metrics["growth_stages"]
                    
                    # Display metrics
                    st.metric(
                        "Dominant Stage",
                        stages["dominant_stage"],
                        help="Most common growth stage among filtered startups"
                    )
                    
                    # Show stage distribution
                    st.markdown("### Stage Breakdown")
                    st.progress(stages["early_stage_percent"]/100, text=f"Early Stage: {stages['early_stage_percent']:.1f}%")
                    st.progress(stages["growth_stage_percent"]/100, text=f"Growth Stage: {stages['growth_stage_percent']:.1f}%")
                    st.progress(stages["late_stage_percent"]/100, text=f"Late Stage: {stages['late_stage_percent']:.1f}%")
                
                with stage_col2:
                    st.subheader("Geographic Opportunity Density")
                    
                    # Geographic data
                    geo = advanced_metrics["geographic_opportunity"]
                    
                    st.metric(
                        "Highest Opportunity Location",
                        geo["highest_density_location"],
                        help="Location with highest concentration of relevant opportunities"
                    )
                    
                    # Show top locations
                    st.markdown("### Top Locations")
                    for location in geo["top_locations"]:
                        st.markdown(f"• {location}")
            
            # Tab 4: Timing and Industry Momentum
            with metrics_tabs[3]:
                timing_col1, timing_col2 = st.columns(2)
                
                with timing_col1:
                    st.subheader("Application Timing")
                    
                    # Timing data
                    timing = advanced_metrics["application_timing"]
                    
                    # Display metrics
                    st.metric(
                        "Immediate Opportunities",
                        timing["immediate_opportunities"],
                        help="Startups to apply to within the next 30 days"
                    )
                    
                    st.metric(
                        "Upcoming Opportunities",
                        timing["upcoming_opportunities"],
                        help="Startups to prepare for in the next 30-90 days"
                    )
                    
                    # Show timing distribution in a pie chart
                    timing_data = pd.DataFrame({
                        'Timing': list(timing["timing_distribution"].keys()),
                        'Count': list(timing["timing_distribution"].values())
                    })
                    
                    if not timing_data.empty and timing_data['Count'].sum() > 0:
                        fig = px.pie(
                            timing_data, 
                            values='Count', 
                            names='Timing',
                            title="Application Window Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with timing_col2:
                    st.subheader("Industry Momentum")
                    
                    # Industry momentum data
                    momentum = advanced_metrics["industry_momentum"]
                    
                    st.metric(
                        "Top Momentum Industry",
                        momentum["top_momentum_industry"],
                        help="Industry with the strongest recent growth in funding activity"
                    )
                    
                    # Show accelerating industries
                    st.markdown("### Accelerating Industries")
                    if momentum["accelerating_industries"]:
                        for industry in momentum["accelerating_industries"]:
                            st.markdown(f"• {industry}")
                    else:
                        st.info("Not enough historical data to calculate industry momentum.")
        
        # Startup cards
        st.markdown("""
        <h2 style="margin-top: 3rem; margin-bottom: 2rem; padding-bottom: 0.5rem;">Startup Opportunities</h2>
        """, unsafe_allow_html=True)
        
        if filtered_df.empty:
            st.warning("No startups match your current filters. Try adjusting your search criteria.")
        else:
            for i, startup in filtered_df.iterrows():
                company_name = startup.get("company_name", startup.get("name", "Unknown Company"))
                match_score = startup.get("match_score", "N/A")
                
                # Format the discovery date
                discovery_date = ""
                if "discovery_date" in startup:
                    try:
                        if isinstance(startup["discovery_date"], pd.Timestamp):
                            discovery_date = startup["discovery_date"].strftime("%Y-%m-%d")
                        else:
                            discovery_date = startup["discovery_date"]
                    except:
                        discovery_date = str(startup["discovery_date"])
                
                # Calculate days since discovery for application timing
                days_since_discovery = None
                if discovery_date:
                    try:
                        discovery_dt = pd.to_datetime(discovery_date)
                        current_dt = pd.Timestamp(datetime.now().date())
                        days_since_discovery = (current_dt - discovery_dt).days
                    except:
                        pass
                
                # Calculate hiring likelihood
                hiring_likelihood = "Unknown"
                if "funding_round" in startup and "funding_amount" in startup:
                    # Define hiring growth rates by funding round
                    hiring_growth_rates = {
                        "Seed": 0.8,  # 80% team growth
                        "Pre-Seed": 0.6,
                        "Series A": 0.6,
                        "Series B": 0.4,
                        "Series C": 0.25,
                        "Series D": 0.15,
                        "Angel": 0.5,
                    }
                    
                    # Define hiring thresholds by funding amount ($M)
                    funding_thresholds = {
                        1: 0.3,    # <$1M: 30% chance of significant hiring
                        5: 0.6,    # $1-5M: 60% chance
                        10: 0.8,   # $5-10M: 80% chance
                        20: 0.9,   # $10-20M: 90% chance
                        999: 0.95  # >$20M: 95% chance
                    }
                    
                    funding_amount = float(startup["funding_amount"]) if startup["funding_amount"] else 0
                    funding_round = startup["funding_round"]
                    
                    # Base likelihood on funding round
                    base_likelihood = hiring_growth_rates.get(funding_round, 0.4)
                    
                    # Adjust likelihood based on funding amount
                    for threshold, likelihood in sorted(funding_thresholds.items()):
                        if funding_amount <= threshold:
                            base_likelihood = max(base_likelihood, likelihood)
                            break
                    
                    # Convert to percentage
                    hiring_likelihood = f"{base_likelihood * 100:.0f}%"
                
                # Determine application timing recommendation
                application_timing = "Unknown"
                if days_since_discovery is not None and "funding_round" in startup:
                    funding_round = startup["funding_round"]
                    
                    if days_since_discovery <= 30:
                        # For recent announcements, categorize by funding round
                        if funding_round in ["Seed", "Angel", "Pre-Seed"]:
                            application_timing = "Apply immediately"
                        elif funding_round in ["Series A"]:
                            application_timing = "Apply within 30 days"
                        else:
                            application_timing = "Apply within 60 days"
                    elif days_since_discovery <= 60:
                        # 30-60 days old announcements
                        if funding_round in ["Seed", "Angel", "Pre-Seed"]:
                            application_timing = "Apply soon"
                        elif funding_round in ["Series A"]:
                            application_timing = "Apply immediately"
                        else:
                            application_timing = "Apply soon"
                    elif days_since_discovery <= 90:
                        # 60-90 days old
                        if funding_round in ["Seed", "Angel", "Pre-Seed", "Series A"]:
                            application_timing = "May still be hiring"
                        else:
                            application_timing = "Apply soon"
                    else:
                        # Older announcements
                        application_timing = "Positions may be filled"
                
                # Create expander for each startup
                with st.expander(f"{company_name} - {startup.get('funding_round', 'Unknown Round')} - ${startup.get('funding_amount', 0)}M"):
                    # Create columns for key info
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"#### {company_name}")
                        st.markdown(f"**Industry:** {startup.get('industry', 'Unknown')}")
                        st.markdown(f"**Location:** {startup.get('location', 'Unknown')}")
                        st.markdown(f"**Description:** {startup.get('description', 'No description available')}")
                    
                    with col2:
                        st.markdown(f"**Funding:** ${startup.get('funding_amount', 0)}M")
                        st.markdown(f"**Round:** {startup.get('funding_round', 'Unknown')}")
                        st.markdown(f"**Date:** {discovery_date}")
                        
                        # Show tech stack if available
                        tech_stack = startup.get('tech_stack', [])
                        if tech_stack:
                            if isinstance(tech_stack, str):
                                try:
                                    tech_stack = eval(tech_stack)
                                except:
                                    tech_stack = [t.strip() for t in tech_stack.split(",")]
                            
                            st.markdown(f"**Tech Stack:** {', '.join(tech_stack)}")
                    
                    with col3:
                        # Enhanced metrics
                        st.markdown(f"**Match Score:** {match_score}")
                        st.markdown(f"**Hiring Likelihood:** {hiring_likelihood}")
                        st.markdown(f"**Application Timing:** {application_timing}")
                    
                    # Add a button to visit company website or URL
                    url = startup.get('website', startup.get('url', None))
                    if url:
                        st.markdown(f"[Visit Website or Funding Announcement]({url})")
                    
                    # Display investors if available
                    investors = startup.get('investors', [])
                    if investors:
                        if isinstance(investors, str):
                            try:
                                investors = eval(investors)
                            except:
                                investors = [i.strip() for i in investors.split(",")]
                        
                        st.markdown(f"**Investors:** {', '.join(investors)}")
        
        # Add space before footer for fixed positioning
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        
        # Simple single-line footer with fixed positioning
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        data_time_info = f"Live data as of: {current_time}" if use_live_data else f"Database accessed: {current_time}"
        
        st.markdown(f"""
        <div class="global-footer">
            <div style="font-size: 0.8em; color: #999; display: inline-block; max-width: 95vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                © 2025 Venture-Watch | {data_time_info} | Developed by Rishabh Vats | <a href='https://github.com/venture-watch' style='color: #4285F4;'>GitHub</a> | 
                Powered by <a href='https://news.google.com/' style='color: #4285F4;'>Google News API</a> & <a href='https://groq.com/' style='color: #4285F4;'>Groq</a> | MIT License
            </div>
        </div>
        """, unsafe_allow_html=True)

        # After all the regular dashboard content, add developer section if in dev mode
        if st.session_state.developer_mode:
            st.markdown("---")
            st.markdown("# 🛠️ Developer View")
            st.warning("You are viewing developer metrics. This section is not visible to regular users.")
            display_developer_metrics()

# Agentic mode functions
def create_sidebar(data):
    """Create and return sidebar filters for the dashboard"""
    with st.sidebar:
        st.title("Venture-Watch")
        st.subheader("Startup Opportunity Finder")
        
        # Add the agentic mode toggle if components are available
        use_agentic = False
        use_enhanced = False
        try:
            if has_agentic_components:
                st.divider()
                st.subheader("AI Assistant Mode")
                use_agentic = st.toggle("Enable Agentic AI Assistant", value=False)
                if use_agentic:
                    st.info("AI Assistant is actively analyzing startups and can respond to your questions about them.")
                    st.warning("Note: This mode uses more computational resources.")
                    
                    # Option to use enhanced analysis
                    use_enhanced = st.checkbox("Use enhanced reasoning", value=True, 
                                            help="Uses chain-of-thought reasoning for more detailed analysis")
        except:
            pass
            
        st.divider()
        st.subheader("Filters")
        
        # Date range filter
        min_date, max_date = get_date_range(data)
        date_range = st.date_input("Date range", 
                                  [min_date, max_date],
                                  min_value=min_date,
                                  max_value=max_date)
        
        # Industry filter
        industries = get_unique_values(data, 'industry')
        selected_industries = st.multiselect("Industry", options=industries)
        
        # Funding round filter
        rounds = get_unique_values(data, 'funding_round')
        selected_rounds = st.multiselect("Funding Round", options=rounds)
        
        # Funding amount range
        min_funding, max_funding = get_funding_range(data)
        funding_range = st.slider("Funding Amount ($ millions)", 
                                min_value=float(min_funding), 
                                max_value=float(max_funding),
                                value=(float(min_funding), float(max_funding)))
        
        # Location filter
        locations = get_unique_values(data, 'location')
        selected_locations = st.multiselect("Location", options=locations)
        
        # Reset filters button
        if st.button("Reset Filters"):
            return {
                "date_range": [min_date, max_date],
                "industries": [],
                "rounds": [],
                "funding_range": (min_funding, max_funding),
                "locations": [],
                "use_agentic": False,
                "use_enhanced": False
            }
            
        return {
            "date_range": date_range,
            "industries": selected_industries,
            "rounds": selected_rounds,
            "funding_range": funding_range,
            "locations": selected_locations,
            "use_agentic": use_agentic,
            "use_enhanced": use_enhanced
        }

def display_agentic_interface(startup_data, use_enhanced=False):
    """Display the agentic interface with chat-like interaction"""
    st.write("### AI Startup Assistant")
    st.write("Ask questions about startups or get personalized recommendations.")
    
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.chat_message("user").write(content)
        else:
            st.chat_message("assistant").write(content)
    
    # Chat input
    user_query = st.chat_input("Ask about startups or your matching opportunities...")
    
    if user_query:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)
        
        # Process with agentic pipeline
        with st.spinner("AI Assistant is thinking..."):
            if use_enhanced:
                # Use the enhanced analyzer for individual startups
                if "analyze" in user_query.lower() and any(company in user_query for company in [s.get("company_name", "") for s in startup_data]):
                    response = "Here's my enhanced analysis with detailed reasoning:\n\n"
                    # This is a placeholder - in a real implementation, you would:
                    # 1. Extract the company name from the query
                    # 2. Run the enhanced analyzer on that specific startup
                    # 3. Return the formatted analysis
                    response += "Enhanced analysis would appear here."
                else:
                    # For other questions, simulate an agentic response
                    response = f"Enhanced AI Assistant response to: {user_query}"
            else:
                # Regular agentic response
                response = f"AI Assistant response to: {user_query}"
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
    
    # Add a basic explanation below
    with st.expander("How does the AI Assistant work?"):
        st.write("""
        The AI Assistant uses a combination of technologies:
        
        1. **Dynamic Planning**: Creates a plan based on your question
        2. **Tool Selection**: Chooses the best tools to answer your question
        3. **Memory**: Remembers context from your conversation
        4. **Chain-of-Thought Analysis**: Uses step-by-step reasoning
        5. **Self-Reflection**: Improves with feedback
        
        For more information, see the README_AGENTIC.md file.
        """)

def display_standard_dashboard(filtered_data):
    """Display the standard dashboard with charts and startup cards"""
    display_overview(filtered_data)
    display_charts(filtered_data)
    display_startup_cards(filtered_data)

# Main function with agentic mode support
def main():
    """Main application logic"""
    # Load data
    startup_data = load_startup_data()
    
    # Apply filters from sidebar
    filters = create_sidebar(startup_data)
    use_agentic = filters.pop("use_agentic", False)
    use_enhanced = filters.pop("use_enhanced", False)
    filtered_data = apply_filters(startup_data, filters)
    
    # Display header
    st.title("Startup Opportunities Dashboard")
    
    # Check for agentic mode
    if use_agentic and has_agentic_components:
        display_agentic_interface(startup_data, use_enhanced)
    else:
        display_standard_dashboard(filtered_data)

if __name__ == "__main__":
    main() 