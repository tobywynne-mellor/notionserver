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

# returns {'config name / type' : first child / the collection_view_page}
def getConfigMap():
    conf = {}
    config_collection = getBlock(config_url)
    for row in config_collection.collection.get_rows():
        if len(row.name) != 0 and len(row.children) != 0:
            if row.children[0].type == "collection_view_page":
                conf[row.name] = {"db" : row.children[0]}
            if len(row.children) > 1 and row.children[1].type == "code":
                conf[row.name]["processCode"] = row.children[1].title
    return conf

def getBlock(id):
    return client.get_block(id)

def getCollectionView(url):
    return client.get_collection_view(url)

def getProps(collection):
    return list(map(lambda prop : prop['slug'], collection.get_schema_properties()))

def getTemplate(collection, type):
    templates = collection.templates
    for template in templates:
        if template.name in type:
            return template
    return None

def hasTemplate(collection, temptype):
    templates = collection.templates
    for template in templates:
        if template.name in temptype:
            return True
    return False

def addDbEntry(collection, data):
    print(collection.parent.views)
    row = collection.add_row()
    props = getProps(collection)
    for prop in data:
        if 'content' == prop:
            block = TextBlock
            row.children.add_new(block, title=data[prop])
        elif prop in props:
            row.set_property(prop, data[prop])
    return row

app = Flask(__name__)

@app.route('/')
def index():
    return "OK!"

@app.route('/addDbEntry', methods=['POST'])
def addEntry():
    conf = getConfigMap()
    if hasattr(request, 'data') and request.data != None:
        try:
            data = json.loads(request.data)
        except:
            return "NO JSON!", 400
    else:
        return "No JSON!", 400
    
    if 'secret' not in data and data['secret'] != os.getenv('SECRET_KEY'):
        return "INVALID SECRET", 401

    if 'type' in data and data['type'] in conf:
        dbViewPageBlock = conf[data['type']]['db']
        entry = addDbEntry(dbViewPageBlock.collection, data)
        try:
            exec(conf[data['type']]['processCode'], {'entry': entry})
        except:
            raise EnvironmentError("Error with processCode")
        return "Added {} - {} to {}".format(data['name'], data['content'], data['type']), 200
    return "Bad Request : invalid type sent " + data['type'], 400

if __name__ == "__main__":
    app.run(debug=True)
