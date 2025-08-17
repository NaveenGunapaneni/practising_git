#!/usr/bin/env python3
"""
Comprehensive guide to exploring data with Sentinel Hub Python package
"""

from sentinelhub import (
    SHConfig, BBox, CRS, MimeType, 
    SentinelHubRequest, DataCollection,
    MosaickingOrder, ResamplingType,
    SentinelHubCatalog, SentinelHubStatistical
)
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import json

# =============================================================================
# 1. BASIC SETUP AND CONFIGURATION
# =============================================================================

def setup_sentinelhub():
    """Configure Sentinel Hub credentials"""
    config = SHConfig()
    
    # Set your credentials (get from https://apps.sentinel-hub.com/dashboard/)
    # config.sh_client_id = 'your-client-id'
    # config.sh_client_secret = 'your-client-secret'
    # config.sh_base_url = 'https://services.sentinel-hub.com'
    # config.save()
    
    return config

# =============================================================================
# 2. VEGETATION AND AGRICULTURE MONITORING
# =============================================================================

def vegetation_analysis():
    """Explore vegetation indices and agricultural monitoring"""
    
    # NDVI Calculation (Normalized Difference Vegetation Index)
    ndvi_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B08", "dataMask"],
                units: "DN"
            }],
            output: {
                bands: 4,
                sampleType: "AUTO"
            }
        };
    }
    
    function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        
        // Color coding for NDVI values
        if (ndvi < 0.2) {
            return [0.5, 0.5, 0.5, sample.dataMask]; // Gray (bare soil/urban)
        } else if (ndvi < 0.4) {
            return [1, 1, 0, sample.dataMask]; // Yellow (sparse vegetation)
        } else if (ndvi < 0.6) {
            return [0, 1, 0, sample.dataMask]; // Green (moderate vegetation)
        } else {
            return [0, 0.5, 0, sample.dataMask]; // Dark green (dense vegetation)
        }
    }
    """
    
    # Enhanced Vegetation Index (EVI)
    evi_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B02", "B04", "B08", "dataMask"]
            }],
            output: {
                bands: 1,
                sampleType: "FLOAT32"
            }
        };
    }
    
    function evaluatePixel(sample) {
        let evi = 2.5 * (sample.B08 - sample.B04) / 
                  (sample.B08 + 6 * sample.B04 - 7.5 * sample.B02 + 1);
        return [evi, sample.dataMask];
    }
    """
    
    return {"NDVI": ndvi_evalscript, "EVI": evi_evalscript}

# =============================================================================
# 3. WATER BODY AND QUALITY MONITORING
# =============================================================================

def water_analysis():
    """Explore water body detection and quality assessment"""
    
    # NDWI (Normalized Difference Water Index)
    ndwi_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B03", "B08", "dataMask"]
            }],
            output: {
                bands: 4,
                sampleType: "AUTO"
            }
        };
    }
    
    function evaluatePixel(sample) {
        let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
        
        // Water body detection
        if (ndwi > 0.3) {
            return [0, 0, 1, sample.dataMask]; // Blue (water)
        } else if (ndwi > 0.0) {
            return [0, 1, 1, sample.dataMask]; // Cyan (wet soil/vegetation)
        } else {
            return [0.5, 0.3, 0.1, sample.dataMask]; // Brown (dry land)
        }
    }
    """
    
    # Turbidity estimation
    turbidity_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B03", "dataMask"]
            }],
            output: {
                bands: 1,
                sampleType: "FLOAT32"
            }
        };
    }
    
    function evaluatePixel(sample) {
        // Simple turbidity proxy using red/green ratio
        let turbidity = sample.B04 / sample.B03;
        return [turbidity, sample.dataMask];
    }
    """
    
    return {"NDWI": ndwi_evalscript, "Turbidity": turbidity_evalscript}

# =============================================================================
# 4. URBAN AND BUILT-UP AREA ANALYSIS
# =============================================================================

def urban_analysis():
    """Explore urban development and built-up area mapping"""
    
    # Built-up area detection
    urban_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B08", "B11", "B12", "dataMask"]
            }],
            output: {
                bands: 4,
                sampleType: "AUTO"
            }
        };
    }
    
    function evaluatePixel(sample) {
        // Urban Index calculation
        let ui = (sample.B12 - sample.B08) / (sample.B12 + sample.B08);
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        
        // Built-up area classification
        if (ui > 0.1 && ndvi < 0.2) {
            return [1, 0, 0, sample.dataMask]; // Red (built-up)
        } else if (ndvi > 0.4) {
            return [0, 1, 0, sample.dataMask]; // Green (vegetation)
        } else {
            return [0.8, 0.8, 0.6, sample.dataMask]; // Beige (bare soil)
        }
    }
    """
    
    return {"Urban_Detection": urban_evalscript}

# =============================================================================
# 5. FOREST AND LAND COVER MONITORING
# =============================================================================

def forest_analysis():
    """Explore forest monitoring and land cover classification"""
    
    # Forest/Non-forest classification
    forest_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B08", "B11", "dataMask"]
            }],
            output: {
                bands: 4,
                sampleType: "AUTO"
            }
        };
    }
    
    function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        let swir_ratio = sample.B11 / sample.B08;
        
        // Forest classification logic
        if (ndvi > 0.6 && swir_ratio < 0.5) {
            return [0, 0.5, 0, sample.dataMask]; // Dark green (dense forest)
        } else if (ndvi > 0.4 && swir_ratio < 0.7) {
            return [0, 1, 0, sample.dataMask]; // Green (sparse forest)
        } else if (ndvi > 0.2) {
            return [0.5, 1, 0.5, sample.dataMask]; // Light green (grassland)
        } else {
            return [0.8, 0.6, 0.4, sample.dataMask]; // Brown (bare land)
        }
    }
    """
    
    return {"Forest_Classification": forest_evalscript}

# =============================================================================
# 6. CHANGE DETECTION AND TIME SERIES ANALYSIS
# =============================================================================

def change_detection_example():
    """Example of temporal change detection"""
    
    # Multi-temporal NDVI comparison
    change_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B04", "B08", "dataMask"],
                units: "DN"
            }],
            output: {
                bands: 1,
                sampleType: "FLOAT32"
            },
            mosaicking: "ORBIT"
        };
    }
    
    function evaluatePixel(samples) {
        // Calculate NDVI for each time point
        let ndvi_values = samples.map(sample => 
            (sample.B08 - sample.B04) / (sample.B08 + sample.B04)
        );
        
        if (ndvi_values.length >= 2) {
            // Return NDVI change (recent - old)
            return [ndvi_values[0] - ndvi_values[ndvi_values.length - 1]];
        }
        return [0];
    }
    """
    
    return change_evalscript

# =============================================================================
# 7. PRACTICAL DATA REQUEST FUNCTIONS
# =============================================================================

def create_data_request(bbox, time_interval, evalscript, collection=DataCollection.SENTINEL2_L2A):
    """Create a Sentinel Hub data request"""
    
    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=collection,
                time_interval=time_interval,
                mosaicking_order=MosaickingOrder.LEAST_CC,
                maxcc=0.3  # Maximum cloud coverage
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF)
        ],
        bbox=bbox,
        size=[512, 512],  # Adjust as needed
        config=setup_sentinelhub()
    )
    
    return request

def explore_statistical_data(bbox, time_interval):
    """Get statistical information about the area"""
    
    stats_evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04", "B08", "B11", "B12", "CLM"],
                units: "DN"
            }],
            output: [
                { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
                { id: "true_color", bands: 3, sampleType: "AUTO" },
                { id: "cloud_mask", bands: 1, sampleType: "UINT8" }
            ]
        };
    }
    
    function evaluatePixel(sample) {
        let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        let true_color = [sample.B04/3000, sample.B03/3000, sample.B02/3000];
        
        return {
            ndvi: [ndvi],
            true_color: true_color,
            cloud_mask: [sample.CLM]
        };
    }
    """
    
    request = SentinelHubStatistical(
        aggregation=SentinelHubStatistical.aggregation(
            evalscript=stats_evalscript,
            time_interval=time_interval,
            aggregation_interval='P1M',  # Monthly aggregation
            resolution=(10, 10)
        ),
        input_data=[
            SentinelHubStatistical.input_data(
                DataCollection.SENTINEL2_L2A,
                maxcc=0.3
            )
        ],
        bbox=bbox,
        config=setup_sentinelhub()
    )
    
    return request

# =============================================================================
# 8. EXAMPLE APPLICATIONS AND USE CASES
# =============================================================================

def example_use_cases():
    """Dictionary of example use cases and their applications"""
    
    use_cases = {
        "Agriculture": {
            "description": "Monitor crop health, estimate yields, detect irrigation needs",
            "indices": ["NDVI", "EVI", "SAVI", "NDRE"],
            "applications": [
                "Precision agriculture",
                "Crop type classification",
                "Yield prediction",
                "Irrigation management",
                "Pest/disease detection"
            ]
        },
        
        "Water Management": {
            "description": "Monitor water bodies, quality, and availability",
            "indices": ["NDWI", "MNDWI", "Turbidity", "Chlorophyll-a"],
            "applications": [
                "Flood mapping",
                "Drought monitoring",
                "Water quality assessment",
                "Reservoir monitoring",
                "Coastal erosion"
            ]
        },
        
        "Urban Planning": {
            "description": "Monitor urban growth and infrastructure development",
            "indices": ["Built-up Index", "Urban Heat Island", "NDBI"],
            "applications": [
                "Urban expansion tracking",
                "Land use planning",
                "Green space monitoring",
                "Infrastructure assessment",
                "Population estimation"
            ]
        },
        
        "Forest Management": {
            "description": "Monitor forest health and deforestation",
            "indices": ["NDVI", "NBR", "Forest Cover"],
            "applications": [
                "Deforestation monitoring",
                "Forest fire detection",
                "Biodiversity assessment",
                "Carbon stock estimation",
                "Illegal logging detection"
            ]
        },
        
        "Disaster Response": {
            "description": "Emergency response and disaster monitoring",
            "indices": ["Flood extent", "Burn severity", "Damage assessment"],
            "applications": [
                "Flood mapping",
                "Fire damage assessment",
                "Earthquake damage",
                "Hurricane impact",
                "Emergency planning"
            ]
        },
        
        "Climate Studies": {
            "description": "Long-term environmental monitoring",
            "indices": ["LST", "Snow cover", "Albedo"],
            "applications": [
                "Climate change monitoring",
                "Seasonal variations",
                "Phenology studies",
                "Carbon cycle research",
                "Weather pattern analysis"
            ]
        }
    }
    
    return use_cases

# =============================================================================
# 9. GETTING STARTED TEMPLATE
# =============================================================================

def getting_started_template():
    """Template for getting started with Sentinel Hub"""
    
    template_code = """
    # 1. Setup
    from sentinelhub import *
    config = SHConfig()
    # Add your credentials here
    
    # 2. Define area of interest (example: San Francisco Bay)
    bbox = BBox(bbox=[-122.5, 37.7, -122.3, 37.9], crs=CRS.WGS84)
    
    # 3. Define time period
    time_interval = ('2024-06-01', '2024-08-31')
    
    # 4. Choose your analysis (pick one from above functions)
    evalscript = vegetation_analysis()["NDVI"]
    
    # 5. Create and execute request
    request = create_data_request(bbox, time_interval, evalscript)
    data = request.get_data()
    
    # 6. Visualize results
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 10))
    plt.imshow(data[0])
    plt.title('NDVI Analysis')
    plt.axis('off')
    plt.show()
    """
    
    return template_code

if __name__ == "__main__":
    # Print available exploration options
    print("=== Sentinel Hub Python Package Exploration Options ===")
    print()
    
    # Display use cases
    use_cases = example_use_cases()
    for category, details in use_cases.items():
        print(f"📊 {category}:")
        print(f"   {details['description']}")
        print(f"   Applications: {', '.join(details['applications'][:3])}...")
        print()
    
    print("🚀 Getting Started:")
    print("   1. Sign up at https://www.sentinel-hub.com/")
    print("   2. Get your API credentials")
    print("   3. Use the template code above to start exploring!")
    print()
    print("📚 Key Features:")
    print("   - Real-time and historical satellite data")
    print("   - Custom processing with evalscripts")
    print("   - Statistical analysis capabilities")
    print("   - Change detection and time series")
    print("   - Cloud-free mosaicking")
    print("   - Multiple satellite missions (Sentinel-1, 2, 3, 5P)")