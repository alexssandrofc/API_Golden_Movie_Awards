from typing import Optional, List
import pandas as pd
from collections import defaultdict, deque
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Create Db in Memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True, poolclass=StaticPool,)

# Create Session on DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Movie model ORM
class Movie(Base):
    __tablename__ = "movie"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    year = Column(Integer, index=True)
    title = Column(String, index=True)
    studios = Column(String, index=True)
    producer = Column(String, index=True)
    winner = Column(String, index=True)

# create tables in DB
Base.metadata.create_all(bind=engine)
        
# Read CSV data to init DB
def get_data_from_csv(db: Session):
    df = pd.read_csv('movielist.csv', delimiter=';')
    #print(df)
    for i,row in df.iterrows():
        movie = Movie(year=row["year"], title=row["title"], studios=row["studios"], producer=row["producers"], winner=row["winner"])
        #print(movie.title)
        db.add(movie)
    db.commit()
    #print("dados csv commitados...")

# Inicializa o banco de dados com dados do CSV
db = SessionLocal()
get_data_from_csv(db)
db.close()

# Model movie
class MovieCreate(BaseModel):
    year: int
    title: str
    studios: str
    producer: str
    winner: str

class MovieResponse(BaseModel):
    id: int
    year: int
    title: str
    studios: str
    producer: str
    winner: Optional[str] = None

    class Config:
        from_attributes = True

class ProducerInterval(BaseModel):
    producer: str
    interval: int
    previousWin: int
    followingWin: int

class ProducerIntervalResponse(BaseModel):
    min: List[ProducerInterval]
    max: List[ProducerInterval] 

#FastAPI
app = FastAPI()

# get Session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# gel all movies
@app.get("/movies", response_model=list[MovieResponse])
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()

# get movie by ID
@app.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# get winner_interval
@app.get("/producers/winnerintervals", response_model=ProducerIntervalResponse)
def get_produce_winner_intervals(db: Session = Depends(get_db)):
    min_intervals = db.execute("SELECT title,producer,prevYear, followYear, diff FROM (SELECT m1.title as title, m1.producer as producer,m1.year as prevYear, m2.year as followYear, ABS(m1.year - m2.year) AS diff FROM movie m1 JOIN movie m2 ON m1.id != m2.id and m1.producer = m2.producer and m1.winner = 'yes' and m2.winner = 'yes' group by m1.producer order by diff) AS differences")
    max_min_intervals = db.execute("SELECT max(diff) as maxvalues, min(diff) as minvalues FROM (SELECT m1.title as title, m1.producer as producer,m1.year as prevYear, m2.year as followYear, ABS(m1.year - m2.year) AS diff FROM movie m1 JOIN movie m2 ON m1.id != m2.id and m1.producer = m2.producer and m1.winner = 'yes' and m2.winner = 'yes' group by m1.producer order by diff) AS differences")
    
    max_value = -1
    min_value = -1
    for row in max_min_intervals:
        aux = row["maxvalues"]
        min_value = row["minvalues"]
        if(aux > min_value):
            max_value = aux
    
    print(min_value)
    print(max_value)

    winners_min_list = []
    winners_max_list = []
    d = defaultdict(lambda: deque)

    for row in min_intervals:
        #print(row["producer"])    
        if(row["diff"] == min_value):
            winners_min_list.append(ProducerInterval(producer=row["producer"],interval=row["diff"],previousWin=row["prevYear"],followingWin=row["followYear"]))
        
        if(row["diff"] == max_value):
            winners_max_list.append(ProducerInterval(producer=row["producer"],interval=row["diff"],previousWin=row["prevYear"],followingWin=row["followYear"]))

    if len(winners_min_list) == 0:
        winners_min_list.append(ProducerInterval(producer="N/A",interval=0,previousWin=0,followingWin=0))
    
    if len(winners_max_list) == 0:
        winners_max_list.append(ProducerInterval(producer="N/A",interval=0,previousWin=0,followingWin=0))

    print(winners_min_list)
    return ProducerIntervalResponse(min=winners_min_list, max=winners_max_list)

# create movie
@app.post("/movies", response_model=MovieResponse, status_code=201)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_Movie = Movie(year=movie.year,title=movie.title,studios=movie.studios,producer=movie.producer,winner=movie.winner)
    db.add(db_Movie)
    db.commit()
    db.refresh(db_Movie)
    return db_Movie

# update movie by ID
@app.put("/movies/{movie_id}", response_model=MovieResponse)
def update_Movie(movie_id: int, updated_movie: MovieCreate, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie.year=updated_movie.year
    movie.title=updated_movie.title
    movie.studios=updated_movie.studios
    movie.producer=updated_movie.producer
    movie.winner=updated_movie.winner
    db.commit()
    db.refresh(movie)
    return movie

# delete movie by ID
@app.delete("/movies/{movie_id}", status_code=204)
def delete_Movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)