import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date/<start><br/>"
        f"/api/v1.0/start-end-date/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of prcp data based on date"""
    # Query all Measurements
    results = session.query(Measurement).all()

    # Convert the query results to a Dictionary using date as the key and prcp as the value
    prcp_dates = []
    for measurement in results:
        measurement_dict = {}
        measurement_dict[measurement.date] = measurement.prcp
        prcp_dates.append(measurement_dict)

    return jsonify(prcp_dates)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    # Query all stations
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    # Set Start and End Date Variables
    end_date = datetime.datetime(2017, 8, 23)
    start_date = end_date + datetime.timedelta(-365)

    # Query Temperature Data for the Previous Year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date).all()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)

@app.route("/api/v1.0/start-date/<start>")
def calc_temps_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date"""
    # Query Data for Calculations
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert list of tuples into normal list
    temp_calcs = list(np.ravel(results))

    return jsonify(temp_calcs)

@app.route("/api/v1.0/start-end-date/<start>/<end>")
def calc_temps_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""    
    # Query Data for Calculations
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert list of tuples into normal list
    temp_calcs = list(np.ravel(results))

    return jsonify(temp_calcs)

if __name__ == '__main__':
    app.run(debug=True)