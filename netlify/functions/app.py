import sys
import os
from werkzeug.wsgi import get_current_url

# Add the project root to the sys.path so that your Flask app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_app import app

def lambda_handler(event, context):
    """
    A WSGI handler for Netlify's serverless function environment.
    """
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    body = event.get('body', '')
    headers = event.get('headers', {})
    
    # Simple WSGI environment creation
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'SERVER_NAME': headers.get('Host', 'localhost'),
        'SERVER_PORT': '443', # Netlify functions are always on HTTPS
        'SCRIPT_NAME': '',
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'HTTP_HOST': headers.get('Host', 'localhost'),
        'REMOTE_ADDR': '127.0.0.1', # Placeholder
        'CONTENT_TYPE': headers.get('Content-Type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'wsgi.url_scheme': 'https',
        'wsgi.input': sys.stdin,
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.input': body.encode('utf-8') if body else None,
        # ... and other necessary headers
    }
    
    # We need to capture the output of the Flask app
    response_headers = []
    
    def start_response(status, headers, exc_info=None):
        response_headers.extend(headers)
        return []
    
    # Call the Flask app
    response_body = app(environ, start_response)
    
    # Process the response from Flask
    status_code = int(response_headers[0][1].split(' ')[0])
    headers = {h[0]: h[1] for h in response_headers}

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': "".join(response_body).decode('utf-8')
    }

# This is the entry point that Netlify will use
def handler(event, context):
    return lambda_handler(event, context)
