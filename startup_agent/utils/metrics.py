"""
Advanced metrics calculations for the Venture-Watch dashboard.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

def calculate_opportunity_match_index(df: pd.DataFrame) -> float:
    """
    Calculate opportunity-to-skill match index weighted by funding amount
    
    Args:
        df: DataFrame containing startup data with match_score and funding_amount
        
    Returns:
        Weighted average match score
    """
    if df.empty or "match_score" not in df.columns or "funding_amount" not in df.columns:
        return 0.0
    
    # Convert to numeric and handle missing values
    df = df.copy()
    df["match_score"] = pd.to_numeric(df["match_score"], errors="coerce")
    df["funding_amount"] = pd.to_numeric(df["funding_amount"], errors="coerce")
    
    # Drop rows with missing values
    df = df.dropna(subset=["match_score", "funding_amount"])
    
    if df.empty:
        return 0.0
    
    # Calculate weighted average
    weighted_avg = np.average(df["match_score"], weights=df["funding_amount"])
    return weighted_avg

def estimate_hiring_likelihood(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Estimate hiring likelihood based on funding round and amount
    
    Args:
        df: DataFrame containing startup data with funding_round and funding_amount
        
    Returns:
        Dictionary with hiring likelihood metrics
    """
    if df.empty:
        return {
            "high_likelihood_count": 0,
            "high_likelihood_percent": 0,
            "estimated_new_roles": 0,
            "growth_categories": []
        }
    
    # Define hiring growth rates by funding round (typical % team growth in 6 months)
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
    
    df = df.copy()
    df["funding_amount"] = pd.to_numeric(df["funding_amount"], errors="coerce")
    
    # Calculate hiring likelihood for each startup
    likelihoods = []
    for _, row in df.iterrows():
        funding_amount = row.get("funding_amount", 0)
        funding_round = row.get("funding_round", "Unknown")
        
        # Base likelihood on funding round
        base_likelihood = hiring_growth_rates.get(funding_round, 0.4)
        
        # Adjust likelihood based on funding amount
        for threshold, likelihood in sorted(funding_thresholds.items()):
            if funding_amount <= threshold:
                base_likelihood = max(base_likelihood, likelihood)
                break
        
        likelihoods.append(base_likelihood)
    
    df["hiring_likelihood"] = likelihoods
    
    # Calculate metrics
    high_likelihood = df[df["hiring_likelihood"] >= 0.7]
    high_likelihood_count = len(high_likelihood)
    high_likelihood_percent = (high_likelihood_count / len(df)) * 100 if len(df) > 0 else 0
    
    # Estimate total new roles
    # Assuming average startup size of 15 people for seed, scaling up by round
    startup_sizes = {
        "Pre-Seed": 5,
        "Seed": 10,
        "Angel": 8,
        "Series A": 25,
        "Series B": 50,
        "Series C": 100,
        "Series D": 200,
    }
    
    new_roles = 0
    for _, row in df.iterrows():
        funding_round = row.get("funding_round", "Seed")
        likelihood = row.get("hiring_likelihood", 0)
        base_size = startup_sizes.get(funding_round, 15)
        new_roles += base_size * hiring_growth_rates.get(funding_round, 0.4) * likelihood
    
    # Find top growth categories (funding rounds with most hiring)
    round_hiring = df.groupby("funding_round").agg(
        {"hiring_likelihood": "mean", "funding_amount": "sum"}
    ).sort_values("hiring_likelihood", ascending=False)
    
    growth_categories = [
        f"{round}: {likelihood*100:.0f}% likelihood" 
        for round, likelihood in round_hiring["hiring_likelihood"].items()
    ][:3]
    
    return {
        "high_likelihood_count": high_likelihood_count,
        "high_likelihood_percent": high_likelihood_percent,
        "estimated_new_roles": int(new_roles),
        "growth_categories": growth_categories
    }

def calculate_tech_stack_alignment(df: pd.DataFrame, user_skills: List[str]) -> Dict[str, Any]:
    """
    Calculate technology stack alignment with user skills
    
    Args:
        df: DataFrame containing startup data
        user_skills: List of user skills to match against
        
    Returns:
        Dictionary with tech alignment metrics
    """
    if df.empty or not user_skills:
        return {
            "overall_alignment": 0,
            "matching_startups_count": 0,
            "matching_startups_percent": 0,
            "top_matching_technologies": []
        }
    
    # Normalize user skills (lowercase for matching)
    user_skills = [skill.lower() for skill in user_skills]
    
    # Track technologies across startups
    all_technologies = []
    matching_technologies = []
    matching_startups = 0
    
    for _, row in df.iterrows():
        # Get technologies from tech_stack or description
        tech_stack = row.get("tech_stack", [])
        
        # If tech_stack is a string, try to convert it to a list
        if isinstance(tech_stack, str):
            try:
                tech_stack = eval(tech_stack)  # Try to parse if it's a string representation of a list
            except:
                tech_stack = [t.strip() for t in tech_stack.split(",")]
        
        if not tech_stack and "description" in row:
            # Extract possible technologies from description
            description = row["description"].lower()
            for skill in user_skills:
                if skill in description:
                    tech_stack.append(skill)
        
        # Add to all technologies list
        all_technologies.extend([tech.lower() for tech in tech_stack])
        
        # Check for matches with user skills
        matches = [tech for tech in tech_stack if tech.lower() in user_skills]
        matching_technologies.extend(matches)
        
        if matches:
            matching_startups += 1
    
    # Calculate metrics
    matching_startups_percent = (matching_startups / len(df)) * 100 if len(df) > 0 else 0
    
    # Get frequency of each matching technology
    tech_counts = {}
    for tech in matching_technologies:
        tech_lower = tech.lower()
        tech_counts[tech_lower] = tech_counts.get(tech_lower, 0) + 1
    
    # Sort by frequency
    top_matching_technologies = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate overall alignment (percentage of startups using user's skills)
    overall_alignment = matching_startups_percent
    
    return {
        "overall_alignment": overall_alignment,
        "matching_startups_count": matching_startups,
        "matching_startups_percent": matching_startups_percent,
        "top_matching_technologies": [f"{tech} ({count})" for tech, count in top_matching_technologies]
    }

def analyze_growth_stages(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze growth stages distribution of startups
    
    Args:
        df: DataFrame containing startup data
        
    Returns:
        Dictionary with growth stage metrics
    """
    if df.empty:
        return {
            "stage_distribution": {},
            "early_stage_percent": 0,
            "growth_stage_percent": 0,
            "late_stage_percent": 0,
            "dominant_stage": "Unknown"
        }
    
    # Define growth stage categories
    early_stages = ["Pre-Seed", "Seed", "Angel"]
    growth_stages = ["Series A", "Series B"]
    late_stages = ["Series C", "Series D", "Series E", "Late Stage"]
    
    # Count startups by funding round
    if "funding_round" in df.columns:
        stage_counts = df["funding_round"].value_counts().to_dict()
    else:
        return {
            "stage_distribution": {},
            "early_stage_percent": 0,
            "growth_stage_percent": 0,
            "late_stage_percent": 0,
            "dominant_stage": "Unknown"
        }
    
    # Calculate stage percentages
    total = len(df)
    early_count = sum(stage_counts.get(stage, 0) for stage in early_stages)
    growth_count = sum(stage_counts.get(stage, 0) for stage in growth_stages)
    late_count = sum(stage_counts.get(stage, 0) for stage in late_stages)
    
    early_percent = (early_count / total) * 100 if total > 0 else 0
    growth_percent = (growth_count / total) * 100 if total > 0 else 0
    late_percent = (late_count / total) * 100 if total > 0 else 0
    
    # Determine dominant stage
    stage_percents = {
        "Early Stage": early_percent,
        "Growth Stage": growth_percent,
        "Late Stage": late_percent
    }
    dominant_stage = max(stage_percents.items(), key=lambda x: x[1])[0]
    
    return {
        "stage_distribution": stage_counts,
        "early_stage_percent": early_percent,
        "growth_stage_percent": growth_percent,
        "late_stage_percent": late_percent,
        "dominant_stage": dominant_stage
    }

def calculate_geographic_opportunity(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate geographic opportunity density
    
    Args:
        df: DataFrame containing startup data
        
    Returns:
        Dictionary with geographic opportunity metrics
    """
    if df.empty or "location" not in df.columns:
        return {
            "top_locations": [],
            "opportunity_density": {},
            "highest_density_location": "Unknown"
        }
    
    # Count startups by location
    location_counts = df["location"].value_counts()
    
    # Calculate average funding by location
    if "funding_amount" in df.columns:
        location_funding = df.groupby("location")["funding_amount"].mean()
        
        # Combine counts and funding for density score
        opportunity_density = {}
        for location in location_counts.index:
            count = location_counts[location]
            avg_funding = location_funding.get(location, 0)
            
            # Simple density score: count * log(avg_funding + 1)
            # Log scale prevents very large funding amounts from dominating
            density_score = count * np.log1p(avg_funding)
            opportunity_density[location] = density_score
        
        # Sort by density score
        sorted_density = sorted(opportunity_density.items(), key=lambda x: x[1], reverse=True)
        top_locations = [f"{loc} ({count})" for loc, count in sorted_density[:5]]
        
        highest_density = sorted_density[0][0] if sorted_density else "Unknown"
    else:
        # Just use counts if funding data is not available
        top_locations = [f"{loc} ({count})" for loc, count in location_counts.items()[:5]]
        highest_density = location_counts.index[0] if not location_counts.empty else "Unknown"
        opportunity_density = location_counts.to_dict()
    
    return {
        "top_locations": top_locations,
        "opportunity_density": opportunity_density,
        "highest_density_location": highest_density
    }

def analyze_industry_momentum(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze industry momentum based on funding patterns
    
    Args:
        df: DataFrame containing startup data
        
    Returns:
        Dictionary with industry momentum metrics
    """
    if df.empty or "industry" not in df.columns or "discovery_date" not in df.columns:
        return {
            "momentum_scores": {},
            "accelerating_industries": [],
            "top_momentum_industry": "Unknown"
        }
    
    # Ensure discovery_date is datetime
    df = df.copy()
    df["discovery_date"] = pd.to_datetime(df["discovery_date"], errors="coerce")
    
    # Filter out rows with invalid dates
    df = df.dropna(subset=["discovery_date"])
    
    if df.empty:
        return {
            "momentum_scores": {},
            "accelerating_industries": [],
            "top_momentum_industry": "Unknown"
        }
    
    # Calculate date ranges for recent vs older
    latest_date = df["discovery_date"].max()
    mid_date = latest_date - timedelta(days=30)  # Past 30 days vs 30-60 days ago
    older_date = latest_date - timedelta(days=60)
    
    recent_df = df[df["discovery_date"] >= mid_date]
    older_df = df[(df["discovery_date"] < mid_date) & (df["discovery_date"] >= older_date)]
    
    # Count funding events by industry for each period
    if not recent_df.empty and not older_df.empty:
        recent_counts = recent_df["industry"].value_counts()
        older_counts = older_df["industry"].value_counts()
        
        # Calculate momentum scores (% change in funding events)
        momentum_scores = {}
        for industry in set(recent_counts.index) | set(older_counts.index):
            recent = recent_counts.get(industry, 0)
            older = older_counts.get(industry, 0)
            
            if older == 0:
                # New industry, assign high momentum
                momentum_scores[industry] = 100 if recent > 0 else 0
            else:
                # Calculate percentage change
                momentum_scores[industry] = ((recent - older) / older) * 100
        
        # Get accelerating industries (positive momentum)
        accelerating = {k: v for k, v in momentum_scores.items() if v > 0}
        accelerating_sorted = sorted(accelerating.items(), key=lambda x: x[1], reverse=True)
        
        accelerating_industries = [
            f"{industry} (+{momentum:.1f}%)" for industry, momentum in accelerating_sorted[:3]
        ]
        
        top_momentum = accelerating_sorted[0][0] if accelerating_sorted else "None"
    else:
        # Not enough historical data
        momentum_scores = {}
        industries = df["industry"].value_counts()
        top_industries = list(industries.index)[:3]
        accelerating_industries = [f"{industry} (new)" for industry in top_industries]
        top_momentum = top_industries[0] if top_industries else "Unknown"
    
    return {
        "momentum_scores": momentum_scores,
        "accelerating_industries": accelerating_industries,
        "top_momentum_industry": top_momentum
    }

def estimate_application_timing(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Estimate optimal application timing for startups
    
    Args:
        df: DataFrame containing startup data
        
    Returns:
        Dictionary with application timing metrics
    """
    if df.empty or "discovery_date" not in df.columns:
        return {
            "immediate_opportunities": 0,
            "upcoming_opportunities": 0,
            "timing_distribution": {}
        }
    
    # Ensure discovery_date is datetime
    df = df.copy()
    df["discovery_date"] = pd.to_datetime(df["discovery_date"], errors="coerce")
    
    # Filter out rows with invalid dates
    df = df.dropna(subset=["discovery_date"])
    
    if df.empty:
        return {
            "immediate_opportunities": 0,
            "upcoming_opportunities": 0,
            "timing_distribution": {}
        }
    
    # Calculate days since funding announcement
    today = pd.Timestamp(datetime.now().date())
    df["days_since_discovery"] = (today - df["discovery_date"].dt.floor("D")).dt.days
    
    # Define timing windows based on funding round and days since discovery
    # Seed/Angel: Apply immediately (0-30 days)
    # Series A: Apply within 30-60 days
    # Series B+: Apply within 60-90 days
    timing_windows = {
        "Immediate (0-30 days)": 0,
        "Soon (30-60 days)": 0,
        "Upcoming (60-90 days)": 0,
        "Future (90+ days)": 0
    }
    
    for _, row in df.iterrows():
        days = row.get("days_since_discovery", 0)
        round = row.get("funding_round", "Unknown")
        
        if days <= 30:
            # For recent announcements, categorize by funding round
            if round in ["Seed", "Angel", "Pre-Seed"]:
                timing_windows["Immediate (0-30 days)"] += 1
            elif round in ["Series A"]:
                timing_windows["Soon (30-60 days)"] += 1
            else:
                timing_windows["Upcoming (60-90 days)"] += 1
        elif days <= 60:
            # 30-60 days old announcements
            if round in ["Seed", "Angel", "Pre-Seed"]:
                timing_windows["Soon (30-60 days)"] += 1
            elif round in ["Series A"]:
                timing_windows["Immediate (0-30 days)"] += 1
            else:
                timing_windows["Soon (30-60 days)"] += 1
        elif days <= 90:
            # 60-90 days old
            if round in ["Seed", "Angel", "Pre-Seed", "Series A"]:
                timing_windows["Upcoming (60-90 days)"] += 1
            else:
                timing_windows["Immediate (0-30 days)"] += 1
        else:
            # Older announcements
            timing_windows["Future (90+ days)"] += 1
    
    return {
        "immediate_opportunities": timing_windows["Immediate (0-30 days)"],
        "upcoming_opportunities": timing_windows["Soon (30-60 days)"] + timing_windows["Upcoming (60-90 days)"],
        "timing_distribution": timing_windows
    }

def generate_all_advanced_metrics(df: pd.DataFrame, user_skills: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate all advanced metrics for the dashboard
    
    Args:
        df: DataFrame containing startup data
        user_skills: List of user skills (optional)
        
    Returns:
        Dictionary with all metrics
    """
    if user_skills is None:
        # Default user skills if none provided
        user_skills = ["python", "javascript", "react", "machine learning", "data analysis"]
    
    return {
        "opportunity_match": calculate_opportunity_match_index(df),
        "hiring_likelihood": estimate_hiring_likelihood(df),
        "tech_alignment": calculate_tech_stack_alignment(df, user_skills),
        "growth_stages": analyze_growth_stages(df),
        "geographic_opportunity": calculate_geographic_opportunity(df),
        "industry_momentum": analyze_industry_momentum(df),
        "application_timing": estimate_application_timing(df)
    } 