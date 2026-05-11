"""Discovery engine for Air Quality channel — thin wrapper around aqi_source."""
from discovery.aqi_source import fetch_all_cities, build_daily_report

def run_discovery():
    cities = fetch_all_cities()
    return build_daily_report(cities)
