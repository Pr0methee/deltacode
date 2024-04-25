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
    def __init__(self,obj,t):
        super().__init__(f"Incorrect convertion, {obj} can't be turn into a {t} object")
    
    def name(self):
        return "ConvertionError : "
    
class UnknownObject(Exception):
    def __init__(self,t):
        super().__init__(f"I don't know object '{t}' ")
    
    def name(self):
        return "UnknownObject : "

class TypeError(Exception):
    def __init__(self, obj,typ=1) -> None:
        if typ == 1 :super().__init__(f"{obj} can't be understood as a type.")
        elif typ == 2: super().__init__(f"{obj} can't be called, it is neither a function nor an application.")
    def name(self):
        return 'TypeError : '

class TypeError_(Exception):
    def __init__(self, expr,name,gettyp,reqtyp) -> None:
        super().__init__(f"Can't affect {''.join(expr)} to <{name}>, it has the type {gettyp} while it's expected to be a {reqtyp} object")
    def name(self):
        return 'TypeError : '
    
class InvalidName(Exception):
    def __init__(self, name) -> None:
        super().__init__(f"Invalid name for an object : '{name}'")
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

class ModuleError(Exception):
    def __init__(self, mod) -> None:
        super().__init__(f"Error while trying to load module : {mod} ")
    
    def name(self):
        return "ModuleError : "

class UnsupportedOperation(Exception):
    def __init__(self, op,t1,t2=None) -> None:
        if t2 is None:
            super().__init__(f"Unsupported opération {op} on {t1} objects")
        else:
            super().__init__(f"Unsupported opération {op} between {t1} and {t2} objects")

    
    def name(self):
        return "UnsupportedOperation : "

class UnexpectedArgument(Exception):
    def __init__(self,given,req,wanted=''):
        if wanted =='':
            super().__init__(f"You named {given} arguments while {req} are expected")
        else:
            super().__init__(f"You named {given} arguments while {req} are expected and should be : {wanted}")
    def name(self):
        return "UnexpectedArgument : "  

class DeniedAccessError(Exception):
    def __init__(self, f) -> None:
        super().__init__(f"You tried to access the function : {f} from global code, but it's in restricted mode.")
    
    def name(self):
        return "DeniedAccessError : "

class IterationError(Exception):
    def __init__(self, t) -> None:
        super().__init__(f"Unable to iterate on {t} objects")
    
    def name(self):
        return "IterationError : "

class InvalidKeyError(Exception):
    def __init__(self, k) -> None:
        super().__init__(f"Unable to access the value associated with {k} : it does not exists.")
    
    def name(self):
        return "InvalidKeyError : "
    
class TooEarlyToAccessError(Exception):
    def __init__(self, v) -> None:
        super().__init__(f"Unable to access the value of {v} : it has not been defined.")
    
    def name(self):
        return "TooEarlyToAccessError : "
    
class IndexError(Exception):
    def __init__(self, v) -> None:
        super().__init__(f"Index {v} is not correct")
    
    def name(self):
        return "IndexError : "

class AttributeError(Exception):
    def __init__(self, f,typ) -> None:
        super().__init__(f"Unknown method {f} on {typ} objects.")
    
    def name(self):
        return "AttributeError : "