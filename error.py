class Error(Exception):
    def __init__(self,name,txt=""):
        super().__init__(txt)
        self.me=name
    
    def name(self):
        return self.me

class InFunctionError(Exception):
    def __init__(self,err,ph,nomfct):
        super().__init__()
        self.err = err
        self.ph = ph
        self.nomfct = nomfct

    def __str__(self):
        return self.err.name()+" has occured in "+self.nomfct+"  while executing "+self.ph+" : \n"+str(self.err)

    def name(self):
        return "An error"



class WrongAssertion(Error):
    def __init__(self,test) -> None:
        super().__init__("WrongAssertion",f"Assertion {' '.join(test)} has failled.")

class DividingByZero(Error):
    def __init__(self) -> None:
        super().__init__("DividingByZero",f"You tried to divide by zero")

class ConvertionError(Error):
    def __init__(self,obj,t):
        super().__init__("ConvertionError",f"Incorrect convertion, {obj} can't be turn into a {t} object")
    
class UnknownObject(Error):
    def __init__(self,t):
        super().__init__("UnknownObject",f"I don't know object '{t}' ")

class TypeError(Error):
    def __init__(self, obj,typ=1) -> None:
        if type(obj)==list:
            obj = ' '.join(obj)

        if typ == 1 :super().__init__( 'TypeError',f"{obj} can't be understood as a type.")
        elif typ == 2: super().__init__( 'TypeError',f"{obj} can't be called, it is neither a function nor an application.")

class TypeError_(Error):
    def __init__(self, expr,name,gettyp,reqtyp,t=1) -> None:
        if t==1:super().__init__('TypeError',f"Can't affect {' '.join(expr)} to <{name}>, it has the type {gettyp} while it's expected to be a {reqtyp} object")
        else:super().__init__('TypeError',f"{' '.join(expr)} has the type {gettyp} when evaluated, while it's expected to be a {reqtyp} object")

class DefinitionTypeError(Error):
    def __init__(self, meth,reqtyp,giventyp,t=1) -> None:
        if t==1:super().__init__('DefinitionTypeError',f"{meth} method should return an object of {reqtyp} not of {giventyp}")
        else:super().__init__('DefinitionTypeError',f"{meth} method should be defined on {reqtyp} set, not on {giventyp}")
    
class InvalidName(Error):
    def __init__(self, name) -> None:
        super().__init__('InvalidName',f"Invalid name for an object : '{name}'")

class NameError(Error):
    def __init__(self, name,typ=1) -> None:
        if typ ==1:super().__init__("NameError",f"Unable to affect value to {name}, it does not exist.")
        else:super().__init__("NameError",f"Unable to add a method to the object {name}, it does not exist.")

class WrongSyntax(Error):
    def __init__(self,*expr) -> None:
        super().__init__("WrongSyntax","This sentence is syntaxly incorrect." if expr==() else f"The sentence '{' '.join(expr)}' is syntaxly incorrect")

class AlreadyExistsError(Error):
    def __init__(self, name,typ=1) -> None:
        if typ==1:super().__init__("AlreadyExistsError",f"Object {name} already exists, we can't create it again.")
        else:super().__init__("AlreadyExistsError",f"Method {name} already exists, we can't create it again.")

class EOI(Error):
    def __init__(self):
        super().__init__("EOI")

class Halt(Error):
    def __init__(self) -> None:
        super().__init__("Halt",f"The running program has been stopped")

class OverWritingWarning(Warning):
    def __init__(self, name) -> None:
        super().__init__(f"Warning : the variable {name} has been overwrote.")

class EvaluationError(Error):
    def __init__(self, expr) -> None:
        super().__init__("EvaluationError",f"Error while evaluating {' '.join(expr)} ")

class ModuleError(Error):
    def __init__(self, mod) -> None:
        super().__init__("ModuleError",f"Error while trying to load module : {mod} ")

class ModuleNotFoundError(Error):
    def __init__(self, mod) -> None:
        super().__init__("ModuleNotFoundError",f"There is no module named : {mod} ")

class RedefiningError(Error):
    def __init__(self) -> None:
        super().__init__("RedefiningError",f"You tried to modify the value of a constant !")

class UnsupportedOperation(Error):
    def __init__(self, op,t1,t2=None) -> None:
        if t2 is None:
            super().__init__("OperatorError",f"Unsupported opération {op} on {t1} objects")
        else:
            super().__init__("OperatorError",f"Unsupported opération {op} between {t1} and {t2} objects")

class UnexpectedArgument(Error):
    def __init__(self,given,req,wanted=''):
        if wanted =='':
            super().__init__("ArgumentError", f"You named {given} arguments while {req} are expected")
        else:
            super().__init__("ArgumentError",f"You named {given} arguments while {req} are expected and should be : {wanted}")

class DeniedAccessError(Error):
    def __init__(self, f) -> None:
        super().__init__("DeniedAccessError",f"You tried to access the function : {f} from global code, but it's in restricted mode.")

class IterationError(Error):
    def __init__(self, t) -> None:
        super().__init__("IterationError",f"Unable to iterate on {t} objects")

class InvalidKeyError(Error):
    def __init__(self, k) -> None:
        super().__init__("InvalidKeyError",f"Unable to access the value associated with {k} : it does not exists.")
    
class TooEarlyToAccessError(Error):
    def __init__(self, v) -> None:
        super().__init__("TooEarlyToAccessError",f"Unable to access the value of {v} : it has not been defined.")
    
class IndexError(Error):
    def __init__(self, v) -> None:
        super().__init__("IndexError",f"Index {v} is not correct")

class AttributeError(Error):
    def __init__(self, f,typ) -> None:
        super().__init__("AttributeError",f"Unknown method {f} on {typ} objects.")
        
class StateError(Error):
    def __init__(self,state,obj):
        super().__init__("StateError","Illegal state %s for a(n) %s"%(state,obj))


class CreationError(Error):
    def __init__(self,thing):
        super().__init__("CreationError","Unable to create a "+thing+" inside a loop")