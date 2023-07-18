from elasticsearch import Elasticsearch
from flask import Flask, render_template, request
from datetime import datetime
import openai
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)

es = Elasticsearch('http://202.61.236.229:9200')

# OpenAI API configuration
openai.api_key = 'your api key here'

def perform_search(query, search_body):
    prompt = f"chatgpt3.5: {query}"

    start_time_gpt = datetime.now()
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=256,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    end_time_gpt = datetime.now()
    gpt_response_time = (end_time_gpt - start_time_gpt).total_seconds()
    chat_response = response.choices[0].text.strip()

    start_time = datetime.now()
    response = es.search(
        index='web_indexer',
        body=search_body
    )
    end_time = datetime.now()
    search_time = (end_time - start_time).total_seconds()

    total_hits = response['hits']['total']['value']

    search_results = []
    for hit in response['hits']['hits']:
        result = {
            'title': hit['_source'].get('title', hit['_source'].get('url', '')),
            'url': hit['_source'].get('url', '')
        }
        search_results.append(result)

    return chat_response, search_results, total_hits, search_time, gpt_response_time


@app.route('/', methods=['GET', 'POST'])
def index():
    query = ''
    search_results = []
    total_results = 0
    search_time = 0
    chat_response = ''
    gpt_response_time = 0

    if request.method == 'POST':
        query = request.form['query']
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"content": query}}
                    ]
                }
            },
            "size": 1000,
            "track_total_hits": True
        }
        try:
            chat_response, search_results, total_results, search_time, gpt_response_time = perform_search(query, search_body)
        except Exception as e:
            return f"Error occurred: {str(e)}"

    return render_template('index.html', query=query, chat_response=chat_response, 
                           search_results=search_results, total_results=total_results, 
                           search_time=search_time, gpt_response_time=gpt_response_time)

if __name__ == "__main__":
    app.run(ssl_context=('/etc/letsencrypt/live/search.nightmare.life/fullchain.pem', '/etc/letsencrypt/live/search.nightmare.life/privkey.pem'), host='0.0.0.0', port=443)

