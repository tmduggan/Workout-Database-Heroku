import psycopg2
from datetime import datetime

# Replace with your Heroku database URL
DATABASE_URL = "postgres://udpnsji7h49vfe:p20aa2e954b559862de4011f375c341d4c78d45fff7238501261a544661e7153f@cf980tnnkgv1bp.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d45o393jceliua"

def calculate_one_rm(weight, reps):
    """Calculate 1RM using the Epley formula."""
    return weight * (1 + 0.0333 * reps) if weight and reps else None

def format_workout_name(name):
    """Normalize workout name (strip spaces and capitalize first letter of each word)."""
    return name.strip().title()

def validate_date(input_date):
    """Validate and process the date input."""
    if input_date.lower() == "today":
        return datetime.today().date()
    try:
        return datetime.strptime(input_date, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD or 'today'.")
        return None

def get_user_input():
    """Prompt user for workout data."""
    # Get workout name, weight, and reps
    workout_input = input("Enter workout name, weight, reps (comma-separated): ").strip()
    try:
        workout_name, weight, reps = [x.strip() for x in workout_input.split(",")]
        weight = float(weight) if weight else None
        reps = int(reps) if reps else None
        workout_name = format_workout_name(workout_name)
    except ValueError:
        print("Invalid input. Please enter data in the format: workout_name, weight, reps")
        return None

    # Get date
    date_input = input("Enter date (YYYY-MM-DD) or 'today' if it was today: ").strip()
    workout_date = validate_date(date_input)
    if not workout_date:
        return None

    # Confirm data
    print(f"\nConfirm the following entry:")
    print(f"Date: {workout_date}, Workout: {workout_name}, Weight: {weight}, Reps: {reps}")
    choice = input("Press Enter to confirm, 'e' to edit, or 'c' to cancel: ").strip().lower()

    if choice == "c":
        print("Entry canceled.")
        return None
    elif choice == "e":
        return get_user_input()  # Recursive call to edit
    elif choice == "":
        return workout_date, workout_name, weight, reps
    else:
        print("Invalid choice. Entry canceled.")
        return None

def insert_workout_data(workout_date, workout_name, weight, reps):
    """Insert workout data into the database."""
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        # Calculate 1RM
        one_rm = calculate_one_rm(weight, reps)

        # Insert data into the database
        cur.execute("""
        INSERT INTO workout_data (workout_name, weight, reps, workout_date, one_rm)
        VALUES (%s, %s, %s, %s, %s);
        """, (workout_name, weight, reps, workout_date, one_rm))

        # Commit transaction
        conn.commit()
        print("Workout data successfully added to the database.")

        # Close connection
        cur.close()
        conn.close()

    except Exception as e:
        print("Error:", e)

def main():
    """Main workflow for entering workout data."""
    workout_entry = get_user_input()
    if workout_entry:
        workout_date, workout_name, weight, reps = workout_entry
        insert_workout_data(workout_date, workout_name, weight, reps)

if __name__ == "__main__":
    main()
