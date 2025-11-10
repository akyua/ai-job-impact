import pandas as pd
from pyspark.sql import SparkSession
from flask import Flask, jsonify, request
from flask_cors import CORS

def load_data_once():
    """Loads data from CSV using Spark and converts to a Pandas DataFrame."""
    spark = SparkSession.builder.appName("AIJobTrends").getOrCreate()
    file_path = "data/ai_job_trends_dataset.csv"
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    
    # Clean up column names that may have issues
    clean_columns = [col.strip() for col in df.columns]
    df = df.toDF(*clean_columns)
    
    pandas_df = df.toPandas()
    spark.stop()
    print("Data loaded into Pandas DataFrame. Spark session stopped.")
    return pandas_df

# --- Main Application Setup ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

print("Loading data... This may take a moment.")
# Load data once at startup and store it in memory
df = load_data_once()

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Returns a list of unique locations."""
    locations = df['Location'].unique().tolist()
    return jsonify(sorted(locations))

@app.route('/api/jobs-by-risk', methods=['GET'])
def get_jobs_by_risk():
    """Returns top/bottom jobs by automation risk, with optional location filter."""
    location = request.args.get('location')
    sort_order = request.args.get('sort', 'desc')
    limit = int(request.args.get('limit', 10))

    filtered_df = df.copy()
    if location and location != 'All':
        filtered_df = filtered_df[filtered_df['Location'] == location]

    is_ascending = sort_order == 'asc'
    sorted_df = filtered_df.sort_values(by='Automation Risk (%)', ascending=is_ascending).head(limit)
    
    result = sorted_df.to_dict(orient='records')
    return jsonify(result)

@app.route('/api/job-growth', methods=['GET'])
def get_job_growth():
    """Calculates projected job growth by AI Impact Level."""
    location = request.args.get('location')
    
    filtered_df = df.copy()
    if location and location != 'All':
        filtered_df = filtered_df[filtered_df['Location'] == location]

    # Ensure numeric types before aggregation
    filtered_df['Job Openings (2024)'] = pd.to_numeric(filtered_df['Job Openings (2024)'])
    filtered_df['Projected Openings (2030)'] = pd.to_numeric(filtered_df['Projected Openings (2030)'])

    growth_df = filtered_df.groupby('Industry').agg({
        'Job Openings (2024)': 'sum',
        'Projected Openings (2030)': 'sum'
    }).reset_index()

    growth_df['Projected Growth (%)'] = (
        (growth_df['Projected Openings (2030)'] - growth_df['Job Openings (2024)']) / 
        growth_df['Job Openings (2024)'] * 100
    ).round(2)

    result = growth_df.to_dict(orient='records')
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)