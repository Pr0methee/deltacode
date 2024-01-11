from default_functions import F

def isfloat(ch:str):
    try:
        float(ch)
        return True
    except:
        return False
#div euclidienne : '├'
#necessaire / possible : '⬜'/'⬨'
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
    '\\P':chr(8472),#P tq P(N) désigne l'ensemble des parties de N
    '\land':'∧',
    '\lor':'∨',
    '\\lnot':'¬',
    '\limpl':'⇒',
    '\\xor':'⊕',
    '\equiv':'⇔',
    '|[':'⟦',
    ']|':'⟧',
    '\\nes':'□',
    '\pos':'◊',
    ':=':'≔',
    '\\neq':'≠',
    '\ge':'⩾',
    '\le':'⩽',
    '\Re':"ℜ",
    '\Im':"ℑ",
    '\\app':'↠',
    '\Omega':'Ω',
    '\\aleph':'ℵ₀',
    '\eucl':'├',
    '_0':'₀',
    '_1':'₁',
    '_2':'₂',
    '_3':'₃',
    '_4':'₄',
    '_5':'₅',
    '_6':'₆',
    '_7':'₇',
    '_8':'₈',
    '_9':'₉',
    '\case':'➣',
    '\\do':'⇝'

}

"""

→↣⇝
⇢⇥⇨⇸⇻⇾
⤀⤁⤍⤏⤐⤑⤔⤕⤖⤗⤘⤞⤠
⇥
"""



def compile(text:str):
    K = list(table.keys())
    K=sorted(K,key=len,reverse=True)
    for k in K:
        v=table[k]
        text =text.replace(k,v)
    return text

def colorise(text:str):
    c,l=0,2
    d={'kw':[],'t':[],'v':[],'str':[],'n':[],'label':[],'B':[],'h':[],'i':[],'f':[],'intervalle':[],'@':[],'comm':[]}
    s,h,iz,ir,hide,com=False,False,False,False,False,False
    mot=''
    for j in range(len(text)) :
        car= text[j]
        if car =='%' and not s :
            com=True
        if car =='⟦' and not s:
            iz=True
        if car  == '[' and not s:
            ir=True
        if car == '@' and not s:
            hide=True

        
        if car =='\n':
            if hide:
                hide=False
            elif com:
                d['comm'].append((l,c))
                com=False
            else:
                if isfloat(mot.replace(',','.').replace('ι','')):
                    index = 'n'
                elif mot in F:
                    index='f'
                elif mot:
                    index='label'
                for j,k in enumerate(mot):
                    d[index].append((l,c-len(mot)+j))
            c=0
            l+=1
        else:
            c+=1

        if not s and not h and not iz and not ir and not com:    
            if car.isalnum():
                mot+=car
            else:
                if isfloat(mot.replace(',','.').replace('ι','')):
                    index = 'n'
                elif mot in F:
                    index='f'
                else:
                    index='label'
                for j,k in enumerate(mot):
                    d[index].append((l,c-len(mot)+j))
                mot=''

        if h:
            d['h'].append((l,c))
        elif s:
            d['str'].append((l,c))
        elif com:
            d['comm'].append((l,c))
        elif iz or ir:
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
        elif car == 'ι':
            d['i'].append((l,c))
            mot='' 
        elif hide:
            d['@'].append((l,c))        
            
        if car =='⟧' and iz:
            iz=False
        if car == ']' and ir:
            ir=False 
            


    
    c+=1
    if isfloat(mot.replace(',','.').replace('ι','')):
        index = 'n'
    elif mot in F:
        index='f'
    elif mot:
        index='label'
    for j,k in enumerate(mot):
        d[index].append((l,c-len(mot)+j))
    mot=''
    if (l,c) in d['str']:d['str'].remove((l,c))
    return d
