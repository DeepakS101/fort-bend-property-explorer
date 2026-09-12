# 🏡 Property Assessment Explorer & Spatial Comp Engine

A full-stack geographic information system (GIS) and valuation tool designed to automate real estate comparable property ("comp") analysis using cascading appraisal logic and spatial math. Built specifically to assist with statutory property tax appeals under **Texas Tax Code §41.43(b)(3)**.

---

## 🚀 Key Features

* **Cascading FBCAD Algorithm:** Replicates official appraisal district workflows by stepping through a 4-tier filtering cascade (Neighborhood + Building Class $\rightarrow$ Neighborhood $\rightarrow$ Neighborhood Prefix $\rightarrow$ 5-Mile Spatial Fallback).
* **Spatial Optimization & Haversine Math:** Implements bounding box pre-filtering to minimize computational overhead, paired with the Haversine formula to compute true great-circle distances on a globe for radius-based fallback searches.
* **FastAPI Backend:** High-performance asynchronous API handling instant autocomplete suggestions and complex multi-parameter database queries.
* **Modern React Frontend:** Interactive dashboard featuring real-time size-difference quality badges, exemption warning indicators, and statutory median price-per-square-foot calculations.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, SQLite, Pandas, GeoPandas[cite: 1, 2, 3]
* **Frontend:** React, Vite, JavaScript, CSS Flexbox
* **Geospatial Processing:** Shapefile parsing, coordinate reference system transformation (`EPSG:4326`), centroid calculation[cite: 3]

---

## 📂 Project Architecture

Deepak Project/
│
├── api.py                   # FastAPI server, spatial cascade logic, and Haversine engine[cite: 1]
├── make_database.py         # Pipeline script converting cleaned CSV data into SQLite[cite: 2]
├── Summer Project.py        # GIS shapefile processor (GeoPandas coordinate extraction)[cite: 3]
├── fort_bend_properties.csv # Processed regional property dataset[cite: 3]
├── properties.db            # Local SQLite database instance[cite: 2]
│
└── property-frontend/       # React application directory
    ├── src/                 # Components, styling (App.jsx, App.css)
    ├── package.json         # Frontend dependencies
    └── vite.config.js       # Vite build configuration
