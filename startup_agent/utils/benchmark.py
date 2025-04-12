import logging
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BenchmarkManager:
    """Utility to benchmark data collection performance across different methods"""
    
    def __init__(self, data_dir: Path):
        """Initialize the benchmark manager with a data directory"""
        self.data_dir = data_dir
        self.benchmark_dir = data_dir / "benchmarks"
        self.benchmark_dir.mkdir(exist_ok=True, parents=True)
        self.benchmark_file = self.benchmark_dir / "collection_benchmarks.json"
        self.latest_results = None
        
    def run_collection_benchmark(self, collector, days=7) -> Dict[str, Any]:
        """
        Run a benchmark comparing data collection with and without Ninja Squirrel Gathering
        
        Args:
            collector: The StartupCollector instance to benchmark
            days: Number of days to look back
            
        Returns:
            Dictionary with benchmark results
        """
        logger.info(f"Running collection benchmark for {days} days lookback")
        
        # Store original setting
        original_setting = collector.use_ninja_squirrels
        
        # First run: API only
        logger.info("Running benchmark with API only (no Ninja Squirrels)")
        start_time_api = time.time()
        collector.use_ninja_squirrels = False
        
        # Get news results
        news_results = collector.collect_from_google_news(days=days)
        logger.info(f"API only: Collected {len(news_results)} results from Google News")
        
        # Get custom search results
        search_results = collector.collect_from_custom_search()
        logger.info(f"API only: Collected {len(search_results)} results from Google Custom Search")
        
        # Combine and deduplicate
        api_only_results = collector.deduplicate_results(news_results + search_results, [])
        api_time = time.time() - start_time_api
        logger.info(f"API only: Found {len(api_only_results)} unique results in {api_time:.2f} seconds")
        
        # Second run: With Ninja Squirrel Gathering
        logger.info("Running benchmark with Ninja Squirrel Gathering enabled")
        start_time_squirrels = time.time()
        collector.use_ninja_squirrels = True
        
        # Get news results again (to be consistent)
        news_results = collector.collect_from_google_news(days=days)
        logger.info(f"With Squirrels: Collected {len(news_results)} results from Google News")
        
        # Get custom search results again
        search_results = collector.collect_from_custom_search()
        logger.info(f"With Squirrels: Collected {len(search_results)} results from Google Custom Search")
        
        # Get Ninja Squirrel results
        squirrel_results = collector.collect_from_ninja_squirrels(days=days)
        logger.info(f"With Squirrels: Collected {len(squirrel_results)} results from Ninja Squirrel Gathering")
        
        # Combine and deduplicate
        combined_results = collector.deduplicate_results(news_results + search_results + squirrel_results, [])
        squirrels_time = time.time() - start_time_squirrels
        logger.info(f"With Squirrels: Found {len(combined_results)} unique results in {squirrels_time:.2f} seconds")
        
        # Restore original setting
        collector.use_ninja_squirrels = original_setting
        
        # Analyze and calculate metrics
        api_stats = self._analyze_results(api_only_results)
        combined_stats = self._analyze_results(combined_results)
        
        # Get unique results from Ninja Squirrel Gathering
        unique_to_squirrels = self._get_unique_results(combined_results, api_only_results)
        
        # Calculate improvements
        improvement = self._calculate_improvement(api_stats, combined_stats)
        
        # Generate detailed result comparison
        result = {
            "timestamp": datetime.now().isoformat(),
            "days_lookback": days,
            "api_only": {
                "count": len(api_only_results),
                "execution_time": api_time,
                "stats": api_stats
            },
            "with_squirrels": {
                "count": len(combined_results),
                "execution_time": squirrels_time,
                "stats": combined_stats
            },
            "improvements": improvement,
            "unique_to_squirrels": {
                "count": len(unique_to_squirrels),
                "examples": unique_to_squirrels[:5] if len(unique_to_squirrels) > 5 else unique_to_squirrels
            }
        }
        
        # Save results
        self._save_benchmark_results(result)
        self.latest_results = result
        
        return result
    
    def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze collection results and generate metrics
        
        Args:
            results: List of startup funding entries
            
        Returns:
            Dictionary with analysis statistics
        """
        if not results:
            return {
                "count": 0,
                "field_completion": {},
                "avg_fields_populated": 0,
                "industry_distribution": {},
                "funding_rounds": {},
                "avg_funding_amount": 0
            }
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(results)
        
        # Calculate field completion rates
        fields = ["company_name", "funding_amount", "funding_round", "industry", 
                 "location", "description", "investors", "url"]
        
        field_completion = {}
        for field in fields:
            if field in df.columns:
                # For regular fields, check if they're not None, NaN, or empty string
                field_completion[field] = (
                    (df[field].notna() & (df[field] != "")).sum() / len(df) * 100
                )
            else:
                field_completion[field] = 0
        
        # Calculate average number of populated fields per entry
        populated_fields = 0
        for field in fields:
            if field in df.columns:
                populated_fields += (df[field].notna() & (df[field] != "")).sum()
        
        avg_fields = populated_fields / len(df) if len(df) > 0 else 0
        
        # Industry distribution
        industry_dist = {}
        if "industry" in df.columns:
            industry_counts = df["industry"].value_counts().to_dict()
            total = sum(industry_counts.values())
            industry_dist = {k: (v / total) * 100 for k, v in industry_counts.items()}
        
        # Funding rounds distribution
        round_dist = {}
        if "funding_round" in df.columns:
            round_counts = df["funding_round"].value_counts().to_dict()
            total = sum(round_counts.values())
            round_dist = {k: (v / total) * 100 for k, v in round_counts.items()}
        
        # Average funding amount
        avg_funding = 0
        if "funding_amount" in df.columns:
            # Convert to numeric, coerce errors to NaN
            df["funding_amount"] = pd.to_numeric(df["funding_amount"], errors="coerce")
            avg_funding = df["funding_amount"].mean()
        
        return {
            "count": len(df),
            "field_completion": field_completion,
            "avg_fields_populated": avg_fields,
            "industry_distribution": industry_dist,
            "funding_rounds": round_dist,
            "avg_funding_amount": avg_funding
        }
    
    def _calculate_improvement(self, api_stats: Dict[str, Any], 
                              combined_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate improvement metrics between API-only and combined approaches
        
        Args:
            api_stats: Statistics from API-only results
            combined_stats: Statistics from combined results (with Ninja Squirrels)
            
        Returns:
            Dictionary with improvement metrics
        """
        # Avoid division by zero
        if api_stats["count"] == 0:
            count_improvement = 100.0
        else:
            count_improvement = ((combined_stats["count"] - api_stats["count"]) / 
                                api_stats["count"]) * 100
        
        # Field completion improvement
        field_completion_improvement = {}
        for field, rate in combined_stats["field_completion"].items():
            if field in api_stats["field_completion"]:
                api_rate = api_stats["field_completion"][field]
                if api_rate == 0:
                    field_completion_improvement[field] = 100.0
                else:
                    field_completion_improvement[field] = rate - api_rate
            else:
                field_completion_improvement[field] = rate
        
        # Fields populated improvement
        if api_stats["avg_fields_populated"] == 0:
            fields_populated_improvement = 100.0
        else:
            fields_populated_improvement = ((combined_stats["avg_fields_populated"] - 
                                          api_stats["avg_fields_populated"]) / 
                                         api_stats["avg_fields_populated"]) * 100
        
        return {
            "count_percent": count_improvement,
            "field_completion": field_completion_improvement,
            "avg_fields_populated_percent": fields_populated_improvement
        }
    
    def _get_unique_results(self, combined_results: List[Dict[str, Any]], 
                           api_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify results that are only present in the combined dataset (unique to Ninja Squirrel Gathering)
        
        Args:
            combined_results: Results from combined approach (with Ninja Squirrels)
            api_results: Results from API-only approach
            
        Returns:
            List of results unique to Ninja Squirrel Gathering
        """
        # Create sets of company names from each result set for easy comparison
        api_companies = set()
        for result in api_results:
            company = result.get("company_name")
            if company:
                api_companies.add(company.lower())
        
        # Find entries in combined results that don't exist in API results
        unique_entries = []
        for result in combined_results:
            company = result.get("company_name")
            if company and company.lower() not in api_companies:
                # Add source field to indicate it came from Ninja Squirrel Gathering
                result_copy = result.copy()
                result_copy["data_source"] = "Ninja Squirrel Gathering"
                unique_entries.append(result_copy)
        
        return unique_entries
    
    def _save_benchmark_results(self, results: Dict[str, Any]) -> None:
        """
        Save benchmark results to the benchmark file
        
        Args:
            results: Dictionary with benchmark results
        """
        # Load existing benchmarks if available
        existing_benchmarks = []
        if self.benchmark_file.exists():
            try:
                with open(self.benchmark_file, 'r') as f:
                    existing_benchmarks = json.load(f)
            except Exception as e:
                logger.error(f"Error loading existing benchmarks: {str(e)}")
        
        # Add new benchmark
        existing_benchmarks.append(results)
        
        # Save updated benchmarks
        try:
            with open(self.benchmark_file, 'w') as f:
                json.dump(existing_benchmarks, f, indent=2)
            logger.info(f"Saved benchmark results to {self.benchmark_file}")
        except Exception as e:
            logger.error(f"Error saving benchmark results: {str(e)}")
    
    def get_latest_benchmark(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent benchmark results
        
        Returns:
            Dictionary with benchmark results or None if no benchmarks exist
        """
        if self.latest_results:
            return self.latest_results
        
        # Try to load from file
        if self.benchmark_file.exists():
            try:
                with open(self.benchmark_file, 'r') as f:
                    benchmarks = json.load(f)
                if benchmarks:
                    # Return the most recent benchmark
                    return benchmarks[-1]
            except Exception as e:
                logger.error(f"Error loading benchmarks: {str(e)}")
        
        return None
    
    def get_all_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Get all historical benchmark results
        
        Returns:
            List of benchmark result dictionaries
        """
        if self.benchmark_file.exists():
            try:
                with open(self.benchmark_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading benchmarks: {str(e)}")
        
        return [] 