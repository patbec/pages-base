import os
import sys
import json
import html
import pathlib

from dataclasses import dataclass
from http.server import *
from jsonschema import *
from jinja2 import *


DEBUG_ENABLED = int(os.environ.get('PAGES_DEBUG', "0"))
TEST_ENABLED = int(os.environ.get('PAGES_TEST', "0"))


#
# Console colors.
#
class Console:
    FAIL = '\033[0;1;31m'
    DEBUG = '\033[0;1;37m'
    ENDC = '\033[0m'


class Log():
    BUILD = 'Building'
    SERVER = 'Server'

    def message(message, section):
        print("[" + section + "] " + message)

    def error(message, section):
        print("[" + section + "] " + Console.FAIL + message + Console.ENDC)

    def debug(message, section):
        print("[" + section + "] " + Console.DEBUG + message + Console.ENDC)


#
# Returns a filtered dict of environment variables.
#
class UserEnvironmentVariables():

    #
    # Get environment variables from the container.
    #
    def get_environment_variables(prefix):
        environment_prefix = prefix
        environment_variables = {}

        if (environment_prefix == ''):
            Log.message(
                f"Load environment variables without filter.", Log.BUILD)
        else:
            Log.message(
                f"Load environment variables with the prefix '{environment_prefix}'.", Log.BUILD)

        for key, value in os.environ.items():
            if (key.startswith(environment_prefix)):
                environment_variables[key] = value

                if (DEBUG_ENABLED):
                    Log.debug("Read environment key " + key, Log.BUILD)

        return environment_variables


@ dataclass
class PageItem():
    path: str
    response: int
    content: bytes

    def __init__(self, path, response, content):
        self.path = path
        self.response = response
        self.content = content


#
# Extensions for Jinja2.
#
class Extensions():
    def escape(value):
        return html.escape(str(value))


#
# Generates static HTML pages from the config.json file and environment variables.
#
class App():
    config = {}
    schema = {
        "type": "object",
        "properties": {
            "default": {
                "type": "object",
                "properties": {
                    "variables": {
                        "type": "object"
                    },
                    "environment": {
                        "type": "boolean"
                    },
                    "environment_filter": {
                        "type": "string"
                    }
                },
                "required": [
                    "variables",
                    "environment",
                    "environment_filter"
                ]
            },
            "server": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string"
                                },
                                "response": {
                                    "type": "number"
                                }
                            },
                            "required": [
                                "path",
                                "response"
                            ]
                        },
                        "template_file": {
                            "type": "string"
                        },
                        "variables": {
                            "type": "object"
                        }
                    },
                    "required": [
                        "request",
                        "template_file",
                        "variables"
                    ]
                }
            }
        },
        "required": [
            "default",
            "server"
        ]
    }

    #
    # Loads the config.json file.
    #
    def load_config(self):
        config_file = os.environ.get('PAGES_CONFIG_FILE', 'config.json')

        Log.message(f"Load settings from '{config_file}'.", Log.BUILD)

        config = json.loads(
            pathlib.Path(config_file).read_text())

        # Checks the json schema of the config.json file.
        validate(instance=config, schema=self.schema)

        self.config = config

    #
    # Creates the static pages from the template.
    #
    def generate(self):
        config = self.config

        # Get user-defined environment variables.
        if (config['default']['environment']):
            environment_filter = config['default']['environment_filter']
            environment_variables = UserEnvironmentVariables.get_environment_variables(
                environment_filter)
        else:
            environment_variables = []

        # Create jinja2 environment and add extensions.
        environment = Environment(
            undefined=StrictUndefined,
            loader=FileSystemLoader(searchpath="./"))

        environment.filters['escape'] = Extensions.escape
        environment.globals['env'] = environment_variables

        Log.message(f"Generate HTML pages...", Log.BUILD)

        cache = []

        # Create list of html pages.
        for item in config['server']:
            Log.message(
                f"Template { item['template_file'] } for { item['request']['path'] }", Log.BUILD)

            # Merge specific page and global variables.
            variables = item['variables'] | config['default']['variables']

            # Load and creates an html from the template.
            template = environment.get_template(item['template_file'])
            content = bytes(template.render(variables), "utf-8")

            # Add item to cache.
            cache.append(
                PageItem(
                    item['request']['path'],
                    item['request']['response'],
                    content))

        Log.message(f"Build completed ({len(cache)} pages)", Log.BUILD)

        return cache


class Webserver():

    http_port = ""
    http_address = ""

    data = []

    #
    # Load config from environment.
    #
    def load_config(self):
        self.http_port = os.environ.get('PAGES_HTTP_PORT', "8090")
        self.http_address = os.environ.get('PAGES_HTTP_ADDRESS', "0.0.0.0")
        self.data = data

    #
    # Serve files from the cache.
    #
    def serve_forever(self):
        Log.message(
            f"Listen on {self.http_address}:{self.http_port}", Log.SERVER)

        socket = (self.http_address, int(self.http_port))

        handler = HTTPRequestHandler
        handler.data = self.data

        httpd = HTTPServer(socket, handler)
        httpd.serve_forever()


#
# Handling of page requests.
#
class HTTPRequestHandler(BaseHTTPRequestHandler):

    data = []

    def log_message(self, format, *args):
        Log.message(
            "Request " + str(args), Log.SERVER)

    def log_debug(self, item, count):
        Log.debug(
            f"Request '{ self.path }' matches filter '{ item.path }' at item {count}", Log.SERVER)

    def log_error(self, format, *args):
        Log.error(
            "Exception " + str(args), Log.SERVER)

    def do_POST(self):
        self.execute_request()

    def do_GET(self):
        self.execute_request()

    def execute_request(self):
        try:
            requested_page_found = self.try_send_response()

            # Return when the requested page was found and sent.
            if (requested_page_found):
                return

            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(
                b"Requested page is not available.")

        except Exception as error:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(
                b"Internal Server Error")

            self.log_error("", error)

    def try_send_response(self):
        count = 0

        for item in self.data:
            count += 1
            if (self.path.startswith(item.path)):
                if (DEBUG_ENABLED):
                    self.log_debug(item, count)

                self.send_response(item.response)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                self.wfile.write(item.content)

                # Requested page found
                return True

        # Requested page not found
        return False


#
# Generates static HTML pages from a template and environment variables.
#
try:
    if (DEBUG_ENABLED):
        Log.debug("Debug mode enabled", Log.BUILD)

    templates = App()

    templates.load_config()
    data = templates.generate()

except ValidationError as error:
    print("An exception occurred while validating config file:" + Console.FAIL, error)
    sys.exit(1)

except UndefinedError as error:
    print("An exception has occurred, a variable in the HTML template is not defined:" + Console.FAIL, error)
    sys.exit(1)

except Exception as error:
    print("An exception occurred:" + Console.FAIL, error)
    sys.exit(1)


if (TEST_ENABLED):
    Log.debug("Test successfully completed.", Log.BUILD)
    sys.exit(0)


#
# Serves the HTML pages via a web server.
#
try:
    webserver = Webserver()
    webserver.data = data
    webserver.load_config()
    webserver.serve_forever()

except Exception as error:
    print("An web exception occurred:" + Console.FAIL, error)
    sys.exit(1)

except KeyboardInterrupt:
    sys.exit(1)
