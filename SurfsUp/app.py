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

# Add connect_args to create news thread
engine = create_engine("sqlite:///./Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

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
def homepage():
    """List all available api routes."""
    return """ <h1> Surf's Up!: Welcome to the Climate App! </h1>
        --------------------------------------------------------------------------------------------<br/>
        <h1>Climate App</h1>
       This is a Flask API for Climate Analysis.<br/><br/><br/>
        <img width='600' src='https://s1.eestatic.com/2022/02/01/alicante/deporte/otros-deportes/646945755_221530575_1706x960.jpg'/>
    <h3> The available routes are: </h3>
    --------------------------------------------------------------------<br/>
    <ul>
    <li><a href = "/api/v1.0/precipitation"> PRECIPITATION </a> To retrieve precipitations from last 12 months. </li>
    <li><a href = "/api/v1.0/stations"> STATIONS </a> To retrieve a list of the stations. </li> 
    <li><a href = "/api/v1.0/tobs"> TEMPERATURES </a> To retrieve dates and temperature observations of the most-active station from last 12 months. </li>
    <li><a href = "/api/v1.0/<start>"> START </a> To retrieve the minimum, average, and maximum temperatures for a specific start date. </li>
     <li><a href = "/api/v1.0/<start>/<end>"> START/END </a> To retrieve the minimum, average, and maximum temperatures for a specific start-end range. </li>
    </ul>
    """
()

# 2. `/api/v1.0/precipitation`
# Convert the query results from your precipitation analysis (i.e. retrieve only the 
# last 12 months of data) to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation ():
    last_date = session.query(func.max(Measurement.date)).scalar()
    lastyear_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    query_date = lastyear_date.strftime('%Y-%m-%d')
    last_year = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= '2016-08-23').all()
            
  # Create a dictionary from the row data and append to a list of prcp_list
    precipitation_list = []
    for date, prcp in last_year:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_list.append(prcp_dict)

    # Return a list of jsonified precipitation data for the previous 12 months 
    return jsonify(precipitation_list)

# 3. `/api/v1.0/stations`
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Query station data from the Station dataset
    stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))

    # Return a list of jsonified station data
    return jsonify(station_list)

# 4. `/api/v1.0/tobs`
# Query the dates and temperature observations of the most-active station for 
# the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def temperature():

# Query tobs data from last 12 months from the most recent date from Measurement table
    last_date = session.query(func.max(Measurement.date)).scalar()
    lastyear_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    query_date = lastyear_date.strftime('%Y-%m-%d')
    temperatures = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date.between(query_date,last_date),\
                   Measurement.station == 'USC00519281').all()
    
 # Create a dictionary from the row data and append to a list of temp_list
    temp_list = []
    for date, tobs in temperatures:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_list.append(temp_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(temp_list)

# 5. `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate `TMIN`, `TAVG`, and `TMAX` for all the dates 
# greater than or equal to the start date.
# For a specified start date and end date, calculate `TMIN`, `TAVG`, and `TMAX` 
# for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    # Create the session
    session = Session(engine)
    
    # Make a list to query (the minimum, average and maximum temperature)
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Check if there is an end date then do the task accordingly
    if end == None: 
        # Query the data from start date to the most recent date
        start_data = session.query(*sel).\
                            filter(Measurement.date >= start).all()
        # Convert list of tuples into normal list
        start_list = list(np.ravel(start_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start date
        return jsonify(start_list)
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(*sel).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
        # Convert list of tuples into normal list
        start_end_list = list(np.ravel(start_end_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start-end date range
        return jsonify(start_end_list)


# Example:
# ------------------

# First change the date in the url
# To do this, check in the precipitation url a desired valid date/range for start only or start/end
# --------------------------------------

# For start:
#http://127.0.0.1:5000/api/v1.0/2016-07-23

# For start/end:
# http://127.0.0.1:5000/api/v1.0/2016-07-23/2016-08-23

# Array example:
# --------------------
#[
#  Temp Min,
#  Average Temp,
#  Temp Max
#]

# Example output:
# --------------------
#[
#  71.0,
#  78.14427860696517,
#  83.0
#]


 # Close the session                   
session.close()

# Define main branch
if __name__ == '__main__':
    app.run(debug=True, port=5000)

### Hints
# Join the station and measurement tables for some of the queries.
# Use the Flask `jsonify` function to convert your API data to a valid JSON response object.
