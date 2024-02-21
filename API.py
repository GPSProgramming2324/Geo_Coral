from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Replace these with your PostgreSQL database credentials
DB_HOST = "your_database_host"
DB_PORT = "your_database_port"
DB_NAME = "your_database_name"
DB_USER = "your_database_user"
DB_PASSWORD = "your_database_password"

def get_data_from_postgres():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cursor = connection.cursor()

        # Replace this query with your actual query
        query = "SELECT * FROM your_table"
        cursor.execute(query)

        data = cursor.fetchall()

        return data

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection:
            connection.close()

@app.route('/get_data', methods=['GET'])
def get_data():
    data = get_data_from_postgres()
    if data is not None:
        return jsonify({"data": data})
    else:
        return jsonify({"error": "Failed to fetch data from the database"}), 500

if __name__ == '__main__':
    app.run(debug=True)
