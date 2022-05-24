from tracemalloc import start
import numpy as np
from requests import session

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from dateutil.relativedelta import relativedelta

engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home(): 
    #List all routes that are available.
    return (
        f"Welcome to my 'Home' page!<br/>"
        f"(----------------------------------)<br/>"
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation(): 
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    session = Session(engine)
    prec_info = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precipitation_info =[]
    for date, prcp in prec_info:
        prec_dict = {}
        prec_dict['Date'] = date
        prec_dict['Precipitation'] = prcp
        precipitation_info.append(prec_dict)
    
    return jsonify(precipitation_info)


@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    session = Session(engine)

    stations = session.query(Station.station, Station.name).all()

    session.close()

    all_stations =[]
    for station, name in stations:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        all_stations.append(station_dict
        )
    return jsonify(all_stations)
    
   
@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    session = Session(engine)
    
    #Get last 12 months from dataset
    latestdate = session.query(func.max(Measurement.date)).scalar()
    last12months= dt.datetime.strptime(latestdate, '%Y-%m-%d') - dt.timedelta(days=365)
    last12months = last12months.strftime('%Y-%m-%d')

    #Choose the most active station
    high_temp = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()
        
    print(f"The most active station is {high_temp[0]}")
    #Query the dates and temp observations from the station above
    station_temp = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= last12months).\
    filter(Measurement.station == high_temp[0]).all()

    session.close()

    active_station = []
    for date, tobs in station_temp:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['Temperature'] = tobs
        active_station.append(temp_dict)

    return jsonify(active_station)


@app.route("/api/v1.0/<startdate>")
def start_temp(startdate):

    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    session = Session(engine)
    startdate =  dt.datetime.strptime(startdate, '%Y-%m-%d')

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= startdate).all()

    session.close()
    
    tobs_all = []
    for min,avg,max in temp_data:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_all.append(tobs_dict)
    
    return jsonify(tobs_all)

@app.route("/api/v1.0/<startdate>/<enddate>")
def date_based_temp(startdate,enddate):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    session = Session(engine)
    startdate =  dt.datetime.strptime(startdate, '%Y-%m-%d')
    enddate =  dt.datetime.strptime(enddate, '%Y-%m-%d')
    
    temp_data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                filter(Measurement.date >= startdate).filter(Measurement.date <= enddate).all()

    session.close()

    tobsall = []
    for min,avg,max in temp_data:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)
    

if __name__ == "__main__":
    app.run(debug=True)