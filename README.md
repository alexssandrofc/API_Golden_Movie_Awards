# Golden Movie Awards!
API para leitura da lista de indicadores e vencedores do evento.

## Install python
$ sudo apt-get install python3 python3-dev

## Install libs python
$ pip install fastapi uvicorn sqlalchemy pytest httpx

## Install uvicorn linux
$ sudo apt install uvicorn

## To run aplication
$ uvicorn main:app --reload

## to run testes integration
$ pytest teste_main.py

## Ao iniciar o programa a API carrega os dados do CSV conforme formato disponibilizado ("movielist.csv")

## Endpoint para inserir novo movie
```
curl --location --request POST 'http://127.0.0.1:8000/movies' \
--header 'Content-Type: application/json' \
--data-raw '{
        "year": 2019,
        "title": "Alex: Last Blood",
        "studios": "Lionsgate",
        "producer": "Avi Lerner, Kevin King Templeton, Yariv Lerner, and Les Weldon",
        "winner": "Yes"
    }'
```

## Endpoint para editar movie
```
curl --location -g --request PUT 'http://127.0.0.1:8000/movies/{movieId}' \
--header 'Content-Type: application/json' \
--data-raw '{
        "year": 2019,
        "title": "Alex: Last Blood",
        "studios": "Lionsgate",
        "producer": "Avi Lerner, Kevin King Templeton, Yariv Lerner, and Les Weldon",
        "winner": "Yes"
    }'
```

## Endpoint para pesquisar todos movies
```
curl --location -g --request GET 'http://127.0.0.1:8000/movies' \
--header 'Content-Type: application/json'
```

## Endpoint para pesquisar movie by ID
```
curl --location -g --request GET 'http://127.0.0.1:8000/movies/{movieId}' \
--header 'Content-Type: application/json'
```

## Endpoint para deletar movie
```
curl --location -g --request Delete 'http://127.0.0.1:8000/movies/{movieId}' \
--header 'Content-Type: application/json'
```

## Endpoint para obter lista de vencedores
```
curl --location -g --request GET 'http://127.0.0.1:8000/producers/winnerintervals' \
--header 'Content-Type: application/json'
```
