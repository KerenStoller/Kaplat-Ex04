import json
import uvicorn
from starlette.datastructures import State
from fastapi import FastAPI, Query

from models import CalculatorRequestBody, StackRequestBody, Action
from Calculate import calculate, checkValidity, checkValidityStackAndOperate
from Stack import addArguments, removeArguments
from logger_setup import LoggerManager


app = FastAPI()
app.state = State()
app.state.stack = []
app.state.stack_history = []
app.state.independent_history = []
app.state.logger_manager = LoggerManager()


@app.get("/calculator/health")
def health():
    app.state.logger_manager .add_info_log_to_request("/calculator/health", "get")

    result_to_return = "OK"

    app.state.logger_manager .add_debug_log_to_request()
    return result_to_return


@app.post("/calculator/independent/calculate")
def calculatePage(request: CalculatorRequestBody):
    app.state.logger_manager .add_info_log_to_request("/calculator/independent/calculate", "post")

    operation = request.operation
    arguments = request.arguments

    is_there_an_error = checkValidity(arguments, operation)
    if is_there_an_error:
        body_dict = json.loads(is_there_an_error.body.decode())
        app.state.logger_manager .add_error_log(app.state.logger_manager .independent_logger, body_dict["errorMessage"])
        return is_there_an_error

    result = calculate(request)

    if "Error" in result:
        body_dict = json.loads(result["Error"].body.decode())
        app.state.logger_manager .add_error_log(app.state.logger_manager .independent_logger, body_dict["errorMessage"])
        return result["Error"]

    result = result["result"]

    action = Action(flavor="INDEPENDENT", operation=operation.lower(), arguments=arguments, result=result)
    app.state.independent_history.append(action)
    result_to_return = {"result": result}

    app.state.logger_manager .add_info_log(app.state.logger_manager .independent_logger, f"Performing operation {operation}. Result is {result}")
    app.state.logger_manager .add_debug_log(app.state.logger_manager .independent_logger, f"Performing operation: {operation}({','.join(map(str, arguments))}) = {result}")
    app.state.logger_manager .add_debug_log_to_request()
    return result_to_return



@app.get("/calculator/stack/size")
def getStackSize():
    app.state.logger_manager .add_info_log_to_request("/calculator/stack/size", "get")

    stack_size = len(app.state.stack)
    result_to_return = {"result": stack_size}

    app.state.logger_manager .add_info_log(app.state.logger_manager .stack_logger, f"Stack size is {stack_size}")
    app.state.logger_manager .add_debug_log(app.state.logger_manager .stack_logger, f"Stack content (first == top): [{', '.join(map(str, reversed(app.state.stack)))}]")
    app.state.logger_manager .add_debug_log_to_request()
    return result_to_return



@app.put("/calculator/stack/arguments")
def stackArguments(request: StackRequestBody):
    app.state.logger_manager .add_info_log_to_request("/calculator/stack/arguments", "put")

    stack_size_before = len(app.state.stack)
    amount_added = addArguments(app.state.stack, request.arguments)
    stack_size = len(app.state.stack)
    result_to_return = {"result": stack_size}

    app.state.logger_manager .add_info_log(app.state.logger_manager .stack_logger, f"Adding total of {amount_added} argument(s) to the stack | Stack size: {stack_size}")
    app.state.logger_manager .add_debug_log(app.state.logger_manager .stack_logger, f"Adding arguments: {','.join(map(str, request.arguments))} | Stack size before {stack_size_before} | stack size after {stack_size}")
    app.state.logger_manager .add_debug_log_to_request()
    return result_to_return



@app.get("/calculator/stack/operate")
def stackOperate(operation: str):
    app.state.logger_manager .add_info_log_to_request("/calculator/stack/operate", "get")

    response = checkValidityStackAndOperate(app.state.stack, operation)

    if "Error" in response:
        body_dict = json.loads(response["Error"].body.decode())
        app.state.logger_manager .add_error_log(app.state.logger_manager .stack_logger, body_dict["errorMessage"])
        return response["Error"]

    arguments = response["arguments"]

    request = CalculatorRequestBody(arguments=arguments, operation=operation)
    result = calculate(request)

    if "Error" in result:
        body_dict = json.loads(response["Error"].body.decode())
        app.state.logger_manager .add_error_log(app.state.logger_manager .stack_logger, body_dict["errorMessage"])
        return result["Error"]

    result = result["result"]

    action = Action(flavor="STACK", operation=operation.lower(), arguments=arguments, result=result)
    app.state.stack_history.append(action)

    result_to_return = {"result": result}


    stack_size = len(app.state.stack)
    app.state.logger_manager .add_info_log(app.state.logger_manager .stack_logger, f"Performing operation {operation}. Result is {result} | stack size: {stack_size}")
    app.state.logger_manager .add_debug_log(app.state.logger_manager .stack_logger, f"Performing operation: {operation}({','.join(map(str, arguments))}) = {result}")
    app.state.logger_manager .add_debug_log_to_request()
    return result_to_return



@app.delete("/calculator/stack/arguments")
def deleteStackArguments(count: int):
    app.state.logger_manager .add_info_log_to_request("/calculator/stack/arguments", "delete")

    error_response = removeArguments(app.state.stack, count)
    if error_response:
        body_dict = json.loads(error_response.body.decode())
        app.state.logger_manager .add_error_log(app.state.logger_manager .stack_logger, body_dict["errorMessage"])
        return error_response

    stack_size = len(app.state.stack)
    result_to_return = {"result": stack_size}

    app.state.logger_manager .add_info_log(app.state.logger_manager .stack_logger, f"Removing total {count} argument(s) from the stack | Stack size: {stack_size}")
    app.state.logger_manager .add_debug_log_to_request()
    return result_to_return



@app.get("/calculator/history")
def getHistory(flavor: str | None = None):
    app.state.logger_manager .add_info_log_to_request("/calculator/history", "get")

    #no other case will be checked
    if flavor == 'STACK':
        result_to_return =  {"result": app.state.stack_history}
        app.state.logger_manager .add_info_log(app.state.logger_manager .stack_logger, f"History: So far total {len(app.state.stack_history)} stack actions")
    elif flavor == 'INDEPENDENT':
        result_to_return = {"result": app.state.independent_history}
        app.state.logger_manager .add_info_log(app.state.logger_manager .independent_logger, f"History: So far total {len(app.state.independent_history)} independent actions")
    else:
        result_to_return = {"result": app.state.stack_history + app.state.independent_history}
        app.state.logger_manager .add_info_log(app.state.logger_manager .stack_logger, f"History: So far total {len(app.state.stack_history)} stack actions")
        app.state.logger_manager .add_info_log(app.state.logger_manager .independent_logger, f"History: So far total {len(app.state.independent_history)} independent actions")

    app.state.logger_manager .add_debug_log_to_request()
    return result_to_return


@app.get("/logs/level")
def getLogLevel(logger_name: str = Query(..., alias="logger-name")):
    app.state.logger_manager .add_info_log_to_request("/logs/level", "get")

    response = app.state.logger_manager .get_log_level_in_upper(logger_name)
    if "Error" in response:
        app.state.logger_manager .add_error_log(app.state.logger_manager .stack_logger, response["Error"])
        return response["Error"]

    app.state.logger_manager .add_debug_log_to_request()
    return response


@app.put("/logs/level")
def putLogLevel(
    logger_name: str = Query(..., alias="logger-name"),
    logger_level: str = Query(..., alias="logger-level")
):
    app.state.logger_manager .add_info_log_to_request("/logs/level", "put")

    response = app.state.logger_manager .update_log_level(logger_name, logger_level)
    if "Error" in response:
        app.state.logger_manager .add_error_log(app.state.logger_manager .stack_logger, response["Error"])
        return response["Error"]

    app.state.logger_manager .add_debug_log_to_request()
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8496)