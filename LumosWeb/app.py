from api import API
from middleware import Middleware

app = API()

@app.route("/home")
def home(request, response):
    if request.method == "get":
        response.text = "Hello from the HOME page"
    else:
        raise AttributeError("Method not allowed.")

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

@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template("index.html", context={"name": "LumosWeb", "title":"Lights are on!"}).encode()

## Adding a route without a decorator
def handler(req, resp):
    resp.text = "We don't have to use decorators!"

app.add_route("/sample", handler)

# To handle exceptions
def custom_exception_handler(request, response, exception_cls):
    response.body = app.template("error.html", context={"name": exception_cls, "title":"Lights cannot be turned on!"}).encode()


app.add_exception_handler(custom_exception_handler)

@app.route("/exception")
def exception_throwing_handler(request, response):
    raise AssertionError("Sorry, This handler should not be used")

# custom middleware
class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Processing request", req.url)

    def process_response(self, req, resp):
        print("Processing response", req.url)

app.add_middleware(SimpleCustomMiddleware)