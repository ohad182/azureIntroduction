import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

bing_subscription_key = "4bffaa212448412d9f3b714927033b7e"
bing_search_url = "https://api.bing.microsoft.com/v7.0/search"

template_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>

<form action="{{ url_for('search') }}" method="post">
    <label for="public-figure">Public figure:</label><br>
    <input type="text" id="public-figure" name="public-figure" value="{{ current_search }}"><br>
    <input type="submit" value="Submit">
</form>

{% if search_link %}
    <a href="{{ search_link }}" target="_blank">Open on Instagram</a>
{% endif %}

<h1>Recent search terms:</h1>
<ul>
    {% for search_term in search_terms %}
        <li>{{ member }}</li>
    {% endfor %}
</ul>
</body>
</html>"""


def search_bing(text):
    search_term = f"{text} instagram" if "instagram" not in text else text
    headers = {"Ocp-Apim-Subscription-Key": bing_subscription_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(bing_search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    return search_results


@app.route('/search_bing', methods=['POST'])
def search():
    current_search = request.form['public-figure']
    search_results = search_bing(current_search)
    web_pages = search_results.get('webPages', dict()).get('value', [])
    if len(web_pages) == 0:
        return "No Results Found"
    else:
        return render_template_string(template_string, current_search=current_search, search_link=web_pages[0]['url'])


@app.route("/")
def hello():
    return render_template_string(template_string, current_search="")
    # return "Hello, World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
