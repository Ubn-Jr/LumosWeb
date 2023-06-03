## LumosWeb ![PyPI](https://img.shields.io/pypi/v/LumosWeb.svg)

- To ensure compatibility and access the latest features and improvements, it is highly recommended to use version 1.0.0 or higher of the package. 
- LumosWeb is web framework written in python
- It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.
- [PyPI Release](https://pypi.org/project/LumosWeb/)
- [Sample App](https://github.com/Sddilora/LumosWeb-SampleApp)



## Installation
```shell
pip install LumosWeb==<latest_version>
e.g. pip install LumosWeb==0.0.2
```

## Getting Started

### Basic usage

### Define App

```python
from LumosWeb.api import API()
app = API()  # We created our api instance
```

```python
@app.route("/home", allowed_methods=["get", "post", "put", "delete"])
def home(request, response):
    if request.method == "get":
        response.text = "Hello from the HOME page"
    else:
        raise AttributeError("Method not allowed.")

# Parameterized routes
@app.route("/book/{title}/page/{page:d}", allowed_methods=["get", "post"])
def book(request, response, title, page):
    response.text = f"You are reading the Book: {title}, and you were on Page: {page}"

## Adding a route without a decorator
def handler(req, resp):
    resp.text = "We don't have to use decorators!"

app.add_route("/sample", handler, allowed_methods=["get", "post"])


```
### Run Server
> Lumosweb --app <module_name> run

### Unit Test

The recommended way of writing unit tests is with [pytest](https://docs.pytest.org/en/latest/). There are two built in fixtures
that you may want to use when writing unit tests with LumosWeb. The first one is `app` which is an instance of the main `API` class:
```python
def test_basic_route_adding(api):
    @api.route("/home", allowed_methods=["get", "post"])
    def home(req, resp):
        resp.text = "Lumos is on!"
    with pytest.raises(AssertionError):
        @api.route("/home", allowed_methods=["get", "post"])
        def home2(req, resp):
            resp.text = "Lumos is off!"
```
The other one is `client` that you can use to send HTTP requests to your handlers. It is based on the famous [requests](https://requests.readthedocs.io/) and it should feel very familiar:
```python
def test_lumos_test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "Yes it can :)!"

    @api.route("/lumos", allowed_methods=["get", "post"])
    def lumos(req, resp):
        resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/lumos").text == RESPONSE_TEXT

```

## Templates
The default folder for templates is `templates`. You can change it when initializing the main `API()` class:
```python
app = API(templates_dir="templates_dir_name")
```
Then you can use HTML files in that folder like so in a handler:

```python
@app.route("/show/template")
def handler_with_template(req, resp):
    resp.html = app.template(
        "example.html", context={"title": "Awesome Framework", "body": "welcome to the future!"})
```

## Static Files

Just like templates, the default folder for static files is `static` and you can override it:
```python
app = API(static_dir="static_dir_name")
```
Then you can use the files inside this folder in HTML files:
```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>{{title}}</title>

  <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>

<body>
    <h1>{{body}}</h1>
    <p>This is a paragraph</p>
</body>
</html>
 ```

 ### Middleware
You can create custom middleware classes by inheriting from the `LumosWeb.middleware.Middleware` class and overriding its two methods
that are called before and after each request:

```python
from LumosWeb.api import API
from LumosWeb.middleware import Middleware

app = API()

class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Before dispatch", req.url)

    def process_response(self, req, res):
        print("After dispatch", req.url)


app.add_middleware(SimpleCustomMiddleware)
```