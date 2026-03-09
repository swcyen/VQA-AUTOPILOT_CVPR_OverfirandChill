import pandas as pd
import json

# 1. Load your JSON data
with open('submission.json', 'r') as f:
    data_json = json.load(f)

# 2. Load the sample submission to use as a literal template
df_template = pd.read_csv('sample_submission.csv')
columns = df_template.columns

# 3. Create a list to hold the ordered rows
final_rows = []

# We iterate from 0 to 660 to ensure the order is perfectly sequential
for i in range(661):
    vid_str = str(i)
    row = {'video_id': str(i)}
    
    # Get the predictions for this specific video ID
    # If the ID is missing from your JSON, it defaults to -1
    video_data = data_json.get(vid_str, {})
    
    for col in columns:
        if col == 'video_id':
            continue
            
        # Extract the Question ID (e.g., 'Q1.a') from the template header
        # This handles the \n characters and prefixes automatically
        found = False
        for q_key in video_data:
            if f"{q_key}:" in col or f"{q_key} " in col:
                row[col] = str(video_data[q_key])
                found = True
                break
        
        if not found:
            row[col] = -1
            
    final_rows.append(row)

# 4. Convert to DataFrame
df_final = pd.DataFrame(final_rows)

# 5. Final Formatting
# Ensure columns are in the exact same order as the sample
# Ensure columns are in the exact same order as the sample
df_final = df_final[columns]

# Force video_id to string
df_final['video_id'] = df_final['video_id'].astype(str)
df_final['video_id'] = "'" + df_final['video_id'] + "'"
# Save CSV
df_final.to_csv('submission.csv', index=False)

print("Submission file 'submission.csv' created successfully.")
print(f"Row count: {len(df_final)}")
print(f"Column count: {len(df_final.columns)}")

