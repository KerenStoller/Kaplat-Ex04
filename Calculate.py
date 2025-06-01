from enum import Enum
from math import factorial
from fastapi import status
from fastapi.responses import JSONResponse
from models import CalculatorRequestBody


class CalculateOperations(str, Enum):
    PLUS = "plus"
    MINUS = 'minus'
    TIMES = 'times'
    DIVIDE = 'divide'
    POW = 'pow'
    ABS = 'abs'
    FACT = 'fact'

def isOperation(operation: str) -> bool:
    try:
        CalculateOperations(operation.lower())
    except ValueError:
        return False
    return True

def isUnaryOperator(operation: str):
    operation = operation.lower()
    if operation == CalculateOperations.ABS.value or operation == CalculateOperations.FACT.value:
        return True
    return False

def checkOperationValidity(operation: str):
    operation = operation.lower()

    # validate operation name
    if not isOperation(operation):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "errorMessage": f"Error: unknown operation: {operation}"
                }
        )
    return None

def checkValidity(arguments: list[int], operation: str):

    response = checkOperationValidity(operation)
    if response:
        return response


    # validate amount of Arguments
    if len(arguments) < 1:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "errorMessage": f"Error: Not enough arguments to perform the operation {operation}"
            }
        )
    if isUnaryOperator(operation):
        if len(arguments) > 1:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "errorMessage": f"Error: Too many arguments to perform the operation {operation}"
                }
            )
    elif len(arguments) > 2:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "errorMessage": f"Error: Too many arguments to perform the operation {operation}"
            }
        )
    elif len(arguments) == 1:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "errorMessage": f"Error: Not enough arguments to perform the operation {operation}"
            }
        )

    return None

def checkValidityStackAndOperate(stack: list[int], operation: str):

    response = checkOperationValidity(operation)
    if response:
        return {"Error" :response}

    arguments = []

    if isUnaryOperator(operation):
        if len(stack) < 1:
            return {"Error": JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "errorMessage": f"Error: cannot implement operation {operation}. It requires 1 arguments and the stack has only 0 arguments"
                }
            )}
        else:
            arguments.append(stack.pop())
    else:
        if len(stack) < 2:
            return {"Error": JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "errorMessage": f"Error: cannot implement operation {operation}. It requires 2 arguments and the stack has only {len(stack)} arguments"
                }
            )}
        else:
            arguments.append(stack.pop())
            arguments.append(stack.pop())

    return {"arguments": arguments}

def calculate(request: CalculatorRequestBody):

    operation_enum = CalculateOperations(request.operation.lower())

    x = request.arguments[0]

    y = 0
    if not isUnaryOperator(request.operation):
        y = request.arguments[1]

    result = 0

    match operation_enum:
        case CalculateOperations.PLUS:
            result = x + y
        case CalculateOperations.MINUS:
            result = x - y
        case CalculateOperations.TIMES:
            result = x * y
        case CalculateOperations.DIVIDE:
            if y == 0:
                return {"Error": JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "errorMessage": "Error while performing operation Divide: division by 0"
                    }
                )}
            result = x // y
        case CalculateOperations.POW:
            result = x ** y
        case CalculateOperations.ABS:
            result = abs(x)
        case CalculateOperations.FACT:
            if x <= 0:
                return {"Error": JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={
                        "errorMessage": "Error while performing operation Factorial: not supported for the negative number"
                    }
                )}
            result = factorial(x)

    return {"result" :result}