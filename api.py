import math
import sqlite3
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Start FastAPI
app = FastAPI()

# Allow request from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_YEAR = datetime.now().year
DATABASE_NAME = "properties.db"
TABLE_NAME = "house_data"

# calcualte distance between two points
def haversine_distance(lat1, lon1, lat2, lon2):
    EARTH_RADIUS_MILES = 3958.8

    # Convert degrees to radians
    p1, p2 = math.radians(lat1), math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (math.sin(delta_lat / 2.0) ** 2 +
         math.cos(p1) * math.cos(p2) * math.sin(delta_lon / 2.0) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_MILES * c


# Calculating a bounding box for the search
def calculate_bounding_box(lat, lon, radius_miles):
    lat_change = radius_miles / 69.0
    lon_change = radius_miles / (69.0 * math.cos(math.radians(lat)))

    min_lat = lat - lat_change
    max_lat = lat + lat_change
    min_lon = lon - lon_change
    max_lon = lon + lon_change

    return min_lat, max_lat, min_lon, max_lon


@app.get("/search-address")
def search_address(query: str):
    """
    Search bar autocomplete endpoint
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Get up to 5 matching addresses
    cursor.execute(
        f"SELECT DISTINCT Situs FROM {TABLE_NAME} WHERE Situs LIKE ? LIMIT 5",
        (f"{query}%",)
    )
    matches = [row[0] for row in cursor.fetchall() if row[0] is not None]
    conn.close()

    return matches


@app.get("/similar-properties")
def get_similar_properties(address: str):
    """
    Main cascading search algorithm following FBCAD appraisal logic
    """
    start_time = time.time()
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Get target property
    cursor.execute(f"""
        SELECT Latitude, Longitude, Total_Valu, Total_Livi, 
               Neighborho, Building_C, Year_Built, Taxing_Uni, Exemptions
        FROM {TABLE_NAME} 
        WHERE Situs = ?
    """, (address,))

    target_property = cursor.fetchone()

    # Check that target property is valid
    if not target_property or target_property[2] is None or target_property[3] is None or target_property[3] <= 0:
        conn.close()
        return {"error": "Target property data not found or invalid."}

    # Unpack target values
    (t_lat, t_lon, t_val, t_sqft,
     t_nbhd, t_bldg_c, t_year, t_taxing_uni, t_exempt) = target_property

    # Fallback for year built if missing
    t_year = t_year if (t_year and t_year > 0) else 2000

    # Set up the 4 search tiers
    tiers = [
        {
            "tier": 1,
            "description": "Same Neighborhood + Building Class",
            "sqft_percent": 0.10,  # +/- 10% square feet
            "age_years": 5,  # +/- 5 years built
            "where_clause": "Neighborho = ? AND Building_C = ?",
            "params": [t_nbhd, t_bldg_c]
        },
        {
            "tier": 2,
            "description": "Same Neighborhood",
            "sqft_percent": 0.20,  # +/- 20% square feet
            "age_years": 10,  # +/- 10 years built
            "where_clause": "Neighborho = ?",
            "params": [t_nbhd]
        },
        {
            "tier": 3,
            "description": "Same Neighborhood Group (Prefix Match)",
            "sqft_percent": 0.30,  # +/- 30% square feet
            "age_years": 15,  # +/- 15 years built
            "where_clause": "Neighborho LIKE ?",
            "params": [f"{str(t_nbhd)[:3]}%" if t_nbhd else "%"]
        },
        {
            "tier": 4,
            "description": "5-Mile Radius Spatial Fallback",
            "sqft_percent": 0.70,  # +/- 70% square feet
            "age_years": 30,  # +/- 30 years built
            "where_clause": "Latitude BETWEEN ? AND ? AND Longitude BETWEEN ? AND ?",
            "params": []  # Calculated dynamically below if needed
        }
    ]

    selected_comps = []
    used_tier = None

    for current_tier in tiers:
        min_sqft = t_sqft * (1 - current_tier["sqft_percent"])
        max_sqft = t_sqft * (1 + current_tier["sqft_percent"])
        min_year = t_year - current_tier["age_years"]
        max_year = t_year + current_tier["age_years"]

        # Calculate bounding box for Tier 4
        if current_tier["tier"] == 4:
            min_lat, max_lat, min_lon, max_lon = calculate_bounding_box(t_lat, t_lon, 5.0)
            current_tier["params"] = [min_lat, max_lat, min_lon, max_lon]

        # Only inlcude properties with same taxing unit
        sql_query = f"""
            SELECT Situs, Total_Valu, Total_Livi, Year_Built, Exemptions, Latitude, Longitude
            FROM {TABLE_NAME}
            WHERE {current_tier['where_clause']}
              AND Taxing_Uni = ?
              AND Total_Livi BETWEEN ? AND ?
              AND Year_Built BETWEEN ? AND ?
              AND Total_Valu > 0
              AND Total_Livi > 0
              AND Situs != ?
        """

        query_params = current_tier["params"] + [t_taxing_uni, min_sqft, max_sqft, min_year, max_year, address]

        cursor.execute(sql_query, tuple(query_params))
        candidate_rows = cursor.fetchall()

        # Check exact distance for Tier 4
        if current_tier["tier"] == 4:
            nearby_rows = []
            for row in candidate_rows:
                dist = haversine_distance(t_lat, t_lon, row[5], row[6])
                if dist <= 5.0:
                    nearby_rows.append(row)
            candidate_rows = nearby_rows

        # Stop when there are atleast 5 matches
        if len(candidate_rows) >= 5:
            selected_comps = candidate_rows
            used_tier = current_tier
            break

    conn.close()

    # Format results of website
    formatted_comps = []
    all_price_per_sqft = []

    for row in selected_comps:
        comp_situs, comp_val, comp_sqft, comp_year, comp_exempt = row[:5]

        # Calculate price per square foot ($/sqft)
        price_per_sqft = comp_val / comp_sqft
        all_price_per_sqft.append(price_per_sqft)

        size_diff_percent = abs((comp_sqft - t_sqft) / t_sqft) * 100

        if size_diff_percent <= 10.0:
            badge_color = "green"
        elif size_diff_percent <= 20.0:
            badge_color = "yellow"
        else:
            badge_color = "red"

        # Check for tax exemptions
        has_exemption = True if (comp_exempt and str(comp_exempt).strip() != "") else False

        formatted_comps.append({
            "address": comp_situs,
            "val": f"${comp_val:,.0f}",
            "sqft": f"{comp_sqft:,.0f}",
            "ppsf": price_per_sqft,
            "ppsf_display": f"${price_per_sqft:,.2f}/sqft",
            "sqft_diff_pct": round(size_diff_percent, 1),
            "badge": badge_color,
            "is_capped": has_exemption,
            "age_diff": abs((comp_year or 2000) - t_year)
        })

    # Target property price per square foot
    target_ppsf = t_val / t_sqft

    formatted_comps.sort(key=lambda x: abs(x["ppsf"] - target_ppsf))

    median_ppsf = 0
    if all_price_per_sqft:
        sorted_prices = sorted(all_price_per_sqft)
        n = len(sorted_prices)
        if n % 2 != 0:
            median_ppsf = sorted_prices[n // 2]
        else:
            median_ppsf = (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2.0

    execution_time = (time.time() - start_time) * 1000
    print(f"Query completed in {execution_time:.2f} ms using Tier {used_tier['tier'] if used_tier else 'None'}")

    return {
        "target": {
            "address": address,
            "val": f"${t_val:,.0f}",
            "sqft": f"{t_sqft:,.0f}",
            "ppsf_display": f"${target_ppsf:,.2f}/sqft"
        },
        "metrics": {
            "tier_used": used_tier["tier"] if used_tier else 0,
            "tier_desc": used_tier["description"] if used_tier else "No matches found",
            "median_ppsf": f"${median_ppsf:,.2f}/sqft",
            "comps_found": len(selected_comps)
        },
        "comps": formatted_comps[:10]  # Return top 10 best matches
    }
