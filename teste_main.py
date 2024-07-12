import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from main import app, get_db, Base, Movie,ProducerInterval
from sqlalchemy.pool import StaticPool

# Create Db in Memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True, poolclass=StaticPool,)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuração do banco de dados de teste
Base.metadata.create_all(bind=engine)

# Dependência para obter a sessão do banco de dados de teste
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_movie(db):
    response = client.post("/movies", json={"year": "1999", "title":"The Mask", "studios":"MGM", "producer":"John F.", "winner":"Yes"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "The Mask"
    assert "id" in data

def test_get_movies(db):
    # Criando usuários para o teste
    client.post("/movies", json={"year": "1999", "title":"The Mask", "studios":"MGM", "producer":"John F.", "winner":"Yes"})
    client.post("/movies", json={"year": "2001", "title":"The Mask II", "studios":"MGM", "producer":"John F.", "winner":"Yes"})

    response = client.get("/movies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "The Mask"
    assert data[1]["title"] == "The Mask II"

def test_get_movie(db):
    # Criando um usuário para o teste
    response = client.post("/movies", json={"year": "2001", "title":"The Mask II", "studios":"MGM", "producer":"John F.", "winner":"Yes"})
    movie_id = response.json()["id"]

    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Mask II"
    assert data["id"] == movie_id

def test_update_movie(db):
    # Criando um usuário para o teste
    response = client.post("/movies", json={"year": "2001", "title":"Error II", "studios":"MGM", "producer":"John F.", "winner":"Yes"})
    movie_id = response.json()["id"]

    response = client.put(f"/movies/{movie_id}", json={"year": "2001", "title":"The Mask II", "studios":"MGM", "producer":"John F.", "winner":"Yes"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Mask II"
    assert data["id"] == movie_id

def test_delete_movie(db):
    # Criando um usuário para o teste
    response = client.post("/movies", json={"year": "2001", "title":"The Mask II", "studios":"MGM", "producer":"John F.", "winner":"Yes"})
    movie_id = response.json()["id"]

    response = client.delete(f"/movies/{movie_id}")
    assert response.status_code == 204

    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 404

def test_get_prod_winners(db):
    # Criando um usuário para o teste
    response = client.post("/movies", json={"year": "2001", "title":"The Mask I", "studios":"MGM", "producer":"John F.", "winner":"yes"})
    response = client.post("/movies", json={"year": "2002", "title":"The Mask II", "studios":"MGM", "producer":"John F.", "winner":"yes"})
    response = client.post("/movies", json={"year": "2012", "title":"The Mask III", "studios":"MGM", "producer":"John G.", "winner":"yes"})
    response = client.post("/movies", json={"year": "2015", "title":"The Mask IV", "studios":"MGM", "producer":"John G.", "winner":"yes"})
    response = client.post("/movies", json={"year": "2018", "title":"The Mask V", "studios":"MGM", "producer":"John H.", "winner":"yes"})
    response = client.post("/movies", json={"year": "2000", "title":"The Mask VI", "studios":"MGM", "producer":"John H.", "winner":""})

    response = client.get(f"/producers/winnerintervals")
    assert response.status_code == 200
    data = response.json()
    
    assert data["min"][0]["producer"] == "John F."
    assert data["max"][0]["producer"] == "John G."