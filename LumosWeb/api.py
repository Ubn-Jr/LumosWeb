import socket
from webob import Request
from parse import parse
import inspect
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from wsgiref.simple_server import make_server
import os
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise
from .middleware import Middleware
from .response import Response

class API:
    def __init__(self, templates_dir="templates", static_dir="static"):
        self.routes = {}  # dictionary of routes and handlers, path as keys and handlers as values

        self.templates_env = Environment(
            loader = FileSystemLoader(os.path.abspath(templates_dir))
        )

        self.exception_handler = None

        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

        self.middleware = Middleware(self)    

    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]

        if path_info.startswith("/static"):
            environ["PATH_INFO"] = path_info[len("/static"):]
            return self.whitenoise(environ, start_response)
        
        return self.middleware(environ, start_response)
    
    def wsgi_app(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)
    
    def add_route(self, path, handler, allowed_methods=None):
        assert path not in self.routes, "You have already used this route, please choose another route :)"
      
        self.routes[path] = {"handler":handler, "allowed_methods": allowed_methods}  # path as an argument.
            
    def route(self, path, allowed_methods=None):
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods) 
            return handler
        return wrapper
        
    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found. :("

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)

            if parse_result is not None:
                return handler, parse_result.named
        return None, None
    
    def handle_request(self, request):
        response = Response()

        handler_data, kwargs = self.find_handler(request_path=request.path)
        try:
            if handler_data is not None:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                if inspect.isclass(handler):  # To check if the handler is a class
                    handler = getattr(handler(), request.method.lower(), None)  # To get the method of the class, if handler() doesn't has the method attribute,getattr() returns None
                    if handler is None:
                        raise AttributeError("Method not allowed", request.method)
                else:
                    if request.method.lower() not in allowed_methods:
                        raise AttributeError("Method not allowed", request.method)
                handler(request, response, **kwargs)  # **kwargs is used to unpack the dictionary
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response
    
    # To create a test client for the API
    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session
    
    def template(self, template_name, context=None):
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context)
    
    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)
        
    def run(self, host="localhost", port=8080):
        while True:
            try:
                server = make_server(host, port, self)
                break  # Exit the loop if the server is created successfully
            except OSError as e:
                if e.errno == socket.errno.EADDRINUSE:
                    # Port is already in use, try another port
                    port += 1
                    print(f"Port {port-1} is not available, trying port {port}")
                else:
                    # Other error occurred, raise the exception
                    raise

        actual_port = server.server_port
        print(f"Starting Lumos server on {host}:{actual_port}")
        server.serve_forever()

