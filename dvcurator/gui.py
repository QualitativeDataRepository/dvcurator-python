
def find_dropbox():
	from tkinter import filedialog
	dropbox = filedialog.askdirectory()
	dropbox_label.configure(text="Dropbox: " + dropbox)


import tkinter as tk
root=tk.Tk()
#root.geometry('600x400')
dv_token=tk.StringVar()
dropbox=tk.StringVar()

dv_label = tk.Label(root, text="Dataverse token")
dv_entry = tk.Entry(root, textvariable=dv_token)
dropbox_label = tk.Label(root, text="Dropbox folder")
dropbox_entry = tk.Button(root, text="Select folder", command=find_dropbox)

dropbox_label.grid(column=2, row=1)
dropbox_entry.grid(column=1, row=1)
dv_label.grid(column=2, row=2)
dv_entry.grid(column=1, row=2)

root.mainloop()
