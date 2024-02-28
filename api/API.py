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

    """
    Retrieve coral data based on the specified Coral ID.

    Parameters:
    - id (int): Coral ID to retrieve data for.

    Returns:
    - JSON response containing information about the corals, including Coral ID, Date, Temperature,
      DHW (Degree Heating Weeks), and Geometry.
    - If no corals are found, returns a JSON response with a 404 status and a message indicating
      that the coral was not found.
    - If an error occurs during the process, returns a JSON response with a 500 status and an error message.

    Example:
    - Request: GET /Corals/1
    - Response:
        {
          "Coral_ID": 1,
          "Date": "2024-02-28",
          "Temperature": 28.5,
          "DHW": 2.3,
          "Geometry": {"type": "Point", "coordinates": [123.456, -78.901]}
        }

    """

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

    """
    Fetches coral data within a specified date range, generates a Folium map, and saves it to an HTML file.

    Parameters:
    - start_date (str): Start date of the desired date range in the format 'YYYY-MM-DD'.
    - end_date (str): End date of the desired date range in the format 'YYYY-MM-DD'.

    Returns:
    - If successful, returns a JSON object containing a list of dictionaries representing coral data.
    - If unsuccessful, returns a JSON object with an error message and a corresponding HTTP status code.

    The function performs the following steps:
    1. Checks if both start_date and end_date are provided; returns an error if not.
    2. Executes a SQL query to fetch coral data within the specified date range.
    3. Converts the fetched data into a list of dictionaries for JSON serialization.
    4. Creates a Folium map centered around Indonesia with a dark background.
    5. Adds GeoJson objects for each coral to the map with tooltips containing relevant information.
    6. Saves the generated map to an HTML file named 'corals.html'.
    7. Returns the JSON object containing coral data.

    Raises:
    - If an exception occurs during the process, returns a JSON object with an error message and a 500 status code.

    Example Usage:
    GET /get_corals_by_date?start_date=2022-01-01&end_date=2022-12-31
    """

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


@app.route('/Corals_temp_dhw', methods=['GET'])
def get_corals_by_temp_dhw():

    """
get_corals_by_temp_dhw - Retrieve coral data based on temperature and Degree Heating Weeks (DHW) criteria.

Parameters:
    cursor (database cursor): The cursor object for executing SQL queries.

Returns:
    dict: A dictionary containing coral data and a Folium map HTML file.
          - 'corals': List of dictionaries, each representing a coral with the following keys:
            - 'Coral_ID': Coral identifier.
            - 'Date': Date of the recorded data.
            - 'Temperature': Temperature recorded for the coral.
            - 'DHW': Degree Heating Weeks recorded for the coral.
            - 'Geometry': GeoJSON representation of the coral's geometry.

          - 'message': String, indicating that no coral was found (if applicable).
          - 'error': String, indicating an error message if there's an exception during execution.

Notes:
    - The function queries a database to retrieve coral data based on temperature (> 30) and DHW (> 4).
    - It constructs a list of dictionaries containing relevant coral information.
    - Creates a Folium map centered around the average coordinates of coral locations with GeoJSON data.
    - Saves the map as an HTML file named 'corals.html'.
    - Returns a dictionary with either coral data, a message if no coral is found, or an error message.
"""

    try:
        cursor.execute("""
                        SELECT t.ID, t.Coral_ID, t.Date, t.Temperature, t.DHW, ST_AsGeoJSON(c.Geometry) 
                        FROM Temperature t
                        JOIN Coral c ON t.Coral_ID = c.ID
                        WHERE t.temperature > 30 AND t.DHW > 4;""")
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
    


if __name__ == '__main__':
    app.run(debug=True)
