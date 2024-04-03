class WrongAssertion(Exception):
    def __init__(self,test) -> None:
        super().__init__(f"Assertion {''.join(test)} has failled.")

    def name(self):
        return "WrongAssertion : "

class DividingByZero(Exception):
    def __init__(self) -> None:
        super().__init__(f"You tried to divide by zero")

    def name(self):
        return "DividingByZero : "

class ConvertionError(Exception):
    def __init__(self):
        super().__init__(f"Incorrect convertion ")
    
    def name(self):
        return "ConvertionError : "
    
class UnknownObject(Exception):
    def __init__(self,t):
        super().__init__(f"I don't know object '{t}' ")
    
    def name(self):
        return "UnknownObject : "

class TypeError(Exception):
    def __init__(self, obj) -> None:
        super().__init__(f"{obj} can't be understood as a type.")
    def name(self):
        return 'TypeError : '

class TypeError_(Exception):
    def __init__(self, expr,name,gettyp,reqtyp) -> None:
        super().__init__(f"Can't affect {''.join(expr)} to <{name}>, it has the type {gettyp} while it's expected to be a {reqtyp} object")
    def name(self):
        return 'TypeError : '
    
class InvalidName(Exception):
    def __init__(self, name) -> None:
        super().__init__(f"Invalid name for an object : {name}")
    def name(self):
        return 'InvalidName : '

class NameError(Exception):
    def __init__(self, name) -> None:
        super().__init__(f"Unable to affect value to {name}, it does not exist.")
    def name(self):
        return "NameError : "

class WrongSyntax(Exception):
    def __init__(self,*expr) -> None:
        super().__init__("This sentence is syntaxly incorrect." if expr==() else f"The sentence '{''.join(expr)}' is syntaxly incorrect")
    
    def name(self):
        return "WrongSyntax : "

class AlreadyExistsError(Exception):
    def __init__(self, name) -> None:
        super().__init__(f"Object {name} already exists, we can't create it again.")
    
    def name(self):
        return "AlreadyExistsError : "

class EOI(Exception):
    def __init__(self):
        super().__init__()
    
    def name(self):
        return "EOI : "

class Halt(Exception):
    def __init__(self) -> None:
        super().__init__(f"The running program has been stopped")
    
    def name(self):
        return "Halt : "

class OverWritingWarning(Warning):
    def __init__(self, name) -> None:
        super().__init__(f"Warning : the variable {name} has been overwrote.")

class EvaluationError(Exception):
    def __init__(self, *expr) -> None:
        super().__init__(f"Error while evaluating {''.join(expr)} ")
    
    def name(self):
        return "EvaluationError : "