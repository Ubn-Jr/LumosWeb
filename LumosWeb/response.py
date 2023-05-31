import json
from webob import Response as WebObResponse

class Response:
    def __init__(self):
        self.text = None
        self.json = None
        self.html = None
        self.status_code = 200
        self.body = b''
        self.content_type = None
    
    def __call__(self, environ, start_response):
        self.set_body_and_content_type()
        
        response = WebObResponse(
            body = self.body, content_type=self.content_type, status=self.status_code
        )
        return response(environ, start_response)
    
    def set_body_and_content_type(self):
        if self.json is not None:
            self.body = json.dumps(self.json).encode("utf-8")
            self.content_type = "application/json"

        if self.text is not None:
            self.body = self.text
            self.content_type = "text/plain"

        if self.html is not None:
            self.body = self.html.encode()
            self.content_type = "text/html"
    