from fastapi import status
from fastapi.responses import JSONResponse

def addArguments(stack: list[int], arguments: list[int]):

    amount_of_arguments = len(arguments)
    i = 0
    while i < amount_of_arguments:
        stack.append(arguments[i])
        i += 1


def removeArguments(stack: list[int], amount_to_delete: int):
    amount_of_arguments = len(stack)
    if(amount_of_arguments < amount_to_delete or amount_to_delete <= 0):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "errorMessage": f"Error: cannot remove {amount_to_delete} from the stack. It has only {amount_of_arguments} arguments"
            }
        )
    else:
        while amount_to_delete > 0:
            stack.pop()
            amount_to_delete -= 1
