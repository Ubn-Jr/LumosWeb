from webob import Request
class Middleware:
    def __init__(self, app):
        self.app = app

    # Since middlewares are the first entrypoint to the app, they are now called by a web server
    # instead of the app itself. So, we need to add a __call__ method to the Middleware class.
    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = self.handle_request(req)
        return resp(environ, start_response)

    # we wrapped the given middleware class around the current app.
    def add(self, middleware_cls):
        self.app = middleware_cls(self.app)

    # we added a process_request and process_response method to the Middleware class.
    def process_request(self, req):
        pass

    def process_response(self, req, resp):
        pass

    # The method that handles incoming requests 
    def handle_request(self, req):
        self.process_request(req)
        resp = self.app.handle_request(req)
        self.process_response(req, resp)
        return resp