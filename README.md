# 🏡 Property Assessment Explorer & Spatial Comp Engine

A full-stack geographic information system (GIS) and valuation tool designed to automate real estate comparable property ("comp") analysis using cascading appraisal logic and spatial math. Built specifically to assist with statutory property tax appeals under **Texas Tax Code §41.43(b)(3)**[cite: 1].

---

## 🚀 Key Features

* **Cascading FBCAD Algorithm:** Replicates official appraisal district workflows by stepping through a 4-tier filtering cascade (Neighborhood + Building Class $\rightarrow$ Neighborhood $\rightarrow$ Neighborhood Prefix $\rightarrow$ 5-Mile Spatial Fallback)[cite: 1].
* **Spatial Optimization & Haversine Math:** Implements bounding box pre-filtering to minimize computational overhead, paired with the Haversine formula to compute true great-circle distances on a globe for radius-based fallback searches[cite: 1].
* **FastAPI Backend:** High-performance asynchronous API handling instant autocomplete suggestions and complex multi-parameter database queries[cite: 1].
* **Modern React Frontend:** Interactive dashboard featuring real-time size-difference quality badges, exemption warning indicators, and statutory median price-per-square-foot calculations[cite: 1].

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, SQLite, Pandas, GeoPandas[cite: 1]
* **Frontend:** React, Vite, JavaScript, CSS Flexbox[cite: 1]
* **Geospatial Processing:** Shapefile parsing, coordinate reference system transformation (`EPSG:4326`), centroid calculation[cite: 1]

---

## 📂 Project Architecture

```text
Deepak Project/
│
├── api.py                   # FastAPI server, spatial cascade logic, and Haversine engine[cite: 1]
├── make_database.py         # Pipeline script converting cleaned CSV data into SQLite[cite: 1]
├── Summer Project.py        # GIS shapefile processor (GeoPandas coordinate extraction)[cite: 1]
├── fort_bend_properties.csv # Processed regional property dataset[cite: 1]
├── properties.db            # Local SQLite database instance[cite: 1]
│
└── property-frontend/       # React application directory[cite: 1]
    ├── src/                 # Components, styling (App.jsx, App.css)[cite: 1]
    ├── package.json         # Frontend dependencies[cite: 1]
    └── vite.config.js       # Vite build configuration[cite: 1]
```

---

## 🚀 Getting Started & Local Installation

Follow these steps to set up and run the project locally on your machine.

### Prerequisites
* Python 3.8+
* Node.js & npm

### 1. Clone the Repository
```bash
git clone https://github.com/DeepakS101/fort-bend-property-explorer.git
cd fort-bend-property-explorer
```

### 2. Backend Setup (FastAPI)
```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install backend dependencies
pip install fastapi uvicorn pandas geopandas shapely

# Run the FastAPI development server
uvicorn api:app --reload
```
*The backend API will be live at http://127.0.0.1:8000

### 3. Frontend Setup (React & Vite)
Open a separate terminal window, then:
```bash
# Navigate to the frontend directory
cd property-frontend

# Install dependencies
npm install

# Start the development server
npm run dev

*The React dashboard will open locally at http://localhost:5173
