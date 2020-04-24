import os
import json
from flask import Flask
from flask import request
from notion.client import NotionClient
from notion.block import TextBlock
from dotenv import load_dotenv
load_dotenv()

# env
token_v2 = os.getenv('token_v2')
config_url = os.getenv('config_url')

client = NotionClient(token_v2=token_v2)

def getConfigMap():
    conf = {}
    config_collection = getBlock(config_url)
    for row in config_collection.collection.get_rows():
        if len(row.name) != 0 and len(row.children) != 0:
            if row.children[0].type == "collection_view_page":
                conf[row.name] = row.children[0]
    return conf


def getBlock(id):
    return client.get_block(id)

def getCollectionView(url):
    return client.get_collection_view(url)

def getProps(collection):
    return list(map(lambda prop : prop['slug'], collection.get_schema_properties()))

def addDbEntry(collection, data):
    print(collection.parent.views)
    row = collection.add_row()
    props = getProps(collection)
    for prop in data:
        if 'content' == prop:
            print("content!")
            row.children.add_new(TextBlock, title=data[prop])
        elif prop in props:
            print(prop, data[prop])
            row.__setattr__(prop, data[prop])

app = Flask(__name__)

@app.route('/')
def index():
    return "OK!"

@app.route('/addDbEntry')
def addEntry():
    conf = getConfigMap()
    if hasattr(request, 'data') and request.data != None:
        try:
            data = json.loads(request.data)
        except:
            return "NO JSON!", 400
    else:
        return "No JSON!", 400
    
    if 'type' in data and data['type'] in conf:
        dbViewPageBlock = conf[data['type']]
        addDbEntry(dbViewPageBlock.collection, data)
        return "Added {} - {} to {}".format(data['name'], data['content'], data['type']), 200
            
    return "Bad Request : invalid type sent " + data['type'], 400

if __name__ == "__main__":
    app.run()
