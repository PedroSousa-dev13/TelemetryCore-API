# TelemetryCore API

Projeto desenvolvido para aprofundar o meu conhecimento em FastAPI, PostgreSQL e algumas bibliotecas de Phyton nomeadamente FASTAPI, SQLAlchemy, Pydantic e Uvicorn.


A aplicação é basicamente uma API REST que permite a gestão de sensores e de leituras de sensores. A API permite criar, ler, atualizar e apagar sensores, bem como criar e ler leituras de sensores ( com filtragem por tipo de sensor, sensor_id etc..). 

## Funcionalidades

- Criar, consultar, atualizar e apagar sensores
- Criar, consultar e apagar leituras
- Paginação de resultados
- Estatísticas das leituras
- Filtros por tipo e intervalo de tempo
- Validação de dados com Pydantic


## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL

## Executar o projeto

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
