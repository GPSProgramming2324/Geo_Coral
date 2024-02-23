CREATE EXTENSION POSTGIS;

-- Create Corals table
CREATE TABLE Coral (
    ID SERIAL PRIMARY KEY,
	Geometry GEOMETRY(POLYGON,4326) NOT NULL
);

-- Create Temperatures table
CREATE TABLE Temperature (
    ID SERIAL PRIMARY KEY,
    Coral_ID INT REFERENCES Coral(ID),
    Date DATE NOT NULL,
    Temperature FLOAT NOT NULL,
	DHW FLOAT NOT NULL
);
