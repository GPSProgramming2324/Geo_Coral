import psycopg2
from flask import Flask, request, jsonify
import json
import folium

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
        cursor.execute("""SELECT t.ID, t.Coral_ID, t.Date, t.Temperature, t.DHW, ST_AsGeoJSON(c.Geometry) 
                        FROM Temperature t
                        JOIN Coral c ON t.Coral_ID = c.ID
                        WHERE coral_id = %s;""", (id,))
        corals = cursor.fetchall()

        coral_list = []

        for coral in corals:
            coral_dict = {
                'Coral_ID':   coral[1],
                'Date':       coral[2],
                'Temperature':coral[3],
                'DHW':        coral[4],
                'Geometry':   json.loads(coral[5])
            }
            coral_list.append(coral_dict)

            # Create Folium map centered around Indonesia with a dark background
            m = folium.Map(location=[-7.5489, 131.0149], zoom_start=10, tiles='CartoDB dark_matter')

            for result in corals:
                folium.GeoJson(
                    result[5], name=f"Coral_{result[1]}",
                    tooltip=f"Coral ID: {result[1]}, Temperature: {result[3]}, Date: {result[2]}, DHW: {result[4]}"
                ).add_to(m)

        # Save the map to an HTML file
        m.save('corals.html')            

        if coral_list:
            return jsonify(coral_list)
        else:
            return jsonify({'message': 'Coral not found'}), 404

    except Exception as e:
        return jsonify({'error': f"Error fetching coral data: {e}"}), 500

@app.route('/Corals_by_DHW/<DHW>', methods=['GET'])
def get_Coral_by_DHW(DHW):
    try:
        cursor.execute("""
                        SELECT t.ID, t.Coral_ID, t.Date, t.Temperature, t.DHW, ST_AsGeoJSON(c.Geometry) 
                        FROM Temperature t
                        JOIN Coral c ON t.Coral_ID = c.ID
                        WHERE t.DHW > %s;""", (DHW,))
        corals = cursor.fetchall()

        coral_list = []

        for coral in corals:
            coral_dict = {
                'Coral_ID':   coral[1],
                'Date':       coral[2],
                'Temperature':coral[3],
                'DHW':        coral[4],
                'Geometry':   json.loads(coral[5])
            }
            coral_list.append(coral_dict)

            # Create Folium map centered around Indonesia with a dark background
            m = folium.Map(location=[-7.5489, 131.0149], zoom_start=10, tiles='CartoDB dark_matter')

            for result in corals:
                folium.GeoJson(
                    result[5], name=f"Coral_{result[1]}",
                    tooltip=f"Coral ID: {result[1]}, Temperature: {result[3]}, Date: {result[2]}, DHW: {result[4]}"
                ).add_to(m)

        # Save the map to an HTML file
        m.save('corals.html')

        
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

        cursor.execute("""
                        SELECT t.ID, t.Coral_ID, t.Date, t.Temperature, t.DHW, ST_AsGeoJSON(c.Geometry) 
                        FROM Temperature t
                        JOIN Coral c ON t.Coral_ID = c.ID
                        WHERE Date BETWEEN %s AND %s""", (start_date, end_date))
        
        corals = cursor.fetchall()

        coral_list = []

        for coral in corals:
            coral_dict = {
                'Coral_ID':   coral[1],
                'Date':       coral[2],
                'Temperature':coral[3],
                'DHW':        coral[4],
                'Geometry':   json.loads(coral[5])
            }
            coral_list.append(coral_dict)

            # Create Folium map centered around Indonesia with a dark background
            m = folium.Map(location=[-7.5489, 131.0149], zoom_start=10, tiles='CartoDB dark_matter')

            for result in corals:
                folium.GeoJson(
                    result[5], name=f"Coral_{result[1]}",
                    tooltip=f"Coral ID: {result[1]}, Temperature: {result[3]}, Date: {result[2]}, DHW: {result[4]}"
                ).add_to(m)

        # Save the map to an HTML file
        m.save('corals.html')

        return jsonify(coral_list)

    except Exception as e:
        return jsonify({'error': f"Error fetching coral data within date range: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
