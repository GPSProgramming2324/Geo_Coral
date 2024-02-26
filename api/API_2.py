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
def get_coral(id):
    try:
        cursor.execute("SELECT * FROM temperature WHERE coral_id = %s", (id,))
        corals = cursor.fetchall()

        if not corals:
            return jsonify({'message': 'Coral not found'}), 404

        coral_list = [{
            'CORAL_ID': coral[1],
            'Date': coral[2],
            'Temperature': coral[3],
            'DHW': coral[4]
        } for coral in corals]

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date and end_date:
            cursor.execute("SELECT * FROM temperature WHERE coral_id = %s AND date >= %s AND date <= %s", (id, start_date, end_date))
            corals_date_range = cursor.fetchall()

            if corals_date_range:
                coral_list_date_range = [{
                    'CORAL_ID': coral[1],
                    'Date': coral[2],
                    'Temperature': coral[3],
                    'DHW': coral[4]
                } for coral in corals_date_range]

                return jsonify(coral_list + coral_list_date_range)
            else:
                return jsonify({'message': 'No corals found within the specified date range'}), 404

        return jsonify(coral_list)

    except Exception as e:
        return jsonify({'error': f"Error fetching coral data: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)