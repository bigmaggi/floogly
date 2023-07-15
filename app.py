from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

def search_documents(query, limit=20):
    es = Elasticsearch([{"host": "localhost", "port": 9200, "scheme": "http"}])

    if not es.indices.exists(index="web_indexer"):
        es.indices.create(index="documents")

    response = es.search(index="web_indexer", body={
        "query": {
            "match_phrase": {  # Use match_phrase for phrase search
                "content": query
            }
        },
        "size": limit
    })

    # Filter out duplicates
    results = response['hits']['hits']
    seen_urls = set()
    unique_results = []
    for result in results:
        url = result['_source']['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    return unique_results

@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = []
    total_results = 0  # Variable to store the total number of results

    if request.method == 'POST':
        query = request.form.get('query')
        search_results = search_documents(query)
        total_results = len(search_results)  # Count the total number of results

    return render_template('index.html', search_results=search_results, total_results=total_results)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

