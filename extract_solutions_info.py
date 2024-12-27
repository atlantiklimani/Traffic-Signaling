import os
import pandas as pd

# Define the custom order
custom_order = [
    "I7073_S9102_C1000", "I10000_S35030_C1000", "I8000_S95928_C1000", "I500_S998_C1000",
    "I1662_S10000_C1000", "I2500_S10000_C306", "I70_S210_C200", "I100_S400_C600",
    "I100_S500_C500", "I100_S600_C153", "I110_S330_C450", "I120_S480_C500",
    "I120_S720_C400", "I150_S45150_C100", "I155_S57155_C300", "I180_S1080_C800",
    "I2000_S12000_C57", "I2000_S6000_C376", "I200_S1000_C400", "I200_S1000_C550",
    "I200_S17200_C1000", "I200_S4200_C400", "I220_S1100_C558", "I220_S660_C430",
    "I241_S43241_C158", "I2500_S10000_C306", "I2999_S17994_C103", "I3000_S12000_C407",
    "I3000_S15000_C316", "I3000_S18000_C227", "I300_S1500_C469", "I300_S900_C500",
    "I3333_S13332_C428", "I4000_S12000_C161", "I4000_S12000_C387", "I4000_S12000_C397",
    "I4000_S20000_C309", "I4000_S24000_C401", "I400_S2400_C944", "I444_S1776_C666",
    "I500_S2000_C315", "I600_S3000_C332", "I90_S360_C400", "I99_S399_C400",
    "I80_S480_C600", "I80_S240_C300", "I12000_S36000_C2000", "I9000_S36000_C1500",
    "I10000_S30000_C1200"
]

# Directory containing the files
input_directory = 'output'

# List to hold the extracted data
data = []

# Process each file in the directory
for file_name in os.listdir(input_directory):
    if file_name.endswith('.txt'):  # Ensure only text files are processed
        file_name_parts = file_name.split('_')

        # Extract components
        instance_name = '_'.join(file_name_parts[0:3]).replace('.txt', '')
        variant = file_name_parts[4]
        version = file_name_parts[6]
        ils_iterations = file_name_parts[9]
        hill_climbing_iterations = file_name_parts[12]
        best_solution_time = file_name_parts[-4].split('.')[0]
        best_score = file_name_parts[-1].split('.')[0]

        # Append the data as a dictionary
        data.append({
            'Instance Name': instance_name,
            'Variant': variant,
            'Version': version,
            'Nr ILS Iterations': ils_iterations,
            'Nr Hill Climbing Iterations': hill_climbing_iterations,
            'Best Solution Time': best_solution_time,
            'Best Score': best_score
        })

# Create a DataFrame from the collected data
df = pd.DataFrame(data)

# Ensure the rows are sorted by the custom order
df['Sort Key'] = df['Instance Name'].apply(lambda x: custom_order.index(x) if x in custom_order else float('inf'))
sorted_df = df.sort_values(by='Sort Key').drop(columns=['Sort Key'])

# Save the sorted DataFrame to a CSV file
output_csv = 'result_stats_custom_order.csv'
sorted_df.to_csv(output_csv, index=False)

print(f"Results sorted by custom order saved to {output_csv}")
