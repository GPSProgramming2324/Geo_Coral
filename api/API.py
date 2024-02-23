import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace these with your PostgreSQL database credentials
DB_HOST = "localhost"
DB_PASS = "postgres"
DB_NAME = "geocoral_example"
DB_USER = "postgres"

try:
    connection = psycopg2.connect(
        host=DB_HOST,
        password=DB_PASS,
        database=DB_NAME,
        user=DB_USER,
    )

    cursor = connection.cursor()
except Exception as e:
    print(f"Error connecting to database: {e}")

"""@app.route('/Corals/<int:id>', methods=['GET'])
def get_Coral(id):
    try:
        cursor.execute("SELECT * FROM Coral WHERE ID = %s", (id,))
        coral = cursor.fetchone()

        if coral:
            coral_dict = {
                'CORAL_ID': coral[0],
                'Geometry': coral[1], 
            }
            return jsonify(coral_dict)
        else:
            return jsonify({'message': 'Coral not found'}), 404

    except Exception as e:
        return jsonify({'error': f"Error fetching coral data: {e}"}), 500
"""



@app.route('/Corals/<int:id>', methods=['GET'])
def get_Coral(id):
    try:
        cursor.execute("SELECT * FROM temperature WHERE ID = %s", (id,))
        corals = cursor.fetchall()

        coral_list = []

        for coral in corals:
            coral_dict = {
                'CORAL_ID':   coral[1],
                'Date':       coral[2],
                'Temperature':coral[3]
            }
            coral_list.append(coral_dict)

        if coral_list:
            return jsonify(coral_list)
        else:
            return jsonify({'message': 'Coral not found'}), 404

    except Exception as e:
        return jsonify({'error': f"Error fetching coral data: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)