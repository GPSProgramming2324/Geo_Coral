#run before the py 

import psycopg2


new_connection = psycopg2.connect(database='geocoral' ,user = "postgres", 
                                  password = "postgres", host = "localhost", port = "5432")
new_connection.autocommit = True
cursor = new_connection.cursor()
table_query = """
CREATE TABLE IF NOT EXISTS coral (
    ID SERIAL PRIMARY KEY,
    Geometry GEOMETRY(Polygon, 4326) 
);
"""



new_connection.autocommit = True
cursor = new_connection.cursor()
cursor.execute(table_query)


new_connection = psycopg2.connect(database='geocoral' ,user = "postgres", 
                                  password = "postgres", host = "localhost", port = "5432")
new_connection.autocommit = True
cursor = new_connection.cursor()
table_query = """
CREATE TABLE Temperature (
    ID SERIAL PRIMARY KEY,
    Coral_ID INT REFERENCES Coral(ID),
    Date DATE NOT NULL,
    Temperature FLOAT NOT NULL,
	DHW FLOAT NOT NULL
);
"""

new_connection.autocommit = True
cursor = new_connection.cursor()
cursor.execute(table_query)