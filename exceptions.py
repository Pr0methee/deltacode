import error


class RunTimeException(Exception):
    def __init__(self, name, txt=""):
        super().__init__(txt)
        self.me = name

    def name(self):
        return self.me

def get_exception(ph:str):
    if not ph.startswith("RunTimeException(") or not ph.endswith(")"):
        raise error.WrongSyntax([ph])
    ph = ph[len("RunTimeException("):-1].split(',')
    if len(ph) != 2:
        raise error.WrongSyntax([ph])
    l=[]
    for elt in ph:
        if not elt.startswith("\"") or not elt.endswith("\""):
            raise error.WrongSyntax([ph])
        l.append(elt[1:-1])
    return RunTimeException(*l)