# Developer Utilities

This directory contains utility modules intended for development and benchmarking purposes only.

## Benchmark Manager

The `benchmark.py` module provides utilities for benchmarking different data collection methods:

- Compare API-only vs. API+Ninja Squirrel Gathering approaches
- Measure performance metrics (execution time, data completeness)
- Track historical improvements
- Identify unique startups found through Data Disco Dancing

## Accessing Developer View

To access the developer view in the dashboard:

1 Click the 🔧 (wrench) icon in the top-right corner of the dashboard
2 Or append `?dev=true` to the dashboard URL

Example: `http://localhost:8501/?dev=true`

## Benchmark Metrics Collected

The benchmark system tracks several key metrics:

- **Quantity metrics:**
  - Total unique startups found by each method
  - Number of startups found exclusively by Ninja Squirrel Gathering
  - Execution time for each method

- **Quality metrics:**
  - Field completion rates (% of fields populated)
  - Average number of fields populated per startup
  - Distribution of industries and funding rounds

Running Benchmarks

Benchmarks can be run:

1 From the developer view in the dashboard
2 Programmatically using the BenchmarkManager

```python
from startup_agent.utils.benchmark import BenchmarkManager
from startup_agent.agents.startup_collector import StartupCollector
from startup_agent.config import DATA_DIR

# Initialize
benchmark_manager = BenchmarkManager(DATA_DIR)
collector = StartupCollector()

# Run benchmark
results = benchmark_manager.run_collection_benchmark(collector, days=7)

# View results
print(f"API only found {results['api_only']['count']} startups")
print(f"With Data Disco Dancing found {results['with_squirrels']['count']} startups")
print(f"Improvement: {results['improvements']['count_percent']:.1f}%")
```

## Notes

- Benchmark results are stored in `startup_agent/data/benchmarks/collection_benchmarks.json`
- The developer view is hidden from regular users 