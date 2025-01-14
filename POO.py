from __future__ import annotations

import copy

from Callable import Function
import error,_parser_,default_types
from default_functions import stringify


class Object:
    def __init__(self,name,echo) -> None:
        valid_name_obj(name)
        self.name=name
        self.echo=echo
        self.methods = {}
        self.static_methods={}
        self.__doc__=self.__str__()+'\nNo methods'

    def __deepcopy__(self,memo):
        res = Object(self.name,self.echo)
        res.methods = self.methods
        res.static_methods = self.static_methods
        res.__doc__=self.__doc__
        return res
    
    def add_method(self,code,obj):
        code=code[1:-1]
        code=_parser_.parse(code,obj)
        if  len(code)<=2:raise error.WrongSyntax()
        if  len(code[0])!=5: raise error.WrongSyntax()
        nom=code[0][0].split('·')[1]
        if nom in self.methods or nom in self.static_methods:
            raise error.AlreadyExistsError(code[0][0],2)
        
        if code[0][1]!=':' or code[0][3] != '⟶':raise error.WrongSyntax()
        if not default_types.recognize_type(code[0][2],obj) : raise error.TypeError(code[0][2])
        if not default_types.recognize_type(code[0][4],obj) : raise error.TypeError(code[0][4])

        self.test_consistence(nom,code[0][2],code[0][4])
        f = Function(nom,default_types.type_from_str(code[0][2],obj),default_types.type_from_str(code[0][4],obj),True)
        s=False
        if not (len(code[1]) == 1 and code[1][0][0] == '⟨' and code[1][0][-1] == '⟩'):
            raise error.WrongSyntax()
        args = code[1][0][1:-1].split(';')

        args = [elt if elt !='' else '∅' for elt in args]
        f.set_args_name(*args)
        i=2
        if code[i] == ['@RESTRICT'] :
            f.set_restricted()
            i+=1
        if code[i] == ['@STATIC']:
            s=True
            f.is_meth=False
            i+=1

        if code[i] == []:raise error.WrongSyntax()
        if code[i][0] != "" and code[i][0][0]=='@':
            raise error.StateError(code[i][0],"method")
        if code[i][0][0]==code[i][0][-1]=='"':
            f.set_doc(code[i][0][1:-1])
            i+=1
        if not code[i:]: raise error.WrongSyntax()
        f.set_code(code[i:])
        if not s:self.methods[nom]=f
        else:self.static_methods[nom]=f

        self.__doc__ =self.__str__()+'\n'+'\n'.join(str(elt) for elt in self.methods.values())+'\n'.join(str(elt) for elt in self.static_methods.values())
    
    @staticmethod
    def test_consistence(n, t1, t2):
        if n =='start':
            if t2 != '℘(∅)':
                raise error.DefinitionTypeError('start','℘(∅)',t2)
        elif n in ('ge','gt','le','lt','eq','neq','and','or','equiv','impl','div'):
            if t2 != '𝔹':
                raise error.DefinitionTypeError('start','𝔹',t2)
            if t1 != 'Ω':
                raise error.DefinitionTypeError('start','Ω',t1,2)
        elif n == 'stringify':
            if t1 != '℘(∅)' :
                raise error.DefinitionTypeError('start','℘(∅)',t1,2)
            if t2 != '𝒮':
                raise error.DefinitionTypeError('start','𝒮',t2)

    def static_call(self,meth,var,dict,al,fct,obj,*args):
        if meth not in self.static_methods:raise error.AttributeError(meth,self.name)
        self.static_methods[meth].set_global_obj(copy.deepcopy(var),copy.deepcopy(fct),copy.deepcopy(al),copy.deepcopy(dict),copy.deepcopy(obj))
        r = self.static_methods[meth](self.echo, *args, father=self.name)
        return r
        
    def call(self,meth,instance:Instance,var,dict,al,fct,obj,*val):
        if meth not in self.methods:
            if meth=='stringify':
                return default_types.S(self.__str__())
            if meth == 'eq':
                return default_types.B(len(val)==1 and id(instance) == id(val[0]))
            if meth == 'neq':
                return default_types.B(len(val)!=1 or id(instance) != id(val[0]))
            raise error.AttributeError(meth,self.name)
        
        d = {'me':instance}
        self.methods[meth].set_global_obj({**instance.var_attributes,**var,**d},{**self.methods,**fct},al,{**instance.dict_attributes,**dict},obj)
        r=self.methods[meth](self.echo,*val,father=self.name)

        for k,v in self.methods[meth].VAR.items():
            if k.startswith('me·'):
                instance.var_attributes[k]=v

        for k,v in self.methods[meth].DICT.items():
            if k.startswith('me·'):
                instance.dict_attributes[k]=v
        return r

    def __str__(self):
        return '<'+self.name+' Object>'
    
    def __repr__(self) -> str:
        return self.__doc__

    def parametrized(self):
        return 0

class ParametrizedObject(Object):
    def __init__(self,name,echo,param):
        assert param in ('𝕋', "𝕂")
        self.param = param
        super().__init__(name,echo)

        self.methods_code =[]
        self.check = [default_types.B(True)]

    def add_method(self,code,obj):
        self.methods_code.append(code)
        super().add_method(code,obj)

    def right_parameter(self,p):
        if self.param == '𝕋':
            return True

        return p in ("𝒮","ℕ","ℤ","ℝ","ℂ",'𝔹')

    def __str__(self):
        return "<%s Object <%s>>"%(self.name,self.param)

    def __repr__(self):
        return self.__doc__

    def get_representant(self,p,objects):
        return RepresentParametrizedObject(self,p,objects)

    def __deepcopy__(self, memodict={}):
        res = ParametrizedObject(self.name, self.echo, self.param)
        res.methods = self.methods
        res.static_methods = self.static_methods
        res.methods_code = self.methods_code
        res.__doc__ = self.__doc__
        return res

    def parametrized(self):
        return 1

class RepresentParametrizedObject(Object):
    def __init__(self,obj:ParametrizedObject,param,objects):
        super().__init__(obj.name,obj.echo)
        self.obj=obj
        self.type=obj
        self.param = param
        self.objects = objects
        self.name = self.obj.name+'⟨'+stringify(param)+'⟩'

        for elt in obj.methods_code:
            self.add_method(elt.replace(self.obj.param,stringify(self.param)),objects)

    def __repr__(self):
        return "Instace<"+self.obj.__repr__()+'>'

    def __deepcopy__(self, memodict={}):
        res = RepresentParametrizedObject(self.obj, self.param, self.objects)
        res.__doc__ = self.__doc__
        return res

    def parametrized(self):
        return 2


class Instance:
    def __init__(self,typ:Object,var,dict,al,fct,obj,*val):
        assert type(typ)==Object or type(typ)==RepresentParametrizedObject or type(typ)==ParametrizedObject
        self.type=typ
        self.var_attributes={}
        self.dict_attributes={}

        self.g_var= {k:v for k,v in var.items() if v.glob}
        self.g_dict={k:v for k,v in dict.items() if v.glob}
        self.g_alias={k:v for k,v in al.items() if v.glob}
        self.g_fct=fct
        self.g_obj=obj

        self.call('start',*val)

        self.repr = "Instance of : "+self.type.name+'⟨'+';'.join([elt.__repr__() for elt in val])+'⟩'
    
    def get_type(self):
        return self.type.name
    
    def call(self,meth,*val):
        #ici: si meth est le nom d'un dict essayer de retourner la valeur à la clé fournie.
        if "me·"+meth in self.dict_attributes and len(val)==1:
            return self.dict_attributes["me·"+meth][val[0]]
        return self.type.call(meth,self,self.g_var,self.g_dict,self.g_alias,self.g_fct,self.g_obj,*val)

    def __repr__(self) -> str:
        return self.repr
    
    def __gt__(self,__o):
        return self.call('gt',__o).v

    def __str__(self) -> str:
        return self.call('stringify').value

    def __eq__(self, value: object) -> bool:
        return self.call('eq',value).v
    
    def __ge__(self,__o):
        return self.call('ge',__o).v
    
    def __ne__(self, value: object) -> bool:
        return self.call('neq',value).v
    
    def __le__(self, value: object) -> bool:
        return self.call('le',value).v
    
    def div(self, value: object) -> bool:
        return self.call('div',value)

    def __not__(self,value):
        return self.call('neg',value)

    def union(self,value):
        return self.call('union',value)

    def inter(self,value):
        return self.call('inter',value)

    def setminus(self,value):
        return self.call('setminus',value)

    def impl(self,value):
        return self.call('impl',value)

    def xor(self, other):
        return self.call('xor',other)

    def equiv(self,value):
        return self.call('equiv',value)

    def __ne__(self, value: object) -> bool:
        return self.call('ne',value).v

    def __hash__(self) -> int:
        return hash(self.type)

def valid_name_obj(name:str):
    if name == '' or ' ' in name:
        raise error.InvalidName(name)
    if name[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        raise error.InvalidName(name)
    if any(car not in 'abcdefghijklmnopqrstuvwxyz' for car in name[1:]):
        raise error.InvalidName(name)