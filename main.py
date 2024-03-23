from flask import Flask, jsonify, request
from jsonschema import validate
from marshmallow import Schema, fields, ValidationError
import jsonschema
import json
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from dotenv import dotenv_values
import time

app = Flask(__name__)

queue = []
neural = []

config = dotenv_values(".env")
pc = Pinecone(api_key = config["PINECONE_API_KEY"])
openAi_key = config["OPENAI_API_KEY"]
index = pc.Index("secon-1", dimension=1536)

class RequiredSchema(Schema):
    UserId = fields.String(required=True)
    MessageText = fields.String(required=True)

@app.route('/api/ping', methods = ['GET'])
def Ping():
    return jsonify({'message': 'pong'})

"""
Queue routes
"""
@app.route('/api/queue', methods = ['GET'])
def GetQueue():
    return jsonify({'queue': queue})

@app.route('/api/queue', methods = ['POST'])
def AddToQueue():
    data = request.get_json()
    schema = RequiredSchema()
    try:
        result = schema.load(data)
    except ValidationError as e:
        return "Bad Request", 400

    queue.append((result['UserId'], result['MessageText']))
    return jsonify({'total_entities_neural': f'{len(queue)}'})

"""
Neural Routes
"""
@app.route('/api/neural', methods = ['GET'])
def GetNeural():
    return jsonify({'neural': neural})

@app.route('/api/neural', methods = ['POST'])
def AddToNeural():
    data = request.get_json()
    schema = RequiredSchema()
    try:
        result = schema.load(data)
    except ValidationError as e:
        return "Bad Request", 400

    neural.append((result['UserId'], result['MessageText']))

    embeddings = OpenAIEmbeddings(api_key=openAi_key)
    vector = embeddings.embed_query(str(result))
    index.upsert(vectors=[{"id": f"{time.time()}", "values": vector}], )
    return jsonify({'total_entities_neural': f'{len(neural)}.'})

@app.route('/api/test', methods = ['POST'])
def Test():
    pc = Pinecone(api_key="159e533b-5d20-4f3c-93c1-5277f3df9cdb")
    index = pc.Index("secon-1", dimension=1536)  # Укажите желаемую размерность векторов

    text = "Privetik, kak delishki?"

    embeddings = OpenAIEmbeddings(api_key='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')

    vector = embeddings.embed_query(text)

    index.upsert(vectors=[{"id": f"{time.time()}", "values": vector}], )
    return jsonify({'OK'})

if __name__ == '__main__':
    print("was started")
    app.run(host = "0.0.0.0", debug=True)