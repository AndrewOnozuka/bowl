import pandas as pd
import json
import random

# Function to generate a random HEX color
def random_hex():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Load CSV Files
hex_df = pd.read_csv("bowl - hex.csv")  # Bowler Full Names + Display Names + Hexcodes
scores_df = pd.read_csv("bowl - all.csv")  # All Scores

# Convert 'date' column to datetime
scores_df['date'] = pd.to_datetime(scores_df['date'])
scores_df['month'] = scores_df['date'].dt.strftime('%Y-%m')  # Extract Month-Year

# Compute Bowler Statistics
bowlers_stats = scores_df.groupby('disp').agg(
    pr=('score', 'max'),  # Personal Record (Highest Score)
    avg=('score', 'mean'),  # Average Score
    total=('score', 'count'),  # Total Games Played
    hundred_plus=('score', lambda x: (x >= 100).sum())  # Count of 100+ Scores
).reset_index()

# Calculate PR - AVG Difference
bowlers_stats['diff'] = bowlers_stats['pr'] - bowlers_stats['avg']

# Compute 100+ Percentage
bowlers_stats['100+(%)'] = (bowlers_stats['hundred_plus'] / bowlers_stats['total']) * 100

# Compute Monthly Averages
monthly_avg = scores_df.groupby(['disp', 'month'])['score'].mean().unstack(fill_value="N/A")

# Merge Bowler Stats with Monthly Averages
result = bowlers_stats.merge(monthly_avg, on="disp", how="left")

# Merge with Full Names & Hex Codes
hex_df = hex_df.rename(columns={'display': 'disp'})  # Ensure Column Names Match
merged_df = result.merge(hex_df, on='disp', how='left')

# Assign Random Hex Code if Missing
merged_df['hexcode'] = merged_df['hexcode'].apply(lambda x: x if pd.notna(x) else random_hex())

# Round All Numeric Values to 2 Decimal Places
numeric_cols = ['pr', 'avg', 'diff', '100+(%)'] + list(monthly_avg.columns)
merged_df[numeric_cols] = merged_df[numeric_cols].applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)

# Convert DataFrame to Dictionary
bowlers_data = merged_df.to_dict(orient="records")

# Include ALL Scores for Charting
all_scores = scores_df[['disp', 'score', 'date']].to_dict(orient="records")

# Final JSON Structure
json_data = {
    "bowlers": bowlers_data,  # Summary Table Data
    "scores": all_scores  # Full Data Points for Charting
}

# Save as JSON
with open("bowlers.json", "w") as f:
    json.dump(json_data, f, indent=4, default=str)

print("JSON file generated successfully.")