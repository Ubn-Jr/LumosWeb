from webob import Request, Response
from parse import parse

class API:
    def __init__(self):
        self.routes = {}  # dictionary of routes and handlers, path as keys and handlers as values

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)
    
    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler  # path as an argument.
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

        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            handler(request, response, **kwargs)  # **kwargs is used to unpack the dictionary
        else:
            self.default_response(response)

        return response
    