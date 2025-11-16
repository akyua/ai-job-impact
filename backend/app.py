from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit


def load_data_once():
    spark = SparkSession.builder.appName("AIJobTrends").getOrCreate()
    file_path = "data/ai_job_trends_dataset.csv"
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    clean_columns = [col.strip() for col in df.columns]
    df = df.toDF(*clean_columns)

    pandas_df = df.toPandas()
    spark.stop()
    print("Data loaded into Pandas DataFrame. Spark session stopped.")
    return pandas_df

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
    avg_risk_df = filtered_df.groupby('Job Title')['Automation Risk (%)'].mean().reset_index()

    ascending = sort_order == 'asc'
    sorted_df = avg_risk_df.sort_values(by='Automation Risk (%)', ascending=ascending).head(limit)

    if ascending:
        sorted_df['Safety Score (%)'] = 100 - sorted_df['Automation Risk (%)']
        sorted_df = sorted_df.drop(columns=['Automation Risk (%)'])

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

    risk_df = risk_df.copy()
    risk_df['Risk_Level'] = risk_df['Risk_Level'].str.replace(r'High.*', 'High', regex=True)
    risk_df['Risk_Level'] = risk_df['Risk_Level'].str.replace(r'Medium.*', 'Medium', regex=True)
    risk_df['Risk_Level'] = risk_df['Risk_Level'].str.replace(r'Low.*', 'Low', regex=True)
    risk_df['Risk_Level'] = risk_df['Risk_Level'].str.replace(r'Average.*', 'Medium', regex=True)

    risk_distribution = risk_df.groupby('Risk_Level')['Number_of_Workers'].sum().reset_index()
    risk_distribution.columns = ['Risk Level', 'Workers']

    return jsonify(risk_distribution.to_dict(orient='records'))

@app.route('/api/workers-by-industry', methods=['GET'])
def get_workers_by_industry():
    location = request.args.get('location', 'All')

    filtered_df = df if location == 'All' else df[df['Location'] == location]

    industry_cols = ['Industry', 'Number_of_Workers']
    industry_df = filtered_df[industry_cols].dropna()

    industry_workers = industry_df.groupby('Industry')['Number_of_Workers'].sum().reset_index()
    industry_workers = industry_workers.sort_values(by='Number_of_Workers', ascending=False).head(10)
    industry_workers.columns = ['Industry', 'Workers']

    return jsonify(industry_workers.to_dict(orient='records'))

@app.route('/api/sectors-at-risk', methods=['GET'])
def get_sectors_at_risk():
    location = request.args.get('location', 'All')

    filtered_df = df if location == 'All' else df[df['Location'] == location]

    filtered_df = filtered_df.copy()
    filtered_df['Risk_Level'] = filtered_df['Risk_Level'].str.replace(r'High.*', 'High', regex=True)

    high_risk_df = filtered_df[filtered_df['Risk_Level'] == 'High']

    sector_cols = ['Industry', 'Number_of_Workers']
    sector_df = high_risk_df[sector_cols].dropna()

    sector_risk = sector_df.groupby('Industry')['Number_of_Workers'].sum().reset_index()
    sector_risk = sector_risk.sort_values(by='Number_of_Workers', ascending=False).head(10)
    sector_risk.columns = ['Sector', 'Workers at Risk']

    return jsonify(sector_risk.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
