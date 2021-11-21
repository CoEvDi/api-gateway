# API-Gateway Micro-service

Description of API-gateway, proxy with route+auth validation for all other micro-services.

## General Info

Gateway gets all requests to the system and serve them to needed micro-service:
-   All requests contains special routing-header for quick search needed route in config
-   After that app perform matching method and route between request and config
-   If request's operation need auth, app send token from cookies to auth-microservice and gets auth headers
-   If auth is OK, app send request to micro-service and proxy response


## Frameworks and libs

-   Python3 + async (maybe just for now and will be reworked to multithread/multiprocessing) FastAPI + uvicorn
-   httpx
-   pyyaml

## Configuring

### Main config

-   **version**
-   **domain**
-   **update_interval** - time (seconds) between reading config-file
-   **token_name** - auth cookie nane with token
-   **route_header_name** - header-name for matching routes
-   **backends** - dict of all service micro-services
    -   **{name}** - name of micro-service
        -   **protocol** - http or secure https
        -   **host** - micro-service address
        -   **port** - micro-service port
        -   **route** - route for auth checking if this micro-service is for auth

### Routes config

All config is a dict of pairs header_route_name - route_data, and route data is:
-   **allowed_methods** - list of methond for route
-   **route_type** - static/dynamic (dynamic means you have routes like /account/{account_name})
-   **route_path** - path for matching with route in request (regexp for dynamic routes)
-   **destination** - name of micro-service to proxy
-   **auth_required** - True if need auth credentials from cookie-token
-   **auth_forbidden** - True if need block auth requests (for example you can't login while being logged-in)

## How to run described in [Information repo]


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [Information repo]: <https://github.com/CoEvDi/service-info#backend-installing>
