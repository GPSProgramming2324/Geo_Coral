import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace these with your PostgreSQL database credentials
DB_HOST = "localhost"
DB_PASS = "postgres"
DB_NAME = "geocoral"
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
                'Temperature':coral[3],
                'DHW':        coral[4]
            }
            coral_list.append(coral_dict)

        if coral_list:
            return jsonify(coral_list)
        else:
            return jsonify({'message': 'Coral not found'}), 404

    except Exception as e:
        return jsonify({'error': f"Error fetching coral data: {e}"}), 500


@app.route('/CoralsByDate', methods=['GET'])
def get_corals_by_date():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not (start_date and end_date):
            return jsonify({'error': 'Both start_date and end_date are required parameters'}), 400

        cursor.execute("SELECT * FROM temperature WHERE Date BETWEEN %s AND %s", (start_date, end_date))
        corals = cursor.fetchall()

        if not corals:
            return jsonify({'message': 'No corals found within the specified date range'}), 404

        coral_list = [{
            'CORAL_ID': coral[1],
            'Date': coral[2],
            'Temperature': coral[3],
            'DHW':coral[4]
        } for coral in corals]

        return jsonify(coral_list)

    except Exception as e:
        return jsonify({'error': f"Error fetching coral data within date range: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)



