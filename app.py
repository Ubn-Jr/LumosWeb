from LumosWeb.api import API
from LumosWeb.middleware import Middleware

app = API()

@app.route("/home", allowed_methods=["get"])
def home(request, response):
    if request.method == "get" or "GET": ### This is a bug, as we are not checking for the request method TODO: Fix this
        response.text = "Hello from the HOME page"
    else:
        raise AttributeError("Method not allowed.",request.method)

@app.route("/lumos", allowed_methods=["get", "post"])
def about(request, response):
    response.text = "Lights are on!"

@app.route("/hello/{name}", allowed_methods=["get", "post"])
def greeting(request, response, name):
    response.text = f"What are you doing here, {name}"

@app.route("/book/{title}/page/{page:d}", allowed_methods=["get", "post"])
def book(request, response, title, page):
    response.text = f"You are reading the Book: {title}, and you were on Page: {page}"

@app.route("/sum/{num_1:d}/{num_2:d}", allowed_methods=["get", "post"])
def sum(request, response, num_1, num_2):
    total = int(num_1) + int(num_2)
    response.text = f"{num_1} + {num_2} = {total}"

@app.route("/book", allowed_methods=["get", "post"])
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"

    def post(self, req, resp):
        resp.text = "Endpoint to create a book"

# @app.route("/template")
# def template_handler(req, resp):
#     resp.body = app.template("index.html", context={"name": "LumosWeb", "title":"Lights are on!"}).encode()  # Now we dont need to encode the body, as we are doing it in the Response class

## Adding a route without a decorator
def handler(req, resp):
    resp.text = "We don't have to use decorators!"

app.add_route("/sample", handler, allowed_methods=["get", "post"])

# To handle exceptions
def custom_exception_handler(request, response, exception_cls):
    response.body = app.template("error.html", context={"name": exception_cls, "title":"Lights cannot be turned on!"}).encode()


app.add_exception_handler(custom_exception_handler)

@app.route("/exception", allowed_methods=["get", "post"])
def exception_throwing_handler(request, response):
    raise AssertionError("Sorry, This handler should not be used")

# custom middleware
class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Processing request", req.url)

    def process_response(self, req, resp):
        print("Processing response", req.url)

app.add_middleware(SimpleCustomMiddleware)

@app.route("/template", allowed_methods=["get", "post"])
def template_handler(req, resp):
    resp.html = app.template("index.html", context={"name": "LumosWeb", "title":"Lights are on!"})

@app.route("/json", allowed_methods=["get", "post"])
def json_handler(req, resp):
    resp.json = {"name": "LumosData", "type":"JSON"}

@app.route("/text", allowed_methods=["get", "post"])
def text_handler(req, resp):
    resp.text = "This is a plain text"

app.run()