import zipfile,os,json

def create(path,name):
    with open(name+'.txt','x')as f:
        pass

    with open(name+'.json','x')as f:
        pass

    with zipfile.ZipFile(path+'.df', 'w') as zipf:
        zipf.write(name+'.txt')
        zipf.write(name+'.json')
    
    os.remove(name+'.txt')
    os.remove(name+'.json')

def save_text(path,name,text):
    with zipfile.ZipFile(path+'.df', 'r') as zipf: 
        file = zipf.extract(name+'.json','')
    with open(name+'.txt','w',encoding='utf-8') as f:
        f.write(text)
    
    with zipfile.ZipFile(path+'.df', 'w') as zipf:
        zipf.write(name+'.txt')
        zipf.write(name+'.json')

    os.remove(name+'.txt')
    os.remove(file)
    
def save_json(name,jsonfile):
    with zipfile.ZipFile(name+'.df', 'r') as zipf: 
        file = zipf.extract(name+'.txt','')
    
    with zipfile.ZipFile(name+'.df', 'w') as zipf:
        zipf.write(jsonfile)
        zipf.write(file)

    os.remove(jsonfile)
    os.remove(file)

def get_text(path,name):
    with zipfile.ZipFile(path+'.df', 'r') as zipf: 
        file = zipf.read(name+'.txt').decode()
    
    return file

def get_json(name):
    with zipfile.ZipFile(name+'.df', 'r') as zipf: 
        file = zipf.extract(name+'.json','')
    try:
        with open(file,'r') as f:
            data=json.load(f)
    except json.decoder.JSONDecodeError:
        data='Unexpected result'
    os.remove(file)
    return data