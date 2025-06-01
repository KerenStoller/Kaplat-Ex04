import uvicorn

from starlette.datastructures import State
from fastapi import FastAPI
from starlette.responses import JSONResponse

from models import CalculatorRequestBody, StackRequestBody, Action
from Calculate import calculate, checkValidity, checkValidityStackAndOperate
from Stack import addArguments, removeArguments

app = FastAPI()
app.state = State()
app.state.stack = []
app.state.stack_history = []
app.state.independent_history = []


@app.get("/calculator/health")
def health():
    return "OK"


@app.post("/calculator/independent/calculate")
def calculatePage(request: CalculatorRequestBody):

    is_there_an_error = checkValidity(request.arguments, request.operation)
    if is_there_an_error:
        return is_there_an_error

    result = calculate(request)

    if "Error" in result:
        return result["Error"]

    result = result["result"]

    action = Action(flavor="INDEPENDENT", operation=request.operation.lower(), arguments=request.arguments, result=result)
    app.state.independent_history.append(action)

    return {"result": result}


@app.get("/calculator/stack/size")
def stackSize():
    return {"result": len(app.state.stack)}


@app.put("/calculator/stack/arguments")
def stackArguments(request: StackRequestBody):
    addArguments(app.state.stack, request.arguments)
    return {"result": len(app.state.stack)}


@app.get("/calculator/stack/operate")
def stackOperate(operation: str):
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

    return {"result": result}


@app.delete("/calculator/stack/arguments")
def deleteStackArguments(count: int):
    error_response = removeArguments(app.state.stack, count)
    if error_response:
        return error_response

    return {"result": len(app.state.stack)}


@app.get("/calculator/history")
def getHistory(flavor: str | None = None):

    #no other case will be checked
    if flavor == 'STACK':
        return {"result": app.state.stack_history}
    if flavor == 'INDEPENDENT':
        return {"result": app.state.independent_history}
    else:
        return {"result": app.state.stack_history + app.state.independent_history}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8496)