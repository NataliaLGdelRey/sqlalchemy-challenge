# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from dateutil.relativedelta import relativedelta


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# 1. `/`
# Start at the homepage.
# List all the available routes.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
         f"<h1>Welcome to the Climate App API!</h1>"
        f"<h1>Step 2 - Climate App</h1>"
        f"This is a Flask API for Climate Analysis .<br/><br/><br/>"
        f" <img width='600' src='https://s1.eestatic.com/2022/02/01/alicante/deporte/otros-deportes/646945755_221530575_1706x960.jpg'/ >"
        f"<h2>Here are the available routes:</h2>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# 2. `/api/v1.0/precipitation`
# Convert the query results from your precipitation analysis (i.e. retrieve only the 
# last 12 months of data) to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
  session = Session(engine)
    # Calculate the date one year from the last date in data set.
    # Query to find the last data point in the database 
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    oneyear_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    query_date = oneyear_date.strftime('%Y-%m-%d')

# Perform a query to retrieve the data and precipitation scores
    last_year = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= '2016-08-23').all()
    last_year
  
    session.close()

# Convert the query results to a dictionary using date as the key and prcp as the value.
    precipitations = []
    for date, prcp in last_year:
        if prcp != None:
            precip_dict = {}
            precip_dict[date] = prcp
            precipitations.append(precip_dict)

    # Return the JSON representation of dictionary.
    return jsonify(precipitations)


# 3. `/api/v1.0/stations`
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
  session = Session(engine)
  session.query(Station.id).count()
   # Query for stations.
    most_active_stations = [Station.station, func.count(Measurement.station)]
    session.query(*most_active_stations).filter(Station.station == Measurement.station).group_by(Station.station).\
                            order_by(func.count(Measurement.station).desc()).all()
    session.close()
  
 # Convert the query results to a dictionary.
 all_stations = []
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)
 
    # Return the JSON representation of dictionary.
    return jsonify(all_stations)


# 4. `/api/v1.0/tobs`
# Query the dates and temperature observations of the most-active station for 
# the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
        station = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
        session.query(*station).filter(Measurement.station == most_active_stations[0]).all()
        session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.tobs).desc()).first()
        last_12_months = session.query(Measurement.tobs).\
            filter(Measurement.date.between(query_date,last_date),\
                   Measurement.station == 'USC00519281').all()
        last_12_months

    session.close()

 # Convert the query results to a dictionary using date as the key and temperature as the value.
    all_temperatures = []
    for date, temp in data_from_last_year:
        if temp != None:
            temp_dict = {}
            temp_dict[date] = temp
            all_temperatures.append(temp_dict)

    # Return the JSON representation of dictionary.
    return jsonify(all_temperatures)


# 5. `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate `TMIN`, `TAVG`, and `TMAX` for all the dates 
# greater than or equal to the start date.
# For a specified start date and end date, calculate `TMIN`, `TAVG`, and `TMAX` 
# for the dates from the start date to the end date, inclusive.

### Hints
# Join the station and measurement tables for some of the queries.
# Use the Flask `jsonify` function to convert your API data to a valid JSON response object.