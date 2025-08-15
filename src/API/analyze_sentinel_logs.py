#!/usr/bin/env python3
"""
Sentinel Hub API Log Analyzer
Extracts and formats Sentinel Hub API call information from geopulse_api.log
"""

import json
import re
from datetime import datetime
from pathlib import Path


def analyze_sentinel_logs(log_file_path="logs/geopulse_api.log"):
    """Analyze Sentinel Hub API logs and generate a summary report."""
    
    if not Path(log_file_path).exists():
        print(f"❌ Log file not found: {log_file_path}")
        return
    
    print("🛰️ SENTINEL HUB API LOG ANALYSIS")
    print("=" * 60)
    
    api_requests = []
    api_responses = []
    batch_summaries = []
    
    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                message = log_entry.get('message', '')
                timestamp = log_entry.get('timestamp', '')
                
                # Extract API requests
                if "🛰️ SENTINEL HUB API REQUEST" in message:
                    api_requests.append({
                        'timestamp': timestamp,
                        'message': message,
                        'request_number': re.search(r'#(\d+)', message).group(1) if re.search(r'#(\d+)', message) else 'N/A'
                    })
                
                # Extract API responses
                elif "📡 SENTINEL HUB API RESPONSE" in message:
                    api_responses.append({
                        'timestamp': timestamp,
                        'message': message,
                        'response_number': re.search(r'#(\d+)', message).group(1) if re.search(r'#(\d+)', message) else 'N/A'
                    })
                
                # Extract batch summaries
                elif "📊 SENTINEL HUB BATCH PROCESSING SUMMARY" in message:
                    batch_summaries.append({
                        'timestamp': timestamp,
                        'message': message
                    })
                
                # Extract specific API call details
                elif any(keyword in message for keyword in [
                    "Request ID:", "Location:", "Time Period:", "Status:", 
                    "Response Time:", "NDVI:", "NDBI:", "NDWI:", "Error:",
                    "Total Properties:", "Successful API Calls:", "Failed API Calls:",
                    "Success Rate:", "Total API Time:", "Average Time per Call:"
                ]):
                    # Store detailed information for the last request/response
                    if api_requests or api_responses:
                        if not hasattr(analyze_sentinel_logs, 'current_details'):
                            analyze_sentinel_logs.current_details = []
                        analyze_sentinel_logs.current_details.append({
                            'timestamp': timestamp,
                            'message': message.strip()
                        })
                        
            except json.JSONDecodeError:
                continue
    
    # Print summary statistics
    print(f"📊 SUMMARY STATISTICS")
    print(f"   Total API Requests Logged: {len(api_requests)}")
    print(f"   Total API Responses Logged: {len(api_responses)}")
    print(f"   Batch Processing Sessions: {len(batch_summaries)}")
    print()
    
    # Print recent API calls
    if api_requests:
        print(f"🔍 RECENT API REQUESTS (Last 10)")
        print("-" * 40)
        for req in api_requests[-10:]:
            timestamp = datetime.fromisoformat(req['timestamp'].replace('Z', '+00:00'))
            print(f"   {timestamp.strftime('%H:%M:%S')} - Request #{req['request_number']}")
        print()
    
    # Print recent API responses
    if api_responses:
        print(f"📡 RECENT API RESPONSES (Last 10)")
        print("-" * 40)
        for resp in api_responses[-10:]:
            timestamp = datetime.fromisoformat(resp['timestamp'].replace('Z', '+00:00'))
            print(f"   {timestamp.strftime('%H:%M:%S')} - Response #{resp['response_number']}")
        print()
    
    # Print batch summaries
    if batch_summaries:
        print(f"📈 BATCH PROCESSING SUMMARIES")
        print("-" * 40)
        for summary in batch_summaries[-3:]:  # Last 3 summaries
            timestamp = datetime.fromisoformat(summary['timestamp'].replace('Z', '+00:00'))
            print(f"   {timestamp.strftime('%H:%M:%S')} - Batch completed")
        print()
    
    # Extract and display detailed information from recent logs
    print(f"🔍 DETAILED LOG ANALYSIS (Last 50 lines)")
    print("-" * 50)
    
    with open(log_file_path, 'r') as f:
        lines = f.readlines()
        
    sentinel_lines = []
    for line in lines[-100:]:  # Check last 100 lines
        try:
            log_entry = json.loads(line.strip())
            message = log_entry.get('message', '')
            timestamp = log_entry.get('timestamp', '')
            
            if any(keyword in message for keyword in [
                "🛰️", "📡", "📊", "🏠", "📅", "✅", "❌", "⚠️",
                "Sentinel Hub", "API REQUEST", "API RESPONSE", 
                "NDVI:", "NDBI:", "NDWI:", "Processing property"
            ]):
                time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
                sentinel_lines.append(f"   {time_str} | {message}")
                
        except json.JSONDecodeError:
            continue
    
    # Display last 20 relevant lines
    for line in sentinel_lines[-20:]:
        print(line)
    
    print()
    print("✅ Log analysis completed!")
    print(f"📁 Full logs available at: {log_file_path}")


def extract_api_performance_stats(log_file_path="logs/geopulse_api.log"):
    """Extract performance statistics from API logs."""
    
    print("\n⚡ API PERFORMANCE ANALYSIS")
    print("=" * 40)
    
    response_times = []
    success_count = 0
    failure_count = 0
    
    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                message = log_entry.get('message', '')
                
                # Extract response times
                if "Response Time:" in message:
                    time_match = re.search(r'Response Time: ([\d.]+) seconds', message)
                    if time_match:
                        response_times.append(float(time_match.group(1)))
                
                # Count successes and failures
                if "Status: SUCCESS" in message:
                    success_count += 1
                elif "Status: FAILED" in message:
                    failure_count += 1
                    
            except (json.JSONDecodeError, ValueError):
                continue
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"   Total API Calls: {len(response_times)}")
        print(f"   Successful Calls: {success_count}")
        print(f"   Failed Calls: {failure_count}")
        print(f"   Success Rate: {(success_count/(success_count+failure_count)*100):.1f}%")
        print(f"   Average Response Time: {avg_time:.3f} seconds")
        print(f"   Fastest Response: {min_time:.3f} seconds")
        print(f"   Slowest Response: {max_time:.3f} seconds")
        print(f"   Total API Time: {sum(response_times):.1f} seconds")
    else:
        print("   No performance data found in logs")


if __name__ == "__main__":
    import sys
    
    log_file = sys.argv[1] if len(sys.argv) > 1 else "logs/geopulse_api.log"
    
    analyze_sentinel_logs(log_file)
    extract_api_performance_stats(log_file)