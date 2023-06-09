import socket
import pytest

from LumosWeb.api import API
from LumosWeb.middleware import Middleware

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
    @api.route("/home", allowed_methods=["get", "post"])
    def home(req, resp):
        resp.text = "Lumos is on!"
    with pytest.raises(AssertionError):
        @api.route("/home", allowed_methods=["get", "post"])
        def home2(req, resp):
            resp.text = "Lumos is off!"

def test_lumos_test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "Yes it can :)!"

    @api.route("/lumos", allowed_methods=["get", "post"])
    def lumos(req, resp):
        resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/lumos").text == RESPONSE_TEXT

def test_parametrized_route(api, client):
    @api.route("/{name}", allowed_methods=["get"])
    def hello(req, resp, name):
        resp.text = f"Hey {name}"

    assert client.get("http://testserver/sdd").text == "Hey sdd"
    assert client.get("http://testserver/123").text == "Hey 123"

def test_params_are_passed_correctly(api, client):
    @api.route("/sum/{num_1:d}/{num_2:d}", allowed_methods=["get", "post"])
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

    @api.route("/book", allowed_methods=["get", "post"])
    class BookResource:
        def get(self, req, resp):
            resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/book").text == RESPONSE_TEXT

def test_class_based_handler_post(api, client):
    RESPONSE_TEXT = "This is a POST request"

    @api.route("/book", allowed_methods=["get", "post"])
    class BookResource:
        def post(self, req, resp):
            resp.text = RESPONSE_TEXT

    assert client.post("http://testserver/book").text == RESPONSE_TEXT

def test_class_based_handler_not_allowed_method(api, client):
    @api.route("/book", allowed_methods=["get", "post"])
    class BookResource:
        def post(self, req, resp):
            resp.text = "Lumos!"

    with pytest.raises(AttributeError):
        client.get("http://testserver/book")

def test_alternative_route(api, client):
    RESPONSE_TEXT = "Alternative way to add a route"

    def home(req, resp):
        resp.text = RESPONSE_TEXT

    api.add_route("/alternative", home, allowed_methods=["get", "post"])

    assert client.get("http://testserver/alternative").text == RESPONSE_TEXT

def test_template(api, client):
    @api.route("/html", allowed_methods=["get", "post"])
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

    @api.route("/", allowed_methods=["get"])
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

    @api.route("/", allowed_methods=["get"])
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

def test_json_response_helper(api, client):
    @api.route("/json", allowed_methods=["get", "post"])
    def json_handler(req, resp):
        resp.json = {"name": "Lumos"}

    response = client.get("http://testserver/json")
    json_body = response.json()
    assert response.headers["Content-Type"] == "application/json"
    assert json_body["name"] == "Lumos"

def test_html_response_helper(api, client):
    @api.route("/html", allowed_methods=["get", "post"])
    def html_handler(req, resp):
        resp.html = api.template(
            "index.html", context={"title": "Some Title", "name": "Some Name"}
        )

    response = client.get("http://testserver/html")
    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text

def test_text_response_helper(api, client):
    response_text = "Plain text response from LumosWeb"

    @api.route("/text", allowed_methods=["get", "post"])
    def text_handler(req, resp):
        resp.text = response_text

    response = client.get("http://testserver/text")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == response_text

def test_manually_setting_body(api, client):
    @api.route("/body", allowed_methods=["get", "post"])
    def text_handler(req, resp):
        resp.body = b"Byte body"
        resp.content_type = "text/plain"

    response = client.get("http://testserver/body")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "Byte body"

def test_run_success(api):
    host = "localhost"
    port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))

        try:
            api.run(host=host, port=port, timeout=1)  # Set a short timeout for testing purposes
            assert api.is_running()
        finally:
            sock.close()

def test_run_alternative_port(api):
    host = "localhost"
    port = 8080

    # Create a socket and bind it to port 8080 to simulate a busy port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))

        try:
            api.run(host=host, port=port, timeout=1)  # Set a short timeout for testing purposes
            assert api.is_running()  # Check if the API is running (on another port, api.run changes the port if default port is not available) even though the default port is busy
        except Exception as exc:
            assert str(exc) == "No ports available to run the API"
        finally:
            sock.close()

def test_run_exception_other_error(api):
    host = "localhost"
    port = 8080

    try:
        with pytest.raises(Exception):
            # Simulate a different exception by passing an invalid value for `host`
            api.run(host=None, port=port, timeout=1)  # Set a short timeout for testing purposes
    finally:
        assert not api.is_running()

