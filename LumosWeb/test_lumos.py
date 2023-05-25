import pytest

from api import API

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