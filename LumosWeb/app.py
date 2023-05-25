from api import API

app = API()

@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route("/lumos")
def about(request, response):
    response.text = "Lights are on!"

@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"What are you doing here, {name}"

@app.route("/book/{title}/page/{page:d}")
def book(request, response, title, page):
    response.text = f"You are reading the Book: {title}, and you were on Page: {page}"

@app.route("/sum/{num_1:d}/{num_2:d}")
def sum(request, response, num_1, num_2):
    total = int(num_1) + int(num_2)
    response.text = f"{num_1} + {num_2} = {total}"

@app.route("/book")
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"

    def post(self, req, resp):
        resp.text = "Endpoint to create a book"