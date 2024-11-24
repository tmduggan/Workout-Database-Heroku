import psycopg2

DATABASE_URL = "postgres://udpnsji7h49vfe:p20aa2e954b559862de4011f375c341d4c78d45fff7238501261a544661e7153f@cf980tnnkgv1bp.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d45o393jceliua"

try:
    # Connect to the database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # Create a test table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50),
        value INT
    );
    """)

    # Insert a test row
    cur.execute("INSERT INTO test_table (name, value) VALUES (%s, %s) RETURNING id;", ('PostgreSQL 16 Test', 789))
    inserted_id = cur.fetchone()[0]
    conn.commit()
    print(f"Inserted row with ID {inserted_id}")

    # Retrieve and print all rows
    cur.execute("SELECT * FROM test_table;")
    rows = cur.fetchall()
    print("Retrieved rows:", rows)

    # Close the connection
    cur.close()
    conn.close()

except Exception as e:
    print("Error:", e)
