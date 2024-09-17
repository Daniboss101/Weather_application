from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, exists, and_
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'mysql+mysqlconnector://DBoss:Da$54338012345@localhost/weather_stations'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Station(Base):
    __tablename__ = 'stations'
    id = Column(String(30), primary_key=True)
    station_name = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    mindate = Column(DateTime)
    maxdate = Column(DateTime)
    datacoverage = Column(Float)
    weather_data = relationship('WeatherData', back_populates='station')

class WeatherData(Base):
    __tablename__ = 'weather_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), ForeignKey('stations.id'))
    date = Column(DateTime)
    datatype = Column(String(50))
    value = Column(Float)
    attributes = Column(String(255))
    station = relationship('Station', back_populates='weather_data')




Base.metadata.create_all(engine)

def insert_station(station_data):
    with Session() as session:
        if not session.query(exists().where(Station.id == station_data['id'])).scalar():
            station = Station(**station_data)
            session.add(station)
            session.commit()
            print(f"Inserted station: {station_data['id']}")
        else:
            print(f"Station already exists: {station_data['id']}")

def insert_weather_data(weather_data):
    with Session() as session:
        exists_query = session.query(exists().where(
            and_(
                WeatherData.station_id == weather_data['station_id'],
                WeatherData.date == weather_data['date'],
                WeatherData.datatype == weather_data['datatype']
            )
        )).scalar()

        if not exists_query:
            weather_data_instance = WeatherData(**weather_data)
            session.add(weather_data_instance)
            session.commit()
            print(f"Inserted weather data: {weather_data}")
        else:
            print(f"Weather data already exists: {weather_data}")

