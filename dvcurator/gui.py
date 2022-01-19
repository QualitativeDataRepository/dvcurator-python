
def find_config():
	from tkinter import filedialog
	config = filedialog.askopenfilename()
	config_label.configure(text="Config file: " + config)


import tkinter as tk
root=tk.Tk()
#root.geometry('300x50')
root.title("dvcurator")

doi=tk.StringVar()
config=tk.StringVar()

doi_label = tk.Label(root, text="Persistent ID (DOI)")
doi_entry = tk.Entry(root, textvariable=doi)
config_label = tk.Label(root, text="Config file")
config_entry = tk.Button(root, text="Select folder", command=find_config)

config_label.grid(column=2, row=1)
config_entry.grid(column=1, row=1)
doi_label.grid(column=2, row=2)
doi_entry.grid(column=1, row=2)

quit = tk.Button(root, text="Exit", command=root.quit)
quit.grid(column=2, row=3)

root.mainloop()
