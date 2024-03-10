class WrongAssertion(Exception):
    def __init__(self,test) -> None:
        super().__init__(f"Assertion {''.join(test)} has failled.")

    def name(self):
        return "WrongAssertion : "

class DividingByZero(Exception):pass

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
        return 'TypeError'
    
class InvalidName(Exception):
    def __init__(self, name) -> None:
        super().__init__(f"Invalid name for an object : {name}")
    def name(self):
        return 'InvalidName'

class NameError(Exception):
    def __init__(self, name) -> None:
        super().__init__(f"Unable to affect value to {name}, it does not exist.")
    def name(self):
        return "NameError"

class WrongSyntax(Exception):
    def __init__(self) -> None:
        super().__init__("This sentence is syntaxly incorrect.")
    
    def name(self):
        return "WrongSyntax : "

class AlreadyExistsError(Exception):
    def __init__(self, name) -> None:
        super().__init__(f"Variable {name} already exists, we can't create it again.")
    
    def name(self):
        return "AlreadyExistsError"

class EOI(Exception):
    def __init__(self):
        super().__init__()
    
    def name(self):
        return "EOI"

class Halt(Exception):
    def __init__(self) -> None:
        super().__init__(f"The running program has been stopped")
    
    def name(self):
        return "Halt"

class OverWritingWarning(Warning):
    def __init__(self, name) -> None:
        super().__init__(f"Warning : the variable {name} has been overwrote.")