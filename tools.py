from tkinter import *
import tkinter.scrolledtext as scrolledtext


class Echo(Frame):
    def __init__(self,master):
        super().__init__(master,bg='gray',height=100)
        self.left =Frame(self)
        self.left.pack(side=LEFT,expand=True,fill=BOTH)
        Label(self.left,text='RETOUR D\'EXECUTION :',fg='#39FF14',bg='black',font=('Terminal',11,'bold'),height=1).pack(pady=0,side=TOP,expand=True,fill=X)
        self.exec = scrolledtext.ScrolledText(self.left,bg='black',fg='#39FF14',cursor="xterm black",insertbackground = '#39FF14',height=10)
        self.exec.insert(END,chr(8422))
        self.exec.config(state='disabled')
        self.exec.pack(pady=0,side=BOTTOM,expand=True,fill=X)
        self.exec.tag_config("err",foreground='red')
        self.exec.tag_config("inf",foreground='white')
        
        self.right =Frame(self)
        self.right.pack(side=RIGHT,expand=True,fill=BOTH)
        Label(self.right,text='INFORMATIONS :',fg='orange',bg='black',font=('Terminal',11,'bold'),height=1).pack(pady=0,side=TOP,expand=True,fill=X)
        self.inf = scrolledtext.ScrolledText(self.right,bg='black',fg='#39FF14',cursor="xterm black",insertbackground = '#39FF14',height=10)
        self.inf.insert(END,chr(8422))
        self.inf.config(state='disabled')
        self.inf.pack(pady=0,side=BOTTOM,expand=True,fill=X)
        self.inf.tag_config("err",foreground='red')
        self.inf.tag_config("dec",foreground='orange')
        self.inf.tag_config("inf",foreground='white')

        self.active=True
    
    def raise_error(self,err):
        self.exec.config(state='normal')
        self.exec.insert('end',err,'err')
        self.exec.config(state='disabled')

        self.inf.config(state='normal')
        self.inf.insert('end',err,'err')
        self.inf.config(state='disabled')
    
    def declare(self,statement):
        self.inf.config(state='normal')
        self.inf.insert('end',statement,'dec')
        self.inf.config(state='disabled')

    def informe_main(self,statement):
        self.exec.config(state='normal')
        self.exec.insert('end',statement,'inf')
        self.exec.config(state='disabled')

    def informe_sec(self,statement):
        self.inf.config(state='normal')
        self.inf.insert('end',statement,'inf')
        self.inf.config(state='disabled')

    def clear(self):
        self.exec.config(state='normal')
        self.exec.delete("0.0",END)
        self.exec.config(state='disabled')
        
        self.inf.config(state='normal')
        self.inf.delete("0.0",END)
        self.inf.config(state='disabled')



class StdRedirector:
    def __init__(self, text_widget:Echo):
        self.text_widget = text_widget.exec
        self.ok = False

    def write(self, message):#enlever le disabled
        self.text_widget.config(state='normal')
        self.text_widget.insert(END,message)
        self.text_widget.see(END)
        self.text_widget.config(state='disabled')
        
    def go(self,*args):
        self.ok=True

    def readline(self,*args):
        end =self.text_widget.index(str(self.last_line())+'.end')
        self.text_widget.config(state='normal')
        self.text_widget.bind('<Return>',self.go)
        while not self.ok:
            self.text_widget.master.update()
        self.text_widget.update()
        self.text_widget.update_idletasks()
        self.text_widget.config(state='disabled')
        return self.text_widget.get(end,'end-1c')
    
    def last_line(self):
        l=self.text_widget.index('end').split('.')[0]
        l=int(l)-1
        return l
