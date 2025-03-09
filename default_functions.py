import default_types #import *
import error

DEFAULT_FUNCTIONS = ['ask', 'card', 'echo','convert','dim','help','set_of','ordering']

def set_of(obj):#
    """
    set_of : Ω ⟶ 𝕋.
    Returns the type of the give object    
    """
    if 'Instance' in obj.__repr__():
        return obj.get_type()
    return type(obj)

def help(v):#
    """help : Ω ⟶ ℘(∅)\nShows the documentation of the given object"""
    echo(v.__doc__)
    return default_types.EmptySet()

def echo(v):#
    """echo : Ω ⟶ ℘(∅)
Displays the string convertion of the given object"""
    print(v)#,file=file)
    return default_types.EmptySet()

def ask(t,ch):#
    """ask : 𝐓×ϩ ⟶ Ω\nDisplays the given string and waits for an input of the user that must be understandable as being of the given type.\nReturns the value gave by the user in the given type"""
    assert type(ch)==default_types.S
    t=default_types.type_from_str(t)
    while True:
        rep = input(ch)
        if t.recognize(rep):break
    return t.from_str(rep)

def convert(obj,typ):#
    """
    convert : Ω×𝐓 ⟶ Ω
    Tries to understand the given object as being of the given type.
    It can raise an error if the input can't  be understood as being in the wanted set.
    Returns the input converted in the asked type 
    """
    if str(obj)==str(typ):return obj#cas instance vers Object
    if typ == 'Ω':return obj
    if type(typ)==str:
        typ = default_types.type_from_str(typ)
    if typ == default_types.Parts(default_types.EmptySet) and type(obj)==default_types.EmptySet:
        return default_types.EmptySet()
    if typ ==type(obj):return obj
    if typ == default_types.S:
        try:
            return obj.stringify()
        except:
            return default_types.S(str(obj))
    
    if type(obj) == default_types.ZIntervalle and type(typ)==default_types.Parts:
        if (typ.typ == default_types.N and obj.binf >= default_types.N(0)) or typ.typ == default_types.Z:
            return obj
        else:
            raise error.ConvertionError(obj,default_types.stringify(typ))
    
    if type(typ)==default_types.Parts:
        if not(type(obj)==default_types.SET or type(obj)==default_types.EmptySet or type(obj)==default_types.OrderedSET):
            raise error.ConvertionError(obj,default_types.stringify(typ))
        if type(obj) == default_types.EmptySet:
            return default_types.SET(typ.typ)

        if type(obj)==default_types.SET:
            r = default_types.SET(typ.typ)
            for elt in obj:
                r.add(convert(elt,typ.typ))
        else:
            r = default_types.OrderedSET(typ.typ)
            for elt in obj:
                r.add(convert(elt,typ.typ))
        return r

    if 'Object' in str(typ):
        if 'Instance' not in str(type(obj)):
            raise error.ConvertionError(obj,typ)
        if obj.type != typ:
            raise error.ConvertionError(obj,typ)
        return obj

    if type(typ)!=default_types.CrossSet:
        if type(obj) not in default_types.INCLUSIONS:
            raise error.ConvertionError(obj,typ)
        if not typ in default_types.INCLUSIONS[type(obj)]:raise error.ConvertionError(obj,typ)
        return typ(obj.value)
    
    #ici typ est un CrossSet
    if type(obj)!=default_types.Tuple:
        raise error.ConvertionError(obj,default_types.stringify(typ))

    if len(obj.v) != len(typ.schema):
        raise error.ConvertionError(obj,default_types.stringify(typ))
    
    for i in range(len(obj.v)):
        if 'Object' in str(obj.v[i]):
            if typ.schema[i] != obj.v[i].type:
                raise error.ConvertionError(obj,default_types.stringify(typ))
        else:
            if not default_types.include(type(obj.v[i]),typ.schema[i]):
                raise error.ConvertionError(obj,default_types.stringify(typ))

    t=[]
    for i in range(len(typ.schema)):
        t.append(convert(obj[i],typ.schema[i]))
    return default_types.Tuple(tuple(t),typ)

def dim(elt):
    """
    dim : 𝐓 ⟶ ℕ
    dim : Ω ⟶ ℕ
    Works only on Tuples and CrossSets.
    Returns the number of components of the given Tuple/CrossSet
    """
    if not(type(elt)==default_types.CrossSet or type(elt)==default_types.Tuple):
        raise error.UnsupportedOperation('dim',default_types.stringify(type(elt)))
    if type(elt)==default_types.Tuple:
        return dim(elt.type)
    return default_types.N(len(elt.schema))

def card(elt):
    """
    card : ℘(Ω) ⟶ ℕ
    Returns the number of elements of the given set
    """
    if type(elt)!=default_types.SET:
        raise error.UnsupportedOperation('card',default_types.stringify(type(elt)))
    return default_types.N(len(elt.deep_get()))

def ordering(elt):
    """
    ordering : ℘(Ω) ⟶ ℘(Ω)
    Returns the given set with the same elements but sorted by the natural ordering
    """
    if type(elt)!=default_types.SET and type(elt)!=default_types.OrderedSET:
        raise error.UnsupportedOperation('ordering',default_types.stringify(type(elt)))

    r= default_types.OrderedSET(elt.type)
    l = list(elt.deep_get())
    quickSort(l,0,len(l)-1)
    for th in l:
        r.add(th)
    return r

def IN(v,t):
    if str(type(t)) == "<class 'default_types.SET'>":
        return default_types.B(v in t.deep_get())
    if str(type(t)) not in ("<class 'type'>","<class 'POO.Object'>"):
        return default_types.B(False)
    #Operateur \in
    try: 
        convert(v,t)
        return default_types.B(True)
    except:
        return default_types.B(False)
    
def INCLUDE(v,t,obj):
    if type(v)==str:
        v=default_types.type_from_str(v,obj)
    if type(t)==str:
        t=default_types.type_from_str(t,obj)

    if default_types.include(v,t):
        return default_types.B(True)

    if str(type(t)) == "<class 'POO.ParametrizedObject'>":
        return default_types.B(str(type(v)) == "<class 'POO.RepresentParametrizedObject'>" and v.obj == t)
    elif str(type(t)) == "<class 'POO.RepresentParametrizedObject'>":
        return default_types.B(str(type(v)) == "<class 'POO.RepresentParametrizedObject'>" and t.obj == v.obj and INCLUDE(v.param,t.param,obj).v)



    if str(type(t)) not in ("<class 'type'>","<class 'POO.Object'>","<class 'default_types.SET'>"):
        return default_types.B(False)
    
    if v == default_types.EmptySet():
        return default_types.B(True)
    
    if str(type(v)) != "<class 'default_types.SET'>":
        return default_types.B(False)
    
    for elt in v:
        if not IN(elt,t):
            return default_types.B(False)
    
    return default_types.B(True)


def stringify(t):
    if t == default_types.EmptySet:return '∅'
    if t in default_types.TYPES_:
        return default_types.TYPES_[t]
    if '<' in str(t) :
        try:
            return t.name
        except:
            return "Created"
    return str(t)

# Function to find the partition position
def partition(array, low, high):

    # choose the rightmost element as pivot
    pivot = array[high]

    # pointer for greater element
    i = low - 1

    # traverse through all elements
    # compare each element with pivot
    for j in range(low, high):
        if array[j] <= pivot:

            # If element smaller than pivot is found
            # swap it with the greater element pointed by i
            i = i + 1

            # Swapping element at i with element at j
            (array[i], array[j]) = (array[j], array[i])

    # Swap the pivot element with the greater element specified by i
    (array[i + 1], array[high]) = (array[high], array[i + 1])

    # Return the position from where partition is done
    return i + 1

# function to perform quicksort


def quickSort(array, low, high):
    if low < high:

        # Find pivot element such that
        # element smaller than pivot are on the left
        # element greater than pivot are on the right
        pi = partition(array, low, high)

        # Recursive call on the left of pivot
        quickSort(array, low, pi - 1)

        # Recursive call on the right of pivot
        quickSort(array, pi + 1, high)