import psycopg2
import csv
from datetime import datetime

# Replace with your Heroku database URL
DATABASE_URL = "postgres://udpnsji7h49vfe:p20aa2e954b559862de4011f375c341d4c78d45fff7238501261a544661e7153f@cf980tnnkgv1bp.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d45o393jceliua"

try:
    # Connect to the database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # Create the workout_data table if it doesn't already exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workout_data (
        id SERIAL PRIMARY KEY,
        workout_name VARCHAR(50),
        weight DECIMAL(10, 2),  -- Allow NULL values for weight
        reps INT,              -- Allow NULL values for reps
        workout_date DATE,
        one_rm FLOAT           -- Allow NULL for one_rep_max if not calculable
    );
    """)

    # Load CSV file into memory
    input_file = 'Workout_Data.csv'
    with open(input_file, 'r') as file:
        csv_reader = list(csv.reader(file))
        header = csv_reader[0]  # Save the header row
        rows = csv_reader[1:]   # All data rows excluding the header

    # Store rows to preserve if insertion fails
    rows_to_keep = []

    for row in rows:
        try:
            # Extract data from the CSV
            raw_date, workout_name, weight, reps = row[:4]

            # Validate and format the date
            workout_date = datetime.strptime(raw_date, '%Y-%m-%d').date()

            # Handle missing values for weight and reps
            weight = float(weight) if weight else None
            reps = int(reps) if reps else None

            # Calculate 1RM only if both weight and reps are available
            one_rm = weight * (1 + 0.0333 * reps) if weight is not None and reps is not None else None

            # Insert data into the database
            cur.execute("""
            INSERT INTO workout_data (workout_name, weight, reps, workout_date, one_rm)
            VALUES (%s, %s, %s, %s, %s);
            """, (workout_name.strip().title(), weight, reps, workout_date, one_rm))
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            rows_to_keep.append(row)  # Preserve rows with errors

    # Commit the transaction
    conn.commit()
    print("Workout data successfully loaded into the database.")

    # Write back the remaining rows to the CSV
    with open(input_file, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(header)  # Preserve the header
        csv_writer.writerows(rows_to_keep)  # Write back only rows that were not successfully added

    # Close the connection
    cur.close()
    conn.close()

except Exception as e:
    print("Error:", e)
