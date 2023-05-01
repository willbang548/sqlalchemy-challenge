#import the dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
#Define the Welcome Route
@app.route('/')
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API! <br>
    Available Routes: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/temp/start/end
    ''')

#Define the Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
    #Create a dictionary with the date as the key and the precipitation as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#Define the Stations Route
@app.route("/api/v1.0/stations")
def stations():
    #Query for the stations
    stations = session.query(Station.station, Station.name).all()
    #jsonify the results into a dictionary
    stations_dict = dict(stations)
    return jsonify(stations_dict=stations_dict)

#Define the TOBS Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    #Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()
    #Unravel the results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    #Return the results
    return jsonify(temps=temps)

#Define the Statistics Route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        #Calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
        filter(Measurement.date >= start).all()
        #Convert the results into a dictionary
        temps = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
        #Return the results
        return jsonify(temps=temps)
    
    #Calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    #Convert the results into a dictionary
    temps = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    #Return the results
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)


