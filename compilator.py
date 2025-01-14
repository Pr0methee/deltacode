#coding : utf-8
with open('dcache/default_functions.txt','r') as f:
    DEFAULT_FUNCTIONS=f.read().splitlines()

def isfloat(ch:str):
    try:
        float(ch)
        return True
    except:
        return False
#div euclidienne : '├'
op=("⊆","∊",'÷','×','∧','∨','¬','⇒','⊕','⇔','≠','⩾','⩽',"⋂","⋃",'∖','+','=','^','-','|')
table = {
    "\\exists":"∃",
    "\\in":"∊",
    "\\forall":"∀",
    '\\empty':"∅",
    "\\include":"⊆",
    '\\S':"𝒮",
    '\\N':"ℕ",
    '\\Z':"ℤ",
    '\\R':"ℝ",
    '\\C':"ℂ",
    '\\B':"𝔹",
    "\\False":'⊥',
    "\\True":"⊤",
    "\\i":'ι',
    '\\div':'÷',
    '\\mul':'×',
    '\\mapsto':'⟼',
    '\\to':'⟶',
    '\\nexists':'∄',
    '\\P':chr(8472),#P tq P(N) désigne l'ensemble des parties de N
    '\\land':'∧',
    '\\lor':'∨',
    '\\lnot':'¬',
    '\\limpl':'⇒',
    '\\xor':'⊕',
    '\\equiv':'⇔',
    '|[':'⟦',
    ']|':'⟧',
    '\\nes':'□',
    ':=':'≔',
    '\\neq':'≠',
    '\\ge':'⩾',
    '\\le':'⩽',
    '\\Re':"ℜ",
    '\\Im':"ℑ",
    '\\dict':'⇴',
    '\\Omega':'Ω',
    '\\aleph':'ℵ₀',
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
    '\\case':'➣',
    '\\do':'⇝',
    '\\alias':'≜',
    "\\inter":"⋂",
    "\\union":"⋃",
    '\\(':'⟨',
    '\\)': '⟩',
    '\\setminus':'∖',
    '\\midpoint':'·',
    '\.':'·',
    '\\F':'ℱ',
    '\\D':'𝒟',
    "\\T":'𝕋',
    "\\K":"𝕂",
    '\\inherit':'⊃',
    '\st':'│'
}

def decompile(text:str):
    for k,v in table.items():
        text=text.replace(v,k)
    return text

def compile(text:str):
    K = list(table.keys())
    K=sorted(K,key=len,reverse=True)
    for k in K:
        v=table[k]
        text =text.replace(k,v)
    return text

def colorise(text):
    c,l=0,1
    #d={'kw':[],'t':[],'v':[],'str':[],'n':[],'label':[],'B':[],'h':[],'i':[],'f':[],'intervalle':[],'@':[],'comm':[],'op':[]}
    s,h,iz,ir,hide,com=False,False,False,False,False,False
    mot=''
    while str(l)+'.'+str(c) != text.index("end"):
        while str(l)+'.'+str(c) != text.index(str(l)+".end"):
            ind = str(l)+'.'+str(c)
            car= text.get(ind)

            if car == '𝒟':
                text.delete(ind)
                text.insert(ind,'𝒟','label')
                c+=1
                continue

            if car == '𝕋' and not h:
                text.delete(ind)
                text.insert(ind,'𝕋','t')
                c+=1
                continue

            if car == '𝕂' and not h:
                text.delete(ind)
                text.insert(ind,'𝕂','t')
                c+=1
                continue


            if car =='%' and not s and not h:
                com=True
            if car =='⟦' and not s and not h:
                iz=True
            if (car == '@' or car =='&') and not s and not h:
                hide=True

            if not s and not h and not iz and not ir and not com:    
                if car.isalnum() or car in "_',":
                    mot+=car
                else:
                    if isfloat(mot.replace(',','.').replace('ι','')):
                        index = 'n'
                    elif mot in DEFAULT_FUNCTIONS:
                        index='f'
                    else:
                        index='label'
                    for j,k in enumerate(mot):
                        text.tag_add(index,str(l)+'.'+str(c-len(mot)+j))
                        #d[index].append(str(l)+'.'+str(c-len(mot)+j))
                    mot=''

            if h:
                text.tag_add('h',ind)
            elif s:
                text.tag_add('str',ind)
            elif com:
                text.tag_add('comm',ind)
            elif iz or ir:
                text.tag_add('intervalle',ind)
            elif car in ('∃','∀','∊','⊆','≔','⇝','➣','□','∄','≜','⊃','│'):
                text.tag_add('kw',ind)
                mot=''
            elif car in ("𝒮","ℕ","ℤ","ℝ","ℂ",'𝔹','Ω'):
                text.tag_add('t',ind)
                mot=''
            elif car in ('⊥',"⊤",'∅'):
                text.tag_add('v',ind)
                mot=''
            elif car in op and not s:
                text.tag_add('op',ind)
            if car == '#'  and not com and not s:
                h=not h
                text.tag_add('h',ind)
            elif car =='"' and not com and not h:
                s=not s
                text.tag_add('str',ind)
            elif car == 'ι' and not s and not h and not com:
                text.tag_add('i',ind)
                mot='' 
            elif hide:
                text.tag_add('@',ind)       
                
            if car =='⟧' and iz:
                iz=False   
            c+=1
        l+=1
        c=0 
        hide,com=False,False    
    
    l-=2
    c = int(text.index(str(l)+'.end').split('.')[1])
    if isfloat(mot.replace(',','.').replace('ι','')):
        index = 'n'
    elif mot in DEFAULT_FUNCTIONS:
        index='f'
    else:
        index='label'
    for j,k in enumerate(mot):
        text.tag_add(index,str(l)+'.'+str(c-len(mot)+j))

def complete (last):
    if last=='':return ''
    l=[]
    for elt in table.keys():
        if elt.startswith(last):
            l.append(elt)

    if len(l)==1:
        return l[0]
    return ''