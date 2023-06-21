# Pages container-base

In this project, static HTML pages can be created from a Jinja2 template. Predefined values from a configuration file or user-defined environment variables can be used in this template.

When pages have been created, they are made available via a built-in web server.

## Configuration

A `config.json` file is used to define the web pages and routes, [see here for examples](#examples). This project is a template and does not contain this file, [see here for a complete project](https://github.com/patbec/traefik-error-pages).

These environment variables can be overridden in the `Dockerfile` or `docker-compose.yml` file:


| Setting            | Description                                  | Default Value |
| ------------------ | -------------------------------------------- | ------------- |
| `APP_CONFIG_FILE`  | Path to the configuration file.              | `config.json` |
| `APP_HTTP_PORT`    | The web pages are served under this port.    | `8090`        |
| `APP_HTTP_ADDRESS` | The web pages are served under this address. | `0.0.0.0`     |


> The built-in web server should not be publicly accessible. Use a reverse proxy to access the content.

## Examples

Here are a few examples of how this container can be used.

  1. [Basic](#basic)<br>Sample page with a custom response code.
  2. [Predefined variables](#predefined-variables)<br>Pages with **specific** and **global variables**.
  3. [Environment variables](#environment-variables)<br>Pages with user-defined **environment variables**.

### Basic

This basic example returns a page under the path `/sample.html` with response code `200`.

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
FROM <pages-base>

ADD ./config.json /data/config.json
ADD ./index.html /data/index.html
```

After launching the Docker container, the website is now available under:
- http://localhost:8090/sample.html

### Predefined variables

In this example **page specific** and **global variables** are used in the HTML template.

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
FROM <pages-base>

ADD ./config.json /data/config.json
ADD ./index.html /data/index.html
```

After launching the Docker container, the two website are now accessible under:
- http://localhost:8090/sample-01.html
- http://localhost:8090/sample-02.html

### Environment variables

In this example, user-defined **environment variables** are used in the HTML template.

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

The env property is a dictionary and contains the loaded variables. [See here](#escape-html) how to escape values with the `escape` filter.


#### File Dockerfile:
```dockerfile
FROM <pages-base>

ENV SAMPLE_VAR="Hello World from Dockerfile"

ADD ./config.json /data/config.json
ADD ./index.html /data/index.html
```

This envirmoment function is intended to allow values to be changed later in a `docker-compose.yml` without rebuilding the container. e.g. the template contains an email address variable that is different for each host.

After launching the Docker container, the two website are now accessible under:
- http://localhost:8090/sample-01.html
- http://localhost:8090/sample-02.html

## Extensions

Variables can be inserted with the Jinja2 syntax `{{ sample }}`, there are built-in extensions to perform additional actions.

### Escape

Convert an email address or words with special characters to html text.

```
<p>{{ sample | escape }}</p>
```

> It is recommended to use this option, especially with user-defined environment variables - otherwise script tags can be inserted in the template.

### Urlencode

Converted a mail address to a valid url.

```
<a href="mailto:{{ sample | urlencode }}">Click here to send a mail to {{ sample | escape }}</a>
```

## Licence

This project is licensed under MIT - See the [LICENSE](LICENSE) file for more information.

---

&uarr; [Back to top](#)