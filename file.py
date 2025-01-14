import zipfile,os

def save_text(path,text):
    with open(path,'w') as f:
        f.write(text)

def get_text(path):
    with open(path,'r') as f:
        return f.read()