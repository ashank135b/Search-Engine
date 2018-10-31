# Multi-frame tkinter application v2.2
import tkinter as tk

input = ""
output = ""

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
        self.master.geometry('200x85')
        start_label = tk.Label(self, text="Enter Text:")
        entry = tk.Entry(self)
        page_1_button = tk.Button(self, text="Submit",
                                  command=lambda: self.submit(entry.get(),master))
        start_label.pack(side="top", fill="x")
        entry.pack(side="top", fill="x")
        page_1_button.pack(side="bottom", fill="x")
    def submit(self, e ,master):
        if e != "":
            global input
            input += e
            master.switch_frame(PageOne)
        else:
            i = tk.Label(self, text='Type Something!!!!')
            i.pack()



class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master.title("App")
        self.master.geometry('200x200')

        '''
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side="right", fill="y")
        '''

        page_1_label = tk.Label(self, text="Output:")
        global input
        i = tk.Label(self, text=input)
        input = ""
        page_1_label.pack(side="top", fill="x", pady=10)
        i.pack(side="top", fill="x", pady=10)
        start_button = tk.Button(self, text="Back",
                                 command=lambda: master.switch_frame(StartPage))
        start_button.pack(side="bottom")


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()