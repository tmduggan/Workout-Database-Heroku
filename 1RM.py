import psycopg2
from tabulate import tabulate  # Optional: for pretty printing (install with `pip install tabulate`)

# Replace with your Heroku database URL
DATABASE_URL = "postgres://udpnsji7h49vfe:p20aa2e954b559862de4011f375c341d4c78d45fff7238501261a544661e7153f@cf980tnnkgv1bp.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d45o393jceliua"

def display_best_1rm():
    """Fetch and display the best 1RM for each workout."""
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        # Query to get the best 1RM for each workout
        cur.execute("""
        SELECT workout_name, MAX(one_rm) AS best_1rm, MAX(workout_date) AS date_achieved
        FROM workout_data
        WHERE one_rm IS NOT NULL
        GROUP BY workout_name
        ORDER BY workout_name;
        """)

        # Fetch all results
        results = cur.fetchall()

        # If results exist, display them
        if results:
            print("Best 1RM Data:")
            headers = ["Workout Name", "Best 1RM (lbs)", "Date Achieved"]
            print(tabulate(results, headers=headers, tablefmt="grid"))
        else:
            print("No data available.")

        # Close the database connection
        cur.close()
        conn.close()

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    display_best_1rm()
