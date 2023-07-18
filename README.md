# Pages container-base

In this project, static HTML pages can be created from a Jinja2 template. Predefined values from a configuration file or user-defined environment variables can be used in this template.

When pages have been created, they are made available via a built-in web server.

## Configuration

A `config.json` file is used to define the web pages and routes, [see here for examples](#examples). This project is a template and does not contain this file, [see here for a complete project](https://github.com/patbec/traefik-error-pages).

These environment variables can be overridden in the `Dockerfile` or `docker-compose.yml` file:

| Setting              | Description                                  | Default Value |
| -------------------- | -------------------------------------------- | ------------- |
| `PAGES_CONFIG_FILE`  | Path to the configuration file.              | `config.json` |
| `PAGES_HTTP_PORT`    | The web pages are served under this port.    | `8090`        |
| `PAGES_HTTP_ADDRESS` | The web pages are served under this address. | `0.0.0.0`     |
| `PAGES_DEBUG`        | Enables the debug mode.                      | `0`           |
| `PAGES_TEST`         | Enables the config test mode.                | `0`           |

> The built-in web server should not be publicly accessible. Use a reverse proxy to access the content.

## Extensions

Variables can be inserted into the template using the Jinja2 syntax `{{ sample }}`, there are built-in extensions to perform additional actions.

| Action      | Example                                                | Description                                                             |
| ----------- | ------------------------------------------------------ | ----------------------------------------------------------------------- |
| `escape`    | `<p>{{ sample \| escape }}</p>`                        | Convert an email address or words with special characters to html text. |
| `urlencode` | `<a href="mailto:{{ sample \| urlencode }}">Click</a>` | Convert an email address to a encoded url.                              |

> It is recommended to use the **escape** action, especially for custom environment variables - otherwise text encoding may be broken or script tags can be inserted into the template.

## Development

To test your template the application can be started locally, create a file named `config.json` and `index.html` in the `data` folder. Examples are included in the next section.

```shell
export PAGES_CONFIG_FILE="config.json"
export PAGES_HTTP_PORT="8090"
export PAGES_HTTP_ADDRESS="localhost"
export PAGES_DEBUG="1"

cd data
python3 run.py
```

<details>
<summary>Sample output</summary>

```
[Building] Debug mode enabled
[Building] Load settings from 'config.json'.
[Building] Load environment variables with the prefix 'PROXY_'.
[Building] Read environment key PROXY_SUPPORT_MESSAGE
[Building] Read environment key PROXY_NAME
[Building] Read environment key PROXY_LOCATION
[Building] Read environment key PROXY_SUPPORT_MAIL
[Building] Generate HTML pages...
[Building] Template index.html for /400.html
[Building] Template index.html for /401.html
[Building] Template index.html for /403.html
[Building] Template index.html for /404.html
[Building] Template index.html for /405.html
[Building] Template index.html for /406.html
[Building] Template index.html for /407.html
[Building] Template index.html for /408.html
[Building] Template index.html for /409.html
[Building] Template index.html for /410.html
[Building] Template index.html for /411.html
[Building] Template index.html for /412.html
[Building] Template index.html for /413.html
[Building] Template index.html for /414.html
[Building] Template index.html for /415.html
[Building] Template index.html for /416.html
[Building] Template index.html for /417.html
[Building] Template index.html for /418.html
[Building] Template index.html for /421.html
[Building] Template index.html for /422.html
[Building] Template index.html for /423.html
[Building] Template index.html for /424.html
[Building] Template index.html for /425.html
[Building] Template index.html for /426.html
[Building] Template index.html for /428.html
[Building] Template index.html for /429.html
[Building] Template index.html for /431.html
[Building] Template index.html for /451.html
[Building] Template index.html for /500.html
[Building] Template index.html for /501.html
[Building] Template index.html for /502.html
[Building] Template index.html for /503.html
[Building] Template index.html for /504.html
[Building] Template index.html for /505.html
[Building] Template index.html for /506.html
[Building] Template index.html for /507.html
[Building] Template index.html for /508.html
[Building] Template index.html for /510.html
[Building] Template index.html for /511.html
[Building] Template index.html for /
[Building] Build completed (40 pages)
[Server] Listen on localhost:8090
[Server] Request '/' matches filter '/' at item 40
[Server] Request ('GET / HTTP/1.1', '404', '-')
```
</details>

## Examples

Here are a few examples of how this container can be used.

  1. [Basic](#basic)<br>Sample page with a custom response code.
  2. [Predefined variables](#predefined-variables)<br>Pages with specific and global variables.
  3. [Environment variables](#environment-variables)<br>Pages with user-defined environment variables.
  4. [Requests path](#requests-path)<br>Catch all http requests.

### Basic

This basic example returns a page under the path `/sample.html` with response code `200`.

<details>
<summary>Show example</summary>

#### File config.json:
```json
{
  "default": {
    "variables": {},
    "environment": false,
    "environment_filter": ""
  },
  "server": [
    {
      "request": {
        "path": "/sample.html",
        "response": 200
      },
      "template_file": "index.html",
      "variables": {}
    }
  ]
}
```

#### File index.html:
```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <title>Sample Page</title>
    <meta name="robots" content="nofollow">
</head>

<body>
    <p>Hello World</p>
</body>

</html>
```

#### File Dockerfile:
```dockerfile
FROM ghcr.io/patbec/pages-base:latest

ADD ./config.json /data/config.json
ADD ./index.html /data/index.html
```

After launching the Docker container, the website is now available under:
- http://localhost:8090/sample.html

</details>

---

### Predefined variables

In this example **page specific** and **global variables** are used in the HTML template.

<details>
<summary>Show example</summary>

#### File config.json:
```json
{
  "default": {
    "variables": {
      "my_global_variable": "Hello World!"
    },
    "environment": false,
    "environment_filter": ""
  },
  "server": [
    {
      "request": {
        "path": "/sample-01.html",
        "response": 200
      },
      "template_file": "index.html",
      "variables": {
        "my_page_variable": "This is sample 01."
      }
    },
    {
      "request": {
        "path": "/sample-02.html",
        "response": 200
      },
      "template_file": "index.html",
      "variables": {
        "my_page_variable": "This is sample 02."
      }
    }
  ]
}
```

#### File index.html:
```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <title>Sample Page</title>
    <meta name="robots" content="nofollow">
</head>

<body>
    <p>{{ my_global_variable }}</p>
    <p>{{ my_page_variable }}</p>
</body>

</html>
```

#### File Dockerfile:
```dockerfile
FROM ghcr.io/patbec/pages-base:latest

ADD ./config.json /data/config.json
ADD ./index.html /data/index.html
```

After launching the Docker container, the two website are now accessible under:
- http://localhost:8090/sample-01.html
- http://localhost:8090/sample-02.html

</details>

---

### Environment variables

In this example, **user-defined environment variables** are used in the HTML template.

<details>
<summary>Show example</summary>

#### File config.json:
```json
{
  "default": {
    "variables": {},
    "environment": true,
    "environment_filter": "SAMPLE_"
  },
  "server": [
    {
      "request": {
        "path": "/sample-01.html",
        "response": 200
      },
      "template_file": "index.html",
      "variables": {}
    },
    {
      "request": {
        "path": "/sample-02.html",
        "response": 200
      },
      "template_file": "index.html",
      "variables": {}
    }
  ]
}
```

The `environment_filter` property in the `config.json` file is used to filter the set environment variables, with this only intended variables can be used in the template.

If the `environment_filter` property contains an **empty string**, all host environment variables are available. With the `env` command all set variables can be displayed.

#### File index.html:
```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <title>Sample Page</title>
    <meta name="robots" content="nofollow">
</head>

<body>
    <p>{{ env["SAMPLE_VAR"] }}</p>
</body>

</html>
```

The env property is a dictionary and contains the loaded variables. [See here](#extensions) how to escape values with the `escape` filter.

#### File Dockerfile:
```dockerfile
FROM ghcr.io/patbec/pages-base:latest

ENV SAMPLE_VAR="Hello World from Dockerfile"

ADD ./config.json /data/config.json
ADD ./index.html /data/index.html
```

This envirmoment function is intended to allow values to be changed later in a `docker-compose.yml` without rebuilding the container. e.g. the template contains an email address variable that is different for each host.

After launching the Docker container, the two website are now accessible under:
- http://localhost:8090/sample-01.html
- http://localhost:8090/sample-02.html

</details>

---

### Requests path

In this example, all HTTP requests are answered with a default page.

<details>
<summary>Show example</summary>

#### File config.json:
```json
{
  "default": {
    "variables": {},
    "environment": false,
    "environment_filter": ""
  },
  "server": [
    {
      "request": {
        "path": "/sample-01.html",
        "response": 200
      },
      "template_file": "index.html",
      "variables": {}
    },
    {
      "request": {
        "path": "/",
        "response": 200
      },
      "template_file": "index.html",
      "variables": {}
    }
  ]
}
```

The `path` property always checks if an incoming request starts with this string. A single `/` is equivalent to a wildcard filter.

#### File index.html:
```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <title>Sample Page</title>
    <meta name="robots" content="nofollow">
</head>

<body>
    <p>Hello World</p>
</body>

</html>
```

#### File Dockerfile:
```dockerfile
FROM ghcr.io/patbec/pages-base:latest

ADD ./config.json /data/config.json
ADD ./index.html /data/index.html
```

After launching the Docker container, the three website are now accessible under:
- http://localhost:8090/sample-01.html
- http://localhost:8090/sample-02.html
- http://localhost:8090/sample-03.html

</details>

---

## Licence

This project is licensed under MIT - See the [LICENSE](LICENSE) file for more information.

---

&uarr; [Back to top](#)
