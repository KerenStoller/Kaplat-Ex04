import logging
from turtledemo.paint import switchupdown

import uvicorn
from starlette.datastructures import State
from fastapi import FastAPI

from models import CalculatorRequestBody, StackRequestBody, Action
from Calculate import calculate, checkValidity, checkValidityStackAndOperate
from Stack import addArguments, removeArguments
from logger import request_logger, stack_logger, independent_logger, addDitsToRequestLog


app = FastAPI()
app.state = State()
app.state.stack = []
app.state.stack_history = []
app.state.independent_history = []


@app.get("/calculator/health")
def health():
    addDitsToRequestLog(logging.INFO, "/calculator/health", "get")

    resultToReturn = "OK"

    addDitsToRequestLog(logging.DEBUG)
    return resultToReturn


@app.post("/calculator/independent/calculate")
def calculatePage(request: CalculatorRequestBody):
    addDitsToRequestLog(logging.INFO, "/calculator/independent/calculate", "post")

    is_there_an_error = checkValidity(request.arguments, request.operation)
    if is_there_an_error:
        return is_there_an_error

    result = calculate(request)

    if "Error" in result:
        return result["Error"]

    result = result["result"]

    action = Action(flavor="INDEPENDENT", operation=request.operation.lower(), arguments=request.arguments, result=result)
    app.state.independent_history.append(action)

    resultToReturn = {"result": result}

    addDitsToRequestLog(logging.DEBUG)
    return resultToReturn



@app.get("/calculator/stack/size")
def stackSize():
    addDitsToRequestLog(logging.INFO, "/calculator/stack/size", "get")

    resultToReturn = {"result": len(app.state.stack)}

    addDitsToRequestLog(logging.DEBUG)
    return resultToReturn



@app.put("/calculator/stack/arguments")
def stackArguments(request: StackRequestBody):
    addDitsToRequestLog(logging.INFO, "/calculator/stack/arguments", "put")

    addArguments(app.state.stack, request.arguments)
    resultToReturn = {"result": len(app.state.stack)}

    addDitsToRequestLog(logging.DEBUG)
    return resultToReturn



@app.get("/calculator/stack/operate")
def stackOperate(operation: str):
    addDitsToRequestLog(logging.INFO, "/calculator/stack/operate", "get")

    response = checkValidityStackAndOperate(app.state.stack, operation)

    if "Error" in response:
        return response["Error"]

    arguments = response["arguments"]

    request = CalculatorRequestBody(arguments=arguments, operation=operation)
    result = calculate(request)

    if "Error" in result:
        return result["Error"]

    result = result["result"]

    action = Action(flavor="STACK", operation=operation.lower(), arguments=arguments, result=result)
    app.state.stack_history.append(action)

    resultToReturn = {"result": result}

    addDitsToRequestLog(logging.DEBUG)
    return resultToReturn



@app.delete("/calculator/stack/arguments")
def deleteStackArguments(count: int):
    addDitsToRequestLog(logging.INFO, "/calculator/stack/arguments", "delete")

    error_response = removeArguments(app.state.stack, count)
    if error_response:
        return error_response

    resultToReturn = {"result": len(app.state.stack)}

    addDitsToRequestLog(logging.DEBUG)
    return resultToReturn



@app.get("/calculator/history")
def getHistory(flavor: str | None = None):
    addDitsToRequestLog(logging.INFO, "//calculator/history", "get")

    #no other case will be checked
    if flavor == 'STACK':
        resultToReturn =  {"result": app.state.stack_history}
    if flavor == 'INDEPENDENT':
        resultToReturn = {"result": app.state.independent_history}
    else:
        resultToReturn = {"result": app.state.stack_history + app.state.independent_history}

    addDitsToRequestLog(logging.DEBUG)
    return resultToReturn



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8496)