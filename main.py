import requests
from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup - Replace connection string with your MongoDB Atlas connection string
connection_string = "mongodb+srv://BDAT100:BDAT100@bdat.mfhgbz0.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)
database_name = "stockDP"
collection_name = "market"




client = MongoClient(connection_string)
database = client[database_name]
collection = database[collection_name]



@app.route('/')
def index():
    # Make the API call
    api_key = "e2b03e2ecdmshc9313caefdd3328p18753ejsn1ff14d4fd7df"
    url = "https://latest-stock-price.p.rapidapi.com/price"
    query_params = {
        "Indices": "NIFTY 50"
    }
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "latest-stock-price.p.rapidapi.com"
    }

    response = requests.get(url, params=query_params, headers=headers)

    if response.status_code == 200:
        api_data = response.json()
        stock_data_list = api_data

        # Clear previous data
        collection.delete_many({})

        # Insert data into MongoDB
        if stock_data_list:
            collection.insert_many(stock_data_list)

        return render_template('index.html', stock_data=stock_data_list)
    else:
        return "API Error: " + str(response.status_code)

@app.route('/stockvolumedistribution')
def histogram_chart():  # Changed function name to 'histogram_chart'
    return render_template('stockvolumedistribution.html', stock_data=collection.find({}))

@app.route('/stockpricechange')
def bar_chart():
    return render_template('stockpricechange.html', stock_data=collection.find({}))

@app.route('/dayhighvalues')
def pie_chart():
    return render_template('dayhighvalues.html', stock_data=collection.find({}))

@app.route('/stockdatasummary')
def stock_data():
    return render_template('stockdatasummary.html', stock_data=collection.find({}))

# API Routes
@app.route('/api/items', methods=['GET'])
def get_all_items():
    items = list(collection.find({}, {'_id': 0}))
    return jsonify(items)

@app.route('/api/items/range/<field>/<start>/<end>', methods=['GET'])
def get_items_in_range(field, start, end):
    try:
        # Convert start and end values to float
        start_value = float(start)
        end_value = float(end)

        # Query for documents within the specified range based on the field
        items = list(collection.find({field: {'$gte': start_value, '$lte': end_value}}, {'_id': 0}))

        return jsonify(items)
    except Exception as e:
        return str(e), 400


@app.route('/api/items/<item_id>', methods=['GET'])
def get_item_by_id(item_id):
    try:
        item = collection.find_one({'identifier': item_id}, {'_id': 0})
        if item:
            return jsonify(item)
        else:
            return jsonify({'message': 'Item not found'}), 404
    except Exception as e:
        return str(e), 400



if __name__ == "__main__":
    app.run(debug=True)