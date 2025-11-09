from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit

app = Flask(__name__)
CORS(app)

print("Loading and merging data... This may take a moment.")

spark = SparkSession.builder.appName("AI Job Impact").getOrCreate()

global_df = spark.read.csv(
    'data/ai_job_trends_dataset.csv',
    header=True,
    inferSchema=True
)
print("Global data loaded.")

brazil_df = spark.read.csv(
    'data/brazil_ai_job_impact_large.csv',
    header=True,
    inferSchema=True
)
print("Brazil-specific data loaded.")

brazil_df = brazil_df.withColumnRenamed("Sector", "Industry")
brazil_df = brazil_df.withColumnRenamed("Occupation_Name", "Job Title")

brazil_df = brazil_df.withColumn("Location", lit("Brazil"))

brazil_df = brazil_df.withColumn(
    "Automation Risk (%)", 
    when(col("Automation_Probability").isNotNull(), col("Automation_Probability") * 100)
    .otherwise(lit(None))
)

merged_df = global_df.unionByName(brazil_df, allowMissingColumns=True)
print("Dataframes merged successfully.")

df = merged_df.toPandas()

spark.stop()
print("Spark session stopped.")

@app.route('/api/locations', methods=['GET'])
def get_locations():
    locations = df['Location'].dropna().unique().tolist()
    return jsonify(sorted(locations))

@app.route('/api/jobs-by-risk', methods=['GET'])
def get_jobs_by_risk():
    sort_order = request.args.get('sort', 'desc')
    limit = int(request.args.get('limit', 15))
    location = request.args.get('location', 'All')
    
    filtered_df = df if location == 'All' else df[df['Location'] == location]
    
    filtered_df = filtered_df[['Job Title', 'Automation Risk (%)']].dropna()
    
    ascending = sort_order == 'asc'
    sorted_df = filtered_df.sort_values(by='Automation Risk (%)', ascending=ascending).head(limit)
    
    return jsonify(sorted_df.to_dict(orient='records'))

@app.route('/api/job-growth', methods=['GET'])
def get_job_growth():
    location = request.args.get('location', 'All')
    
    filtered_df = df if location == 'All' else df[df['Location'] == location]
    
    required_cols = ['Industry', 'Job Openings (2024)', 'Projected Openings (2030)']
    growth_df = filtered_df[required_cols].dropna()
    
    industry_growth = growth_df.groupby('Industry').agg({
        'Job Openings (2024)': 'sum',
        'Projected Openings (2030)': 'sum'
    }).reset_index()
    
    industry_growth['Projected Growth (%)'] = (
        (industry_growth['Projected Openings (2030)'] - industry_growth['Job Openings (2024)']) 
        / industry_growth['Job Openings (2024)'] * 100
    )
    
    result = industry_growth[['Industry', 'Projected Growth (%)']].to_dict(orient='records')
    return jsonify(result)

@app.route('/api/workers-by-risk', methods=['GET'])
def get_workers_by_risk():
    location = request.args.get('location', 'All')
    
    filtered_df = df if location == 'All' else df[df['Location'] == location]
    
    risk_cols = ['Risk_Level', 'Number_of_Workers']
    risk_df = filtered_df[risk_cols].dropna()
    
    risk_distribution = risk_df.groupby('Risk_Level')['Number_of_Workers'].sum().reset_index()
    risk_distribution.columns = ['Risk Level', 'Workers']
    
    return jsonify(risk_distribution.to_dict(orient='records'))

@app.route('/api/impact-type', methods=['GET'])
def get_impact_type():
    location = request.args.get('location', 'All')
    
    filtered_df = df if location == 'All' else df[df['Location'] == location]
    
    impact_cols = ['Impact_Type']
    impact_df = filtered_df[impact_cols].dropna()
    
    impact_distribution = impact_df['Impact_Type'].value_counts().reset_index()
    impact_distribution.columns = ['Impact Type', 'Count']
    
    return jsonify(impact_distribution.to_dict(orient='records'))

@app.route('/api/sectors-at-risk', methods=['GET'])
def get_sectors_at_risk():
    location = request.args.get('location', 'All')
    
    filtered_df = df if location == 'All' else df[df['Location'] == location]
    
    high_risk_df = filtered_df[filtered_df['Risk_Level'] == 'High']
    
    sector_cols = ['Industry', 'Number_of_Workers']
    sector_df = high_risk_df[sector_cols].dropna()
    
    sector_risk = sector_df.groupby('Industry')['Number_of_Workers'].sum().reset_index()
    sector_risk = sector_risk.sort_values(by='Number_of_Workers', ascending=False).head(10)
    sector_risk.columns = ['Sector', 'Workers at Risk']
    
    return jsonify(sector_risk.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
