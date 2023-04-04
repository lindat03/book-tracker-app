
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "lt2899"
DATABASE_PASSWRD = "3463"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

# active user id
USER = 2


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
@app.route('/')
def index():
    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    #
    # example of a database query
    #
    select_query = "SELECT title from book"
    cursor = g.conn.execute(text(select_query))
    titles = []
    for result in cursor:
        titles.append(result[0])
    cursor.close()

    
    #
    context = dict(data=titles)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#


@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/collection')
def collection():

    return render_template("collection.html")




# search database by book title
@app.route('/search/title/<title>')
def title_search(title):

    ids = []

    select_query = "SELECT * FROM book"
    cursor = g.conn.execute(text(select_query))
    relevant = []
    for book in cursor:
        if title in book[1]:
            relevant.append(book[1])
            ids.append(book[0])
    cursor.close

    return render_template("search.html", titles=relevant, ids=ids)


# search database by author
@app.route('/search/author/<author>')
def author_search(author):

    select_query = "SELECT * FROM author"
    cursor = g.conn.execute(text(select_query))
    author_ids = []
    for person in cursor:
        if author in person[1]:
            author_ids.append(person[0])
    cursor.close

    cursor = g.conn.execute(text("SELECT * FROM book"))
    relevant = []
    ids = []
    for book in cursor:
        if book[2] in author_ids:
            relevant.append(book[1])
            ids.append(book[0])
    cursor.close

    return render_template("search.html", titles=relevant, ids=ids)

@app.route('/book/<title>')
def book_page(title):
    select_query = "SELECT * FROM book WHERE title='" + title + "'"
    cursor = g.conn.execute(text(select_query))
    book = []
    for c in cursor:
        book.append(c)
    cursor.close
    title = book[0][1]
    author_id = book[0][2]
    description = book[0][3]
    date = book[0][4]

    cursor = g.conn.execute(text("SELECT name FROM author WHERE author_id=" + str(author_id)))
    list = []
    for c in cursor:
        list.append(c)
    cursor.close
    author = list[0][0]
    return render_template("book.html", title=title, author=author, description=description, date=date)



@app.route('/user')
def user():

    select_query = "SELECT name from collection WHERE user_id=" + str(USER)
    cursor = g.conn.execute(text(select_query))
    collectionnames = []
    for result in cursor:
        collectionnames.append(result[0])
    cursor.close()

    usercontext = dict(collectiondata=collectionnames)
    return render_template("user.html", **usercontext)


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

                python server.py

        Show the help text using:

                python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
