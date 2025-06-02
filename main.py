import json
import uvicorn
from starlette.datastructures import State
from fastapi import FastAPI, Query

from models import CalculatorRequestBody, StackRequestBody, Action
from Calculate import calculate, checkValidity, checkValidityStackAndOperate
from Stack import addArguments, removeArguments
from logger import (stack_logger,
                    independent_logger,
                    addInfoLogToRequest,
                    addDebugLogToRequest,
                    addInfoLog,
                    addDebugLog,
                    addErrorLog,
                    updateLogLevel,
                    getLogLevelInUpper)


app = FastAPI()
app.state = State()
app.state.stack = []
app.state.stack_history = []
app.state.independent_history = []


@app.get("/calculator/health")
def health():
    addInfoLogToRequest("/calculator/health", "get")

    result_to_return = "OK"

    addDebugLogToRequest()
    return result_to_return


@app.post("/calculator/independent/calculate")
def calculatePage(request: CalculatorRequestBody):
    addInfoLogToRequest("/calculator/independent/calculate", "post")

    operation = request.operation
    arguments = request.arguments

    is_there_an_error = checkValidity(arguments, operation)
    if is_there_an_error:
        body_dict = json.loads(is_there_an_error.body.decode())
        addErrorLog(independent_logger, body_dict["errorMessage"])
        return is_there_an_error

    result = calculate(request)

    if "Error" in result:
        body_dict = json.loads(result["Error"].body.decode())
        addErrorLog(independent_logger, body_dict["errorMessage"])
        return result["Error"]

    result = result["result"]

    action = Action(flavor="INDEPENDENT", operation=operation.lower(), arguments=arguments, result=result)
    app.state.independent_history.append(action)
    result_to_return = {"result": result}

    addInfoLog(independent_logger, f"Performing operation {operation}. Result is {result}")
    addDebugLog(independent_logger, f"Performing operation: {operation}({','.join(map(str, arguments))}) = {result}")
    addDebugLogToRequest()
    return result_to_return



@app.get("/calculator/stack/size")
def getStackSize():
    addInfoLogToRequest("/calculator/stack/size", "get")

    stack_size = len(app.state.stack)
    result_to_return = {"result": stack_size}

    addInfoLog(stack_logger, f"Stack size is {stack_size}")
    addDebugLog(stack_logger, f"Stack content (first == top): [{', '.join(map(str, reversed(app.state.stack)))}]")
    addDebugLogToRequest()
    return result_to_return



@app.put("/calculator/stack/arguments")
def stackArguments(request: StackRequestBody):
    addInfoLogToRequest("/calculator/stack/arguments", "put")

    stack_size_before = len(app.state.stack)
    amount_added = addArguments(app.state.stack, request.arguments)
    stack_size = len(app.state.stack)
    result_to_return = {"result": stack_size}

    addInfoLog(stack_logger, f"Adding total of {amount_added} argument(s) to the stack | Stack size: {stack_size}")
    addDebugLog(stack_logger, f"Adding arguments: {','.join(map(str, request.arguments))} | Stack size before {stack_size_before} | stack size after {stack_size}")
    addDebugLogToRequest()
    return result_to_return



@app.get("/calculator/stack/operate")
def stackOperate(operation: str):
    addInfoLogToRequest("/calculator/stack/operate", "get")

    response = checkValidityStackAndOperate(app.state.stack, operation)

    if "Error" in response:
        body_dict = json.loads(response["Error"].body.decode())
        addErrorLog(stack_logger, body_dict["errorMessage"])
        return response["Error"]

    arguments = response["arguments"]

    request = CalculatorRequestBody(arguments=arguments, operation=operation)
    result = calculate(request)

    if "Error" in result:
        body_dict = json.loads(response["Error"].body.decode())
        addErrorLog(stack_logger, body_dict["errorMessage"])
        return result["Error"]

    result = result["result"]

    action = Action(flavor="STACK", operation=operation.lower(), arguments=arguments, result=result)
    app.state.stack_history.append(action)

    result_to_return = {"result": result}


    stack_size = len(app.state.stack)
    addInfoLog(stack_logger, f"Performing operation {operation}. Result is {result} | stack size: {stack_size}")
    addDebugLog(stack_logger, f"Performing operation: {operation}({','.join(map(str, arguments))}) = {result}")
    addDebugLogToRequest()
    return result_to_return



@app.delete("/calculator/stack/arguments")
def deleteStackArguments(count: int):
    addInfoLogToRequest("/calculator/stack/arguments", "delete")

    error_response = removeArguments(app.state.stack, count)
    if error_response:
        body_dict = json.loads(error_response.body.decode())
        addErrorLog(stack_logger, body_dict["errorMessage"])
        return error_response

    stack_size = len(app.state.stack)
    result_to_return = {"result": stack_size}

    addInfoLog(stack_logger, f"Removing total {count} argument(s) from the stack | Stack size: {stack_size}")
    addDebugLogToRequest()
    return result_to_return



@app.get("/calculator/history")
def getHistory(flavor: str | None = None):
    addInfoLogToRequest("/calculator/history", "get")

    #no other case will be checked
    if flavor == 'STACK':
        result_to_return =  {"result": app.state.stack_history}
        addInfoLog(stack_logger, f"History: So far total {len(app.state.stack_history)} stack actions")
    elif flavor == 'INDEPENDENT':
        result_to_return = {"result": app.state.independent_history}
        addInfoLog(independent_logger, f"History: So far total {len(app.state.independent_history)} independent actions")
    else:
        result_to_return = {"result": app.state.stack_history + app.state.independent_history}
        addInfoLog(stack_logger, f"History: So far total {len(app.state.stack_history)} stack actions")
        addInfoLog(independent_logger, f"History: So far total {len(app.state.independent_history)} independent actions")

    addDebugLogToRequest()
    return result_to_return


@app.get("/logs/level")
def getLogLevel(logger_name: str = Query(..., alias="logger-name")):
    addInfoLogToRequest("/logs/level", "get")

    response = getLogLevelInUpper(logger_name)
    if "Error" in response:
        addErrorLog(stack_logger, response["Error"])
        return response["Error"]

    addDebugLogToRequest()
    return response


@app.put("/logs/level")
def putLogLevel(
    logger_name: str = Query(..., alias="logger-name"),
    logger_level: str = Query(..., alias="logger-level")
):
    addInfoLogToRequest("/logs/level", "put")

    response = updateLogLevel(logger_name, logger_level)
    if "Error" in response:
        addErrorLog(stack_logger, response["Error"])
        return response["Error"]

    addDebugLogToRequest()
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8496)