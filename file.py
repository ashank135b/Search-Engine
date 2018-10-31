import math
import pickle
from operator import itemgetter

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


def query_rank(document, query):
    """
    :return: cosine distance between document and query
    :rtype:float
    :type query: dict
    :type document: dict
    """
    sumxx = 0
    sumyy = 0
    sumxy = 0
    for term in idf.keys():
        sumxx += document[term] * document[term]
        sumyy += query[term] * query[term]
        sumxy += query[term] * document[term]
    try:
        return float(sumxy) / math.sqrt(sumxx * sumyy)
    except Exception:
        return 0.0


def return_list(query):
    """

    :type query: string
    :return: sorted dictionary of story titles and corresponding data
    :rtype:dict
    """
    query_vec = query_vector(query)
    output = {}
    outputdata = {}
    i = 1
    for story in data.keys():
        output[story] = query_rank(data[story]['tf'], query_vec)
        outputdata[story] = {"index": data[story]['index'], "genre": data[story]['genre']}
        print(i)
        i += 1
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


class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master.title("App")
        self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        start_label = tk.Label(self, text="Enter Text:")
        entry = tk.Entry(self)
        page_1_button = tk.Button(self, text="Submit",
                                  command=lambda: self.submit(entry.get(), master))
        start_label.pack(side="top", fill="x")
        entry.pack(side="top", fill="x")
        page_1_button.pack(side="bottom", fill="x")

    def submit(self, e, master):
        if e != "":
            i = tk.Label(self, text='Loading.....')
            i.pack(side="bottom")
            global input
            input += e
            master.switch_frame(PageOne)
        else:
            i = tk.Label(self, text='Type Something!!!!')
            i.pack()


Selected_novel = ()


class PageOne(tk.Frame):
    def __init__(self, master):
        global input
        global final_output
        final_output = return_list(input)
        output = final_output[0]
        print(output[0][1])

        tk.Frame.__init__(self, master)
        self.master.title("App")
        self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth(), self.master.winfo_screenheight()))

        page_1_label = tk.Label(self, text="Output:")
        page_1_label.pack(side="top", fill="x", pady=10)
        i = 0
        for out in output:
            if i == 5 or out[1] == 0:
                break
            print(out[0])
            b = tk.Button(self, text=out[0], command=lambda: self.switch(master, out))
            b.pack(side="top", fill="x", pady=10)
            i += 1
        print(final_output)
        input = ""
        start_button = tk.Button(self, text="Back",
                                 command=lambda: self.BACK(master))
        start_button.pack(side="bottom")

    def BACK(self, master):
        global final_output
        final_output = {}
        return master.switch_frame(StartPage)

    def switch(self, master, out):
        global Selected_novel
        Selected_novel = out
        return master.switch_frame(Selected_Page)


class Selected_Page(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master.title("App")
        #self.master.geometry('1000x1000')
        self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        #self.master.bind('<Escape>', self.toggle_geom)
        global final_output
        print(final_output)
        global text

        ans = tk.Label(self, text=text[6 * final_output[1][Selected_novel[0]]['index'] + 6], wraplength=1000)
        ans.pack(side='top')
        start_button = tk.Button(self, text="Search another word!!!",
                                 command=lambda: master.switch_frame(StartPage))
        start_button.pack(side="bottom")


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
