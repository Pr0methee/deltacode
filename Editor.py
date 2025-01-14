import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext
import tkinter.ttk as ttk
from tkinter import *

import BaseEx
import _parser_
import compilator
import file
import os
import tools

FILES = [('Delta files', '.df')]


class App(Tk):
    def __init__(self):
        super().__init__()

        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)

        self.texts = {}

        self.F = True

        self.f1 = Frame(self)
        self.f1.grid(row=0, column=0, sticky=NSEW)

        self.file = Menubutton(self.f1, text="Fichier")

        menu = Menu(self.file)
        menu.add_command(label='Enregistrer Sous', accelerator="Ctrl+S", command=self.saveas)
        menu.add_command(label='Enregistrer', accelerator="Ctrl+s", command=self.save)
        menu.add_command(label='Nouveau', accelerator="Ctrl+n", command=self.new)
        menu.add_command(label='Ouvrir', accelerator="Ctrl+O", command=self.open)

        self.file.config(menu=menu)
        self.file.pack(side=LEFT)
        self.btn = Button(self.f1, text="Parse", command=self.parse)
        self.btn.pack(side=LEFT)
        self.comp = Button(self.f1, text="Compiler", command=self.compile)
        self.comp.pack(side=LEFT)
        self.run = Button(self.f1, text="Run", command=self.run)
        self.run.pack(side=LEFT)
        self.close_btn = Button(self.f1, text='x', command=self.close)
        self.close_btn.pack(side=RIGHT)
        self.new_window = Button(self.f1, text='+', command=self.new_tab)
        self.new_window.pack(side=RIGHT)

        self.clear = Button(self.f1, text='C', command=lambda : self.f3.clear())
        self.clear.pack(side=RIGHT)

        self.f2 = Frame(self, height=500)
        self.f2.grid(row=1, column=0, sticky=NSEW)

        self.notebook = ttk.Notebook(self.f2, height=750)
        self.notebook.pack(fill=BOTH, expand=True)

        self.new_tab()

        self.f3 = tools.Echo(self)
        self.f3.grid(row=2, column=0, sticky=EW)

        self.path = ''

    def new_tab(self, name='New File'):
        """
        lines = Label(self.notebook,width=10,height=500)
        lines.pack(side=TOP,expand=True,fill=Y)
        """

        text = scrolledtext.ScrolledText(self.notebook, cursor="xterm black", font=('Cambria', 14), height=500)
        text.pack(side=TOP, expand=True, fill=BOTH)
        text.update()

        """
        text=tools.NumberedScrolledText(self.notebook)
        text.pack()
        """

        text.bind("<Control-s>", self.save)
        text.bind("<Control-o>", self.open)
        text.bind("<Control-n>", self.new)
        text.bind("<Control-S>", self.saveas)
        text.bind("<period>", self.compile)
        text.bind("<Tab>",self.tab)

        text.tag_config('kw', foreground='#D4AF37')
        text.tag_config('t', foreground='#7d0d82')
        text.tag_config('v', foreground='#ff8040')
        text.tag_config('str', foreground='#329b2f')
        text.tag_config('n', foreground='#9191ff')
        text.tag_config('h', foreground='#008000')
        text.tag_config('intervalle', foreground='#A04000')
        text.tag_config('f', foreground='#804000')
        text.tag_config('label', foreground='#0080ff')
        text.tag_config('@', foreground='#808000')
        text.tag_config('comm', foreground='#455926')
        text.tag_config('op', foreground='#0000ff')
        text.tag_config('i', font=('Lucida Calligraphy', 12), foreground='#ff8040')

        lst = [self.notebook.tab(tab_index, "text") for tab_index in range(len(self.notebook.tabs()))]
        i = 1
        if name == 'New File':
            while name in lst:
                name = 'New File ' + str(i)
                i += 1

        self.notebook.add(text, text=name)

        last_tab_index = len(self.notebook.tabs()) - 1
        last_tab = self.notebook.tabs()[last_tab_index]
        self.texts[last_tab] = text
        self.notebook.select(last_tab)

    def tab(self,*_):
        ch = self.texts[self.notebook.select()].get("0.0","insert").split(' ')[-1]
        while ch!='' and ch[0]!='\\':
            ch=ch[1:]
        if ch=='':return
        r = compilator.complete(ch)
        if r =='':return

        txt=self.texts[self.notebook.select()].get("0.0","insert")
        while ch!= '':
            txt = txt[:-1]
            ch = ch[:-1]

        self.texts[self.notebook.select()].delete('0.0','insert')
        self.texts[self.notebook.select()].insert('0.0',txt+r)
        return 'break'


    def close(self):
        self.notebook.forget(self.notebook.select())
        if len(self.notebook.tabs()) == 0:
            self.new_tab()

        if self.notebook.tab(self.notebook.select(), 'text').startswith("New File"):
            self.path = ''
        else:
            self.path = self.notebook.tab(self.notebook.select(), 'text')

    def compile(self, *_):
        place = self.texts[self.notebook.select()].index(INSERT)
        if self.texts[self.notebook.select()].tag_ranges('i') != ():
            i = 0
            while i < len(self.texts[self.notebook.select()].tag_ranges('i')):
                self.texts[self.notebook.select()].replace(
                    self.texts[self.notebook.select()].tag_ranges('i')[i],
                    self.texts[self.notebook.select()].tag_ranges('i')[i + 1],
                    '\i')

        t = self.texts[self.notebook.select()].get(0.0, END)
        t = t.replace('\r', '')
        t = compilator.compile(t)
        while len(t) != 0 and t[-1] == '\n':
            t = t[:-1]
        t += '\n'

        self.texts[self.notebook.select()].delete(0.0, END)
        self.texts[self.notebook.select()].insert(END, t)
        self.texts[self.notebook.select()].mark_set(INSERT, place)

        self.colorize()

    def parse(self):
        self.compile()
        r = (_parser_.parse(self.texts[self.notebook.select()].get(0.0, END)))
        print(r)

    def colorize(self):
        compilator.colorise(self.texts[self.notebook.select()])

    def run(self):
        self.compile()
        if self.path == '':
            messagebox.showinfo("Run", "You should save your code before running it.")
            self.saveas()
            if self.path == '':
                return
        else:
            self.save()

        os.chdir(os.path.dirname(self.path))
        var = "Running file : " + self.path
        self.f3.informe_sec(f"{var:=^80}" + '\n')
        if os.path.splitext(self.path)[1] == '.df':
            ex = BaseEx.Executor(self.f3)
            nom = self.path.split('/')[-1].split('.')[0]
            ex.execute(self.texts[self.notebook.select()].get(0.0, END),
                       name=nom)
        self.f3.informe_sec("=" * 10 + "End" + "=" * 10 + '\n')

    def saveas(self, *_):
        self.compile()
        f = filedialog.asksaveasfilename(defaultextension='.df', filetypes=FILES)
        if f == '': return
        r = os.path.splitext(f)
        if r[1] == '':
            f += '.df'
        self.path = f
        self.write()
        self.notebook.tab(self.notebook.select(), text=self.path)

    def save(self, *_):
        if self.path == '':
            self.saveas()
            return
        self.compile()
        self.write()

    def write(self):
        file.save_text(self.path, compilator.decompile(
            self.texts[self.notebook.select()].get(0.0, END)))

    def open(self, *_):
        f = filedialog.askopenfilename(defaultextension='.df', filetypes=FILES)
        if f == '': return
        self.path = f
        self.new_tab(self.path)
        r = file.get_text(self.path)
        self.texts[self.notebook.select()].insert(END, r)
        self.compile()
        self.update()

    def new(self, *_):
        rep = messagebox.askyesno("New page", "Do you want to save before cleanning ?")
        if rep: self.save()
        self.new_tab()


if __name__ == '__main__':
    app = App()
    app.mainloop()
