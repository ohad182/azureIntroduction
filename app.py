import requests
import pyodbc
from flask import Flask, render_template_string, request

app = Flask(__name__)

table_name = "SearchTerms"
bing_subscription_key = "d851a9e5ade844d18a2c7dd548b53a45"
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
        <li>{{ search_term['searchTerm'] }}</li>
    {% endfor %}
</ul>
</body>
</html>"""


def get_database_connection_string():
    # return "DRIVER={ODBC Driver 13 for SQL Server};Server=tcp:web-app-sql-srv-ohadc.database.windows.net;Database=web-app-sql-db-ohadc;User ID=db_admin@web-app-sql-srv-ohadc;Password=db_Password!;Trusted_Connection=False;Encrypt=True;"
    return "Driver={ODBC Driver 17 for SQL Server};Server=tcp:web-app-sql-srv-ohadc.database.windows.net,1433;Database=web-app-sql-db-ohadc;Uid=db_admin;Pwd=db_Password!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"


def get_connection():
    connection_string = get_database_connection_string()
    connection = pyodbc.connect(connection_string)
    return connection


def dict_factory2(cursor):
    columns = [d[0] for d in cursor.description]

    def create_row(*args):
        return dict(zip(columns, args))

    return create_row


def get_recent_search_terms():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("select * from {} ORDER BY ID DESC".format(table_name))
    all_items_dict = cursor.fetchall()
    recent_search_terms = [dict(zip([column[0] for column in cursor.description], row)) for row in all_items_dict]
    return recent_search_terms


def add_search_term_to_db(search_term, search_result):
    connection = get_connection()
    cur = connection.cursor()
    try:
        cur.execute("INSERT INTO SearchTerms (searchTerm, webPage) values(?, ?)", search_term, search_result)
        cur.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        connection.close()


def create_table():
    connection = get_connection()
    cursor = connection.cursor()
    print("Create table")
    try:
        cursor.execute(
            """IF OBJECT_ID(N'dbo.SearchTerms', N'U') IS NULL BEGIN   
                    CREATE TABLE SearchTerms (
                        ID INT IDENTITY(1,1) PRIMARY KEY CLUSTERED, 
                        searchTerm varchar(255) not null, 
                        webPage varchar(255) not null      
                    ); 
                    END;
            """)
        cursor.commit()
    finally:
        cursor.close()
        connection.close()


def drop_table():
    connection = get_connection()
    cursor = connection.cursor()
    print("Drop table")
    try:
        cursor.execute("DROP TABLE IF EXISTS MachineScoreEvents")
        cursor.commit()
    finally:
        cursor.close()
        connection.close()


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
        url = web_pages[0]['url']
        add_search_term_to_db(current_search, url)
        return render_template_string(template_string, current_search=current_search, search_link=url,
                                      search_terms=get_recent_search_terms())


@app.route("/")
def hello():
    return render_template_string(template_string, current_search="", search_terms=get_recent_search_terms())
    # return "Hello, World!"


create_table()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
