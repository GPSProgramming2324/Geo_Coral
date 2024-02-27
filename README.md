#Geo Coral

#Overview
Welcome to Geocoral! This project involves extracting, tranforming and loading (ETL) data from NOAA for Maluku Tenggara, Indonesia. 

##Table of contents
1.[Getting Started]
2.[Prerequisites]
3.[Instalation]
4.[Usage]
5.[Features]
6.[Contribuitions]
7.[Acknowledgements]
8.[Bibliography]
9.[Contacts]

##Getting Started
###Prerequisites
- Python 3.x
- PostgreSQL database
- Read the requirements

###Instalation
1. Clone the repository;
2. Create and activate an environment
3. Navigate to the project directory
4. Install dependencies
5. Create the database "geocoral" nad run the file "Database/SQL_create_tables.SQL" to create the tables

###Usage
Once the project is installed run the following command: 'python ETL_databse.python'.
This will start the project.

###Features
- Fetches degree heat week (DHW), dates and temperature data from NOAA API;
- Transforms into a tiff file for each parameter
- Stores the data in a PostgreSQL database;
- Creates two tables: 'coral' and 'Temperature';
- Demonstrates Python scripting for data retrival, processement and database interaction.
- Create an html map with corals accordingly to the parameters selected in the API.

##Contribuitions
Contributions are welcome! If you have improvements or additional features, feel free to open an issue or create a pull request.

##Acknowledgements
NOAA API Documentation
psycopg2 Documentation

Watch a tutorial of the process over here: 
https://youtu.be/1-6JAyLUmTs

##Bibliography: 
• Carlson, D( 2023) How to Retrieve and Visualize Sea Surface Temperature Data Using Python, link: https://python.plainenglish.io/how-to-retrieve-and-visualize-sea-surface-temperature-data-using-python-60ce6fc199e6.
• Tatheer, F( 2021) Crud operations using postgres. Link: https://github.com/TatheerFatima/CRUD-application-with-Python-and-PostgreSQL/blob/main/CRUD%20operations%20using%20postgresql.ipynb

##Contacts
For questions or support, contact us at:
-> Miguel -- 20230800@novaims.unl.pt
-> Alonso -- 20230803@novaims.unl.pt
-> Lemesa -- 20230813@novaims.unl.pt
	
