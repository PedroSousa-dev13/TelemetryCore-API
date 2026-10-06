from typing import Literal
from datetime import datetime
from fastapi import FastAPI, HTTPException, Response,Depends, Query, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models


Base.metadata.create_all(bind=engine)


app = FastAPI()



class sensorCreate(BaseModel): # criacao da classe sensor 
    nome:str =Field (..., min_length=3, max_length=100) # nome que é uma string de caracteres minimos 3 e caracteres maximos 100
    tipo: Literal["temperatura", "pressao", "vibracao", "humidade"] # o tipo é um literal de escolha fixa
    localizacao:str=Field(..., min_lenght=3, max_length=150) # localizacao em string tambem limitada ás condicoes acima

class LeituraCreate(BaseModel): # nova classe leitura obriga a um float que é o valor e uma string de caracteres maximos 10
  valor:float
  unidade:str =Field(...,max_length=10)

#nome: str | None = Field(default=None, min_length=3, max_length=100)
#    tipo: Literal["temperatura", "pressao", "vibracao", "humidade"] | None = None
  #  localizacao: str | None = Field(default=None, min_length=3, max_length=150)


class patchSensor(BaseModel):
    nome:str | None=Field (default=None,min_length=3,max_length=100)
    tipo:Literal["temperatura","pressao","vibracao","humidade"] |None=None
    localizacao:str |None=Field(default=None,min_length=3,max_length=150)

@app.get("/health")
def health():
    return {"status": "ok"}
def health_db(db:Session=Depends(get_db)):
    return {"status":"ok"}

@app.get("/sensores")
def sensores():
    return []

def listar_sensores(db:Session=Depends(get_db), 
    skip:int= Query(0, ge=0),
    limit:int=Query(100, ge=1,le=100),  #aqui defino o limite de leituras que podem ser feitas na database, no caso 100
    # sendo ge o limite minimo e le o limite maximo,
    ):
                    
    query = db.query(models.Sensor)

    return {
        "total":query.count(),
        "items" :query.offset(skip).limit(limit).all(),# aqui ignora os primeiros skip que sao introduzidos pelo utilizador ao invocar a funcao,
        #limit sera a quantidade de sensores 
    }

@app.post("/sensores",status_code=201) #aqui faço o post da invocacao da funca sensores se a mesma correr bem retirbui status 201
# 
def criar_sensor(   
    sensor: sensorCreate, 
    db:Session=Depends(get_db) #valida se a sessão est+a ativa na db
    ):
    novo_sensor=models.Sensor( 
        nome=sensor.nome, 
        tipo=sensor.tipo,
        localizacao=sensor.localizacao,
    )

    db.add(novo_sensor) # adiciona á database o novo sensor
    db.commit()     # faz commit das alterações na database
    db.refresh(novo_sensor) # da refresh á database
    return novo_sensor 

@app.get("/sensores/{sensor_id}")

def obtain_sensores ( #aqui a funcao necessita de 1 inteiro, e valida se a sessão na database está ativa
    sensor_id :int,
    db: Session = Depends(get_db)
    ):
        sensor=(
            db.query(models.Sensor) # faz uma query para procurar pelos sensores
            .filter(models.Sensor.id==sensor_id) # aqui a database vai verirficar qual o id e atribuir o mesmo ao sensor id
            .first()
        )
        if sensor is None:
            raise HTTPException (
                status_code=404,
                detail="Sensor não encontrado"
            )
        return sensor

@app.delete ("/sensores/{sensor_id}") # elimina o sensor

def eliminar_sensor( 
    sensor_id: int, #recebe um inteiro
    db:Session=Depends(get_db), # verifica se a base de dados esta de pe
    ):

    sensor=( 
        db.query(models.Sensor)
        .filter(models.Sensor.id==sensor_id)
        .first()
    )
    if sensor is None:
        raise HTTPException(
        status_code=404,
        detail="O sensor em questão nao foi encontrado na base de dados"      
    )
    db.delete(sensor)
    db.commit()

    return Response(status_code=204)
    
@app.post("/sensores/{sensor_id}/leituras", status_code=201)

def criar_letitura (sensor_id:int, leitura:LeituraCreate,db:Session=Depends(get_db)):
    sensor=(
        db.query(models.Sensor)
        .filter(models.Sensor.id==sensor_id)
        .first()
    )

    if  sensor is None:
        raise HTTPException(
            status_code=404,
            detail =" Sensor nao existe"
        )  


    nova_leitura =models.Leitura(

        sensor_id=sensor_id,
        valor=leitura.valor,
        unidade=leitura.unidade,

    )
    
    db.add(nova_leitura)
    db.commit()
    db.refresh(nova_leitura)


    return nova_leitura

@app.get("/sensores/{sensor_id}/leituras") # api call para receber as leituras associdas ao id do sensor

def ler_leituras(sensor_id:int, db:Session=Depends(get_db),
    skip:int= Query(0, ge=0),
    limit:int=Query(100, ge=1,le=100),
    ):
    sensor= (
        db.query(models.Sensor)
        .filter(models.Sensor.id==sensor_id)
        .first()
     )

    if sensor is None:
        raise HTTPException(
        status_code=404,
        detail="Sensor nao existe"
      )

    query =db.query(models.Leitura).filter(models.Leitura.sensor_id==sensor_id) 

    return{
               
        "total":query.count(),
        "items" :query.offset(skip).limit(limit).all(),# aqui ignora os primeiros skip que sao introduzidos pelo utilizador ao invocar a funcao,
        #limit sera a quantidade de sensores 
    }

@app.put("/sensores/{sensor_id}")

def alterar_sensor(
    sensor_id:int, 
    dados:sensorCreate,
    db:Session=Depends(get_db),
):
    sensor = (
        db.query(models.Sensor)
        .filter(models.Sensor.id == sensor_id)
        .first()
    )


    if sensor is None:
     raise HTTPException(
        status_code= 404,
        detail="Nao existe nenhum sensor associado a esse ID"
    )

    sensor.nome=dados.nome
    sensor.tipo=dados.tipo
    sensor.localizacao=dados.localizacao

    db.commit(),
    db.refresh(sensor)

    return sensor

@app.patch("/sensores/{sensor_id}")

def alterar_parcial(
    sensor_id:int,
    dados:patchSensor,
    db:Session=Depends(get_db ),
):
    #encontra o sensor na bd
    sensor=(
        db.query(models.Sensor)
        .filter(models.Sensor.id==sensor_id)
        .first()
    )
    # aborta se nao existir sensor com o id mandado
    if sensor is None:
        raise HTTPException(
            status_code= 404,
            detail ="Nao existe nenhum sensor associado a esse ID"
        )
    
    alteracoes=dados.model_dump(exclude_unset=True) # aqui a funcao modeldump vai excluir os campos que nao foram alterados, ou seja, que nao foram setados

    # se nao houver alterações ou seja, se o dicionario estiver vazio, vai levantar uma excecao HTTP 404
    if not alteracoes :
        raise HTTPException(
            status_code=422,
            detail= "Enviar pelo menos 1 parametro a ser atualizado"
        )
    
    # aqui a funcao setattr vai percorrer o dicionario alteracoes e vai setar os campos do sensor com os valores correspondentes
    for campo,valor in alteracoes.items():
        setattr(sensor,campo,valor)

    db.commit()
    db.refresh(sensor)

    return sensor


@app.get("/leituras/{id_leitura}")
def obter_leituras_id (

    id_leitura:int,
    db:Session=Depends(get_db),
    ):

    leitura = (
        db.query(models.Leitura)
        .filter(models.Leitura.id==id_leitura)
        .first()
    )

    if leitura is None:
        raise HTTPException(
            status_code= 404,
            detail= "Não existe nenhuma leitura com esse id"
        )

    return leitura


@app.delete("/leituras/{id_leitura}")
def apagar_leitura_id (
    id_leitura:int,
    db:Session=Depends(get_db),
    ):  

    leitura=(
        db.query(models.Leitura)
        .filter(models.Leitura.id==id_leitura)
        .first()

    )

    if leitura is None:
        raise HTTPException(
            status_code= 404,
            detail=" Não existe leitura com esse id"
        )

    db.delete(leitura)
    db.commit()
    return Response( status_code=204)



@app.get("/sensores/{sensor_id}/leituras/")
def sensor_id_leitura_tipo(
    sensor_id:int,
    tipo_leitura:Literal[
        "temperatura",
        "vibracao",
        "pressao",
        "humidade"
    ]=Query(...),
    db:Session=Depends(get_db),
    ):

    

    sensor=(
        db.query(models.Sensor)
        .filter(models.Sensor.id==sensor_id)
        .first()
    ) 
    
    if sensor is None:
          raise  HTTPException (
                status_code= 404,
                detail=" Não existe ou leirura com este id ou sensor com este id "
            )
    

    leituras=(
        db.query(models.Leitura)
        .join( models.Sensor,models.Sensor.id==models.Leitura.sensor_id) #aqui faz a uniao das tabelas na query, procura por sensor id e verifica se o mesmo existe em alguma leitura com o mesmo id de sensor
        .filter(models.Leitura.sensor_id==sensor_id, models.Sensor.tipo==tipo_leitura) #aqui faz a filtragem de leituras com o sensor id e puxa os que tem o mesmo tipo introduzido
        .all()
    )



   
    return leituras


@app.get("/sensores/{id_sensor}/leituras/stats")
def estatisticas_sensor_por_id (
    id_sensor:int,
    db:Session=Depends(get_db),
):
    sensor=(
        db.query(models.Sensor)
        .filter(models.Sensor.id==id_sensor)
        .first()
    )

    if sensor is None:
        raise HTTPException(
            status_code=404,
            detail="Não existe sensor com este id"
        )

    resultado= (
       db.query(
           func.count(models.Leitura.id),
           func.min(models.Leitura.valor),
           func.max(models.Leitura.valor),
           func.avg(models.Leitura.valor),
       )
       .filter(models.Leitura.sensor_id==id_sensor)
       .one()
       
   )
    return{
        "count":resultado[0],
        "min": resultado[1],
        "max": resultado[2],
        "media": resultado[3],
 }


@app.get ("/sensores/{id_sensor}/leituras/intervalo")
def leituras_por_intervalo (
    id_sensor:int,
    data_inicio:datetime|None=Query(None),
    data_fim:datetime|None=Query(None),
    db:Session=Depends(get_db),
):
    query=db.query(models.Leitura).filter(models.Leitura.sensor_id==id_sensor)

    if data_inicio:
        query=query.filter(models.Leitura.timestamp>=data_inicio)

    if data_fim:
        query=query.filter(models.Leitura.timestamp<=data_fim)


    return query.all()


# se um sensor nao possuir dados o mesmo tem que ser printado

@app.get("/sensores/{id_sensor}/sem_leituras")
def sensores_sem_leituras( 
    db:Session=Depends(get_db),
    ):

    sensores=( # abre a lista sensores como sensores
        db.query(models.Sensor)  # da search na base de dados pela tabela sensores 
        .filter(~models.Sensor.leituras.any()) # aqui faz a filtracao da tabela sensores que nao possuem leituras
        .all()
    )
    return sensores


@app.get("/sensores/leituras/tipo")
def filtragem_sensores_por_tipo(
    tipo:Literal["temperatura","vibracao","pressao","humidade"] =Query(...), # defino as opcoes de tipo de sensor
    db:Session=Depends(get_db), # peço a sessao á base de dados para verificar a sessao ativa
):
    leituras=( # faço uma query na base de dados que vai á tabela leituras 
        db.query(models.Leitura)
        .join(models.Sensor) # aqui faço a junção da tabela leituras com a tabela sensores 
        # organizando os dados pela primary key sensor_id
        .filter(models.Sensor.tipo==tipo) # aqui faço a filtragem dos sensores pelo input do utilizador
        .all()
    )

    if not leituras: # se não houver leituras levanta uma execessao 
        raise HTTPException(
            status_code=404,
            detail= "Nao existem leituras desse tipo"
        )


    return leituras


@app.exception_handler(Exception) # uso o exception handler para capturar erros que não foram definidos
# e rotorno a resposta em formato json com o codigo de erro 500 e detalhes do erro
def exception_handler(
    request: Request,
    exc : Exception ):

    raise JSONResponse(

        status_code=500,
        content= {"detail":"Erro interno do servidor"},
    )

@app.exception_handler(RequestValidationError) # uso o o exception handler para capturar erros de validacao de requests
# e retornar uma resposta formato json com o codigo de erro 422 e detalhes do erro
def error_validation(
    request:Request,
    exc:RequestValidationError,
):
    raise JSONResponse(
        eror_code=422,
        content={"detail":jsonable_encoder(exc.errors())}

    )


@app.exception_handler(HTTPException) # uso o httpexception para capturar todos os erros do genero 404 
def error_not_found(    
    request:Request,
    exc:Exception,
):

    raise JSONResponse(
        status_code=404,
        content={"detail":exc.detail()},
    )