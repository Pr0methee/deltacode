from default_functions import F

def isfloat(ch:str):
    try:
        float(ch)
        return True
    except:
        return False

table = {
    "\exists ":"∃ ",
    "\in ":"∊ ",
    "\\forall ":"∀ ",
    '\empty':"∅ ",
    "\include ":"⊆ ",
    '\S':"ϩ",
    '\\N':"ℕ",
    '\\Z':"ℤ",
    '\\R':"ℝ",
    '\\C':"ℂ",
    '\\B':'ℬ',
    "\False":'⊥',
    "\True":"⊤",
    "\i":'ι',
    '\div':'÷',
    '\mul':'×',
    '\\to':'↦',
    '\\P':chr(8472)
}

def compile(text:str):
    for k,v in table.items():
        text =text.replace(k,v)
    return text

def colorise(text:str):
    c,l=0,3
    d={'kw':[],'t':[],'v':[],'str':[],'n':[],'label':[],'B':[],'h':[],'i':[],'f':[],'intervalle':[]}
    s,h,i=False,False,False
    mot=''
    for i in range(len(text)) :
        car= text[i]
        if car =='|' and (i+1<len(text) and text[i+1]=='['):
            i=True
        if car =='\n':
            if isfloat(mot.replace(',','.').replace('ι','')):
                index = 'n'
            elif mot in F:
                index='f'
            elif mot:
                index='label'
            for i,k in enumerate(mot):
                d[index].append((l,c-len(mot)+i))
            c=0
            l+=1
        else:
            c+=1

        if not s and not h and not i:    
            if car.isalnum() or car in ',;?!\'':
                mot+=car
            else:
                if isfloat(mot.replace(',','.').replace('ι','')):
                    index = 'n'
                elif mot in F:
                    index='f'
                else:
                    index='label'
                for i,k in enumerate(mot):
                    d[index].append((l,c-len(mot)+i))
                mot=''

        if h:
            d['h'].append((l,c))
        elif s:
            d['str'].append((l,c))
        elif i:
            d['intervalle'].append((l,c))
        elif car in ('∃','∀','∊','⊆'):
            d['kw'].append((l,c))
            mot=''
        elif car in ("ϩ","ℕ","ℤ","ℝ","ℂ",'ℬ'):
            d['t'].append((l,c))
            mot=''
        elif car in ('⊥',"⊤",'∅'):
            d['v'].append((l,c))
            mot=''
        
        if car == '#':
            h=not h
            d['h'].append((l,c))
        elif car =='"':
            s=not s
            d['str'].append((l,c))
        elif car == 'ℬ':
            d['B'].append((l,c))
            mot=''
        elif car == 'ι':
            d['i'].append((l,c))
            mot=''         
            
        if car =='|' and (0<=i-1 and text[i-1]==']'):
            i=False
            


    
    c+=1
    if isfloat(mot.replace(',','.').replace('ι','')):
        index = 'n'
    elif mot in F:
        index='f'
    elif mot:
        index='label'
    for i,k in enumerate(mot):
        d[index].append((l,c-len(mot)+i))
    mot=''
    if (l,c) in d['str']:d['str'].remove((l,c))
    return d
