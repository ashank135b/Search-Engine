import math
import pickle
from operator import itemgetter
from Trie import Trie
import numpy as np
from tkinter import *
import re
from tkinter.ttk import Progressbar

import nltk
from nltk.stem.snowball import SnowballStemmer

# Multi-frame tkinter application v2.2
import tkinter as tk

input = ""
final_output = {}

stemmer = SnowballStemmer(language="english", ignore_stopwords=True)

with open("storevec.txt", "rb") as myFile:
    data = pickle.load(myFile)
with open("storeidf.txt", "rb") as myFile:
    idf = pickle.load(myFile)
with open("storedata.txt", "rb") as myFile:
    text = pickle.load(myFile)
with open("storewords.txt", "rb") as myFile:
    all_words = pickle.load(myFile)


def percentageCalculator(x, y):
    return x * 1.0 / y * 100


def query_vector(query):
    """
    :rtype:dict
    :return: vector representing query
    :type query: String
    """
    vec = {}
    tokens = nltk.word_tokenize(query)
    tokens = [stemmer.stem(token.lower()) for token in tokens if token.isalnum()]
    N = len(tokens)
    d = {token: tokens.count(token) / float(N) for token in tokens}
    for key in idf.keys():
        if key in d.keys():
            vec[key] = idf[key] * d[key]
        else:
            vec[key] = 0
    return vec


def normalize(query):
    magnitude = sum(query[k] * query[k] for k in idf.keys())
    return dict((k, query[k] / magnitude) for k in idf.keys())


def query_rank(document, query):
    """
    :return: cosine distance between document and query
    :rtype:float
    :type query: dict
    :type document: dict
    """

    sumxx = sum(document[k] * document[k] for k in idf.keys())
    sumyy = sum(query[k] * query[k] for k in idf.keys())
    sumxy = sum(document[k] * query[k] for k in idf.keys())
    # for term in idf.keys():
    #   sumxx += document[term] * document[term]
    #   sumyy += query[term] * query[term]
    #   sumxy += query[term] * document[term]
    try:
        return float(sumxy) / math.sqrt(sumxx * sumyy)
    except Exception:
        return 0.0


def return_list(master, query):
    """

    :param master: master
    :type query: string
    :return: sorted dictionary of story titles and corresponding data
    :rtype:dict
    """
    query_vec = query_vector(query)
    output = {}
    outputdata = {}
    i = 1

    for story in data.keys():
        unit = percentageCalculator(i, 1000)
        step = "Working on {}...".format(i)
        # log.write(str('\n[OK]'))
        master.progress['value'] = unit
        master.percent['text'] = "{:.1f}%".format(unit)
        master.status['text'] = "{}".format(step)

        output[story] = query_rank(data[story]['tf'], query_vec)
        outputdata[story] = {"index": data[story]['index'], "genre": data[story]['genre']}
        print(i)
        i += 1
        master.update()

    # output = dict((k,query_rank(data[k]['tf'],query=query_vec)) for k in data.keys())
    # outputdata = dict((k,{"index":data[k]['index'],'genre':data[k]['genre']}) for k in data.keys())
    return sorted(output.items(), key=itemgetter(1), reverse=True), outputdata


class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


Selected_novel = ""


class AutocompleteEntry(Entry):
    def __init__(self, lista, *args, **kwargs):

        Entry.__init__(self, *args, **kwargs)
        self.lista = lista
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)

        self.lb_up = False

    def changed(self, name, index, mode):

        if self.var.get() == '':
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.lb_up = True

                self.lb.delete(0, END)
                for w in words:
                    self.lb.insert(END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):

        if self.lb_up:
            self.var.set(self.lb.get(ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(END)

    def up(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':
                self.lb.selection_clear(first=index)
                index = str(int(index) - 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def down(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != END:
                self.lb.selection_clear(first=index)
                index = str(int(index) + 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        pattern = re.compile('.*' + self.var.get() + '.*')
        return [w for w in self.lista if re.match(pattern, w)]


class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master.title("App")
        # self.master.geometry("{0}x{1}+0+0".format(
        #   self.master.winfo_screenwidth(), self.master.winfo_screenheight()))

        # self.cb = tk.Label(self, font=("Arial", 15), text="button changes here...")
        global all_words
        self.start_label = tk.Label(self, font=("Arial", 15), text="Enter Text to search:")
        self.entry = AutocompleteEntry(all_words, self)

        """bottomframe=tk.Frame
        bottomframe.pack(self, side= "bottom")"""
        self.page_1_search = tk.Button(self, text="Search",
                                       command=lambda: self.submit(self.entry.get(), master))
        # self.page_1_advsearch = tk.Button(self, text="Advanced Search",
        # command=lambda: self.advsubmit(self.entry.get(), master))

        self.start_label.pack(padx=(10, 200), pady=(100, 0), side="top", fill="x")
        self.entry.pack(padx=(10, 30), pady=(10, 20), ipady=3, side="top", fill="x")
        self.page_1_search.pack(padx=(0, 30), pady=(0, 100), anchor='se')
        # self.page_1_advsearch.pack(side="left")
        # self.cb.pack()
        self.percent = tk.Label(self, text="00.0%", width=5, relief='sunken', anchor='se')
        self.progress = Progressbar(self, length=250, mode='determinate')
        self.status = tk.Label(self, text="progress tracker", relief='sunken', anchor='sw')

        self.percent.pack(side='left')
        self.progress.pack(side='left')
        self.status.pack(side='left')

    def submit(self, e, master):

        print('entered button')
        if e != "":
            self.page_1_search['state'] = 'disabled'
            global input
            input += e

            global final_output
            final_output = return_list(self, input)

            output = final_output[0]

            if output[0][1] == 0:
                tk.messagebox.showinfo('Oops!!', "nothing to display !!")
                self.page_1_search['state'] = 'normal'
                input = ""
            else:
                master.switch_frame(PageOne)
        else:
            tk.messagebox.showinfo('Info', "type something!!")

    '''def advsubmit(self, e, master):
        if e != "":
            i = tk.Label(self, text='Loading.....')
            i.pack(side="bottom")
            global input
            input += e
            master.switch_frame(PageOne)
        else:
            i = tk.Label(self, text='Type Something!!!!')
            i.pack()'''


class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master.title("App")
        '''global input
        global final_output
        final_output = return_list(input)'''
        output = final_output[0]
        print(output[0][1])

        page_1_label = tk.Label(self, text="Output:")
        page_1_label.pack(side="top", fill="x", pady=10)

        if output[0][1] != 0:
            b1 = tk.Button(self, text=output[0][0], command=lambda: self.switch(master, output[0][0]))
            b1.pack(side="top", fill="x", padx=(70, 70), pady=10)
        if output[1][1] != 0:
            b2 = tk.Button(self, text=output[1][0], command=lambda: self.switch(master, output[1][0]))
            b2.pack(side="top", fill="x", padx=(70, 70), pady=10)
        if output[2][1] != 0:
            b3 = tk.Button(self, text=output[2][0], command=lambda: self.switch(master, output[2][0]))
            b3.pack(side="top", fill="x", padx=(70, 70), pady=10)
        if output[3][1] != 0:
            b4 = tk.Button(self, text=output[3][0], command=lambda: self.switch(master, output[3][0]))
            b4.pack(side="top", fill="x", padx=(70, 70), pady=10)
        if output[4][1] != 0:
            b5 = tk.Button(self, text=output[4][0], command=lambda: self.switch(master, output[4][0]))
            b5.pack(side="top", fill="x", padx=(70, 70), pady=10)

        start_button = tk.Button(self, text="Back",
                                 command=lambda: self.BACK(master))
        start_button.pack(side="bottom", pady=50)

    def BACK(self, master):
        global final_output
        final_output = {}
        global input
        input = ""
        return master.switch_frame(StartPage)

    def switch(self, master, out):
        global Selected_novel
        print(out)
        Selected_novel = out
        return master.switch_frame(Selected_Page)


class Selected_Page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master.title("App")
        # self.master.geometry('1000x1000')
        '''self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth(), self.master.winfo_screenheight()))'''
        # self.master.bind('<Escape>', self.toggle_geom)
        global final_output
        global text
        global Selected_novel

        txt = text[6 * final_output[1][Selected_novel]['index'] + 6]
        # self.ans = tk.Label(self, relief='sunken', height=50, text=' ', wraplength=500)



        self.frm = tk.Frame(self)
        self.scrollbarV = tk.Scrollbar(self.frm, orient='vertical')
        self.scrollbarH = tk.Scrollbar(self.frm, orient='horizontal')
        self.txtItem = tk.Text(self.frm, wrap='word', yscrollcommand=self.scrollbarV.set,
                               xscrollcommand=self.scrollbarH.set,
                               relief='sunken', takefocus=0, borderwidth=1, state='normal', cursor='arrow')
        self.txtItem.grid(row=5, column=0, columnspan=7, sticky='n' + 'w' + 's' + 'e')

        self.scrollbarV.grid(row=5, column=7, sticky='n' + 's')
        self.scrollbarV.config(command=self.txtItem.yview)
        self.scrollbarH.grid(row=6, column=0, columnspan=7, sticky='e' + 'w')
        self.scrollbarH.config(command=self.txtItem.xview)

        self.txtItem.config(state='normal')
        self.txtItem.delete(1.0, 'end')
        self.txtItem.insert('insert', txt)
        # self.txtItem.insert(INSERT, rss_item.link, 'a')
        self.txtItem.config(state='disabled')

        self.story_label = tk.Label(self, font=("Arial", 15), text=Selected_novel + ":")
        global input
        inputstr = input.split(' ')
        with open("storetrie.txt", "rb") as myFile:
            trie = pickle.load(myFile)

        start = 1.0

        inputstr += [inp.capitalize() for inp in inputstr]
        inputstr += [inp.lower() for inp in inputstr]
        print(inputstr)
        all_words = []
        for inp in inputstr:
            all_words += list(trie.all_words_beginning_with_prefix(inp))
        all_words = sorted(all_words, reverse=True)

        print(all_words)
        for word in all_words:
            print(word)
            pos = self.txtItem.search(word, start, stopindex='end')
            while pos:
                length = len(word)
                row, col = pos.split('.')
                end = int(col) + length
                end = row + '.' + str(end)
                self.txtItem.tag_add('highlight', pos, end)
                start = end
                pos = self.txtItem.search(word, start, stopindex='end')
            self.txtItem.tag_config('highlight', background='white', foreground='red')

        # self.ans.pack(side='top',pady=50)
        self.story_label.pack(side='top')
        self.frm.pack(side='top')
        start_button = tk.Button(self, text="Search another word!!!",
                                 command=lambda: self.switch(master))
        start_button.pack(side='right', padx=20, pady=20)

        back_button = tk.Button(self, text="Back",
                                command=lambda: self.back(master))
        back_button.pack(side="right", padx=10, pady=20)

    def switch(self, master):
        global input
        input = ""
        global Selected_novel
        self.txtItem.delete(1.0, 'end')
        Selected_novel = ""
        return master.switch_frame(StartPage)

    def back(self, master):
        global Selected_novel
        self.txtItem.delete(1.0, 'end')
        Selected_novel = ""
        return master.switch_frame(PageOne)


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
