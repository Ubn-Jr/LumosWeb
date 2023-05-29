import pytest

from api import API
from middleware import Middleware

FILE_DIR ="css"
FILE_NAME = "main.css"
FILE_CONTENTS = "body {background-color: #d0e4fe}"


# helpers
# A helper method is created that creates a static file under the given folder.
def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)

    return asset

# tests

def test_basic_route_adding(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "Lumos is on!"
    with pytest.raises(AssertionError):
        @api.route("/home")
        def home2(req, resp):
            resp.text = "Lumos is off!"

def test_lumos_test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "Yes it can :)!"

    @api.route("/lumos")
    def lumos(req, resp):
        resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/lumos").text == RESPONSE_TEXT

def test_parametrized_route(api, client):
    @api.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"Hey {name}"

    assert client.get("http://testserver/sdd").text == "Hey sdd"
    assert client.get("http://testserver/123").text == "Hey 123"

def test_params_are_passed_correctly(api, client):
    @api.route("/sum/{num_1:d}/{num_2:d}")
    def sum(req, resp, num_1, num_2):
        resp.text = f"{num_1} + {num_2} = {num_1 + num_2}"

    assert client.get("http://testserver/sum/12/13").text == "12 + 13 = 25"
    assert client.get("http://testserver/sum/12/13/14").status_code == 404
    assert client.get("http://testserver/sum/12/hello").status_code == 404

def test_default_404_response(client):
    response = client.get("http://testserver/doesnotexist")
    assert response.status_code == 404
    assert response.text == "Not found. :("

def test_class_based_handler_get(api, client):
    RESPONSE_TEXT = "This is a GET request"

    @api.route("/book")
    class BookResource:
        def get(self, req, resp):
            resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/book").text == RESPONSE_TEXT

def test_class_based_handler_post(api, client):
    RESPONSE_TEXT = "This is a POST request"

    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = RESPONSE_TEXT

    assert client.post("http://testserver/book").text == RESPONSE_TEXT

def test_class_based_handler_not_allowed_method(api, client):
    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = "Lumos!"

    with pytest.raises(AttributeError):
        client.get("http://testserver/book")

def test_alternative_route(api, client):
    RESPONSE_TEXT = "Alternative way to add a route"

    def home(req, resp):
        resp.text = RESPONSE_TEXT

    api.add_route("/alternative", home)

    assert client.get("http://testserver/alternative").text == RESPONSE_TEXT

def test_template(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.body = api.template(
            "index.html", context={"title": "Some Title", "name": "Some Name"}
        ).encode()

    response = client.get("http://testserver/html")
    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text

def test_custom_exception_handler(api, client):
    def on_exception(req, resp, exc):
        resp.text = "AttributeErrorHappened"

    api.add_exception_handler(on_exception)

    @api.route("/")
    def index(req, resp):
        raise AttributeError()

    response = client.get("http://testserver/")
    assert response.text == "AttributeErrorHappened"

# This one tests if a 404 (Not Found) response is returned if a request is sent for a nonexistent static file.
def test_404_is_returned_for_nonexistent_static_file(client):
    assert client.get(f"http://testserver/static/main.css)").status_code == 404

def test_assets_are_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_static(static_dir)

    api = API(static_dir=str(static_dir))
    client = api.test_session()

    response = client.get(f"http://testserver/static/{FILE_DIR}/{FILE_NAME}")
    assert response.status_code == 200
    assert response.text == FILE_CONTENTS

def test_middleware_methods_are_called(api, client):
    process_request_called = False
    process_response_called = False

    class CalledMiddleware(Middleware):
        def __init__(self, app):
            super().__init__(app)

        def process_request(self, req):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, req, resp):
            nonlocal process_response_called
            process_response_called = True

    api.add_middleware(CalledMiddleware)

    @api.route("/")
    def index(req, resp):
        resp.text = "Hello Middleware!"

    client.get("http://testserver/")

    assert process_request_called is True
    assert process_response_called is True

def test_allowed_methods_for_function_based_handlers(api, client):
    @api.route("/home", allowed_methods=["post"])
    def home(req, resp):
        resp.text = "Hello"

    with pytest.raises(AttributeError):
        client.get("http://testserver/home")

    assert client.post("http://testserver/home").text == "Hello"

def test_allowed_methods_not_specified(api, client):
    @api.route("/home")
    def home(req, resp):
        resp.text = "Hello"

    assert client.get("http://testserver/home").text == "Hello"
    assert client.put("http://testserver/home").text == "Hello"