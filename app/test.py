import pandas as pd
import plotly
import json 

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar

import joblib
from sqlalchemy import create_engine

app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens

# load data
engine = create_engine('sqlite:///../data/DB_LAB04.db')
df = pd.read_sql_table('disaster_messages', engine)
pl1 = pd.read_csv('../data/plot/genre_counts.csv')
pl2 = pd.read_csv('../data/plot/top5cates.csv')
pl3 = pd.read_csv('../data/plot/corr.csv')


# load model 
model = joblib.load("../models/classifier.pkl")

# index webpage visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = pl1['message']
    genre_names = pl1['genre']
    
    category_names = pl2['category']
    category_counts = pl2['counts']
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        # plot for genre
        {
            'data': [
                {
                    'type': 'pie',
                    'labels': genre_names,
                    'values': genre_counts
                }
            ],

            'layout': {
                'title': 'Distribution of Message Genres'
            }
        },
        
        # plot for top 5 category
        {
            'data': [
                Bar(
                    x=category_names,
                    y=category_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Message Categories',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Category"
                }
            }
        },
        
        # plot for correlation
        {
            'data': [
                {
                    'type': 'heatmap',
                    'z': pl3['z'],
                    'x': pl3['x'],
                    'y': pl3['y']
                }
            ],

            'layout': {
                'title': 'Correlation of Essential Needs'
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)

@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '') 
    
    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file. 
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)

if __name__ == '__main__':
    main()
