import logging

import azure.functions as func


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="HelloWorld", methods=["GET", "POST"])
def hello_world(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        name = req_body.get("name")

    body = "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response."
    if name:
        body = f"Hello, {name}. This HTTP triggered function executed successfully."

    return func.HttpResponse(body, status_code=200)