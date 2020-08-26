# Localhero

Localhero is a small GUI-application that helps you manage local server instances from your flask and vue-cli apps.

The project is currently in beta status and tested on OSX.

## Features

* Start, stop and monitor local server instances in one place
* Automatically activate corresponding virtual envs
* Expandable via plugin system
* Easy configuration via YAML file

## Example configuration

``` yaml
servers:

  MyApp API (Dev):
    type: flask
    env:
      FLASK_APP: server.py
    dir: /projects/flask_app
    venv: $dir/.venv

  MyApp Frontend (Dev):
    type: vue-cli
    dir: /projects/my_vue_app
```

## Changes

### 0.1.0b1

* First beta version