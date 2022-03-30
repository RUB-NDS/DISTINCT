# DISTINCT

Dynamic In-Browser Single Sign-On Tracer Inspecting Novel Communication Techniques

DISTINCT is an analysis framework for modern communication techniques that was developed for the paper "DISTINCT: Identity Theft using Cross-Window Communications in Modern Single Sign-On".

## Quick Start with Gitpod

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/iphoneintosh/DISTINCT)

## Setup

Setup was tested on `Ubuntu 20.04.3 LTS`

- Download and install [Docker](https://docs.docker.com/get-docker/)
- Clone this repository and go into its `src` directory: `cd ./src`
- Run: `docker-compose build`
- Run: `docker-compose up`
  - Check that ports `8080` and `9090` are not allocated on your system
- Open `http://localhost:8080` in your webbrowser
- Press `Ctrl+C` and run `docker-compose down` to close and exit the tool

## Workflow

> TODO: Outdated, change to v2

- [OPTIONAL] Generate cookies that should be preloaded into the browser, i.e., for Google and Facebook sessions
  - Go into the repository's `tools` directory
  - Run `python3 cookiegen.py --output /tmp/cookiejar.json`
  - Sign in to Google, and once completed, hit ENTER
  - Sign in to Facebook, and once completed, hit ENTER
  - You can use the `--cookie-file /tmp/cookiejar.json` in the next step to preload the cookies into the browser
- Go into the repository's `src` directory
- Start DISTINCT: `python3 main.py --url "https://pocs.work/tests/postmessage" --out /tmp`
  - `--url` (mandatory) - the url of the site that should be analyzed
  - `--out` (mandatory) - the directory which should contain the tool's output
  - `--cookie-file` (optional) - the cookie file which contains cookies that are pre-loaded into the browser
  - `--verbosity` (optional) - the overall output verbosity (default: debug)
  - `--chromium-path` (optional) - set a specific path to a chrome / chromium binary
  - `--webdriver-path` (optional) - set a specific path to a chrome / chromium webdriver binary
  - `--port-proxy` (optional) - set a specific port of the http proxy (default: 20201)
- Interact with the website, i.e., execute the Single Sign-On flow
- If you are done, manually stop by tool by hitting `ENTER` on the command prompt
- Investigate the output:
  - `cookiejar.json` - contains all cookies that were set during the browser session
  - `history.json` - database storing all reports sent from the chrome extension to the backend
  - `logs.log` - logging file of general purpose and for debugging
  - `proxy.dump` - database of all http requests and responses in mitmproxy's format
    - You can start a web instance of mitmproxy: `mitmweb`
    - Then, go to `http://127.0.0.1:8081/`, click `mitmproxy -> open`, and load the `proxy.dump` file
  - `proxy.har` - database of all http requests and responses in well-known [HAR](https://w3c.github.io/web-performance/specs/HAR/Overview.html) format
  - `proxy_stderr.log` and `proxy_stdout.log` - output streams of proxy, usually empty
  - `report.json` - contains the most relevant information about this output trace, i.e., which SSO flows were started and in which configuration
  - `sequencediagram.txt` and `sequencediagram.svg`: contains the sequence diagram of the SSO flow generated by DISTINCT in textual and visual form
    - You can recompile the textual representation with `java -jar [plantuml.jar] -svg [sequencediagram.txt]`
    - You can find the `plantuml.jar` in the `tools` directory

## Layout

> TODO: Outdated, change to v2

- `./chrome_extension` - contains the chrome extension that monitors the in-browser events and sends them in reports back to the python backend
- `./mitmproxy` - contains the configurations for the proxy
- `./model` - contains all python classes for the backend's post-processing
- `./processors` - contains the processors for each report that (1) generate the output (i.e., sequence diagram), and (2) analyze the patterns (i.e., security checks, back tracing, ...)
- `./tests` - contains tests for the virtual execution context
- `config.py` - performs basic configurations, i.e., sets up the browser
- `main.py` - main routine
