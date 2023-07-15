from elasticsearch import Elasticsearch, ElasticsearchException
from urllib.parse import urlparse
from flask import Flask, render_template, request

app = Flask(__name__)

# Elasticsearch connection
es = Elasticsearch('http://localhost:9200')

def perform_search(query):
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": query}}
                ]
            }
        },
        "size": 100  # Adjust the size parameter as needed
    }

    try:
        response = es.search(index='web_indexer', body=search_body, track_total_hits=True)

        search_results = []
        unique_domains = set()

        for hit in response['hits']['hits']:
            domain = urlparse(hit['_source'].get('url', '')).netloc
            if domain not in unique_domains:
                unique_domains.add(domain)
                result = {
                    'title': hit['_source'].get('title', ''),
                    'url': hit['_source'].get('url', '')
                }
                search_results.append(result)

        total_hits = response['hits']['total']['value']  # Extract the total hits
        time_taken = response['took']  # Extract the time taken

        return search_results, total_hits, time_taken  # Return time taken along with search results and total hits
    except ElasticsearchException as e:
        raise e


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        try:
            search_results, total_hits = perform_search(query)  # Receive total_hits here
            return render_template('index.html', search_results=search_results, total_results=total_hits)  # Pass total_hits to template
        except ElasticsearchException as e:
            return f"Error occurred: {str(e)}"

    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

