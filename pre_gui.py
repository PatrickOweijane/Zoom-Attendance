import tkinter as tk
from tkinter import filedialog

from PIL import ImageTk, Image

import os

from pathlib import Path

app_icon_path = Path('./Icons/App Icon.ico')
app_name = 'Attendance Tool'

def main(attendance_path, history_path, reference_path, open_files, percentage_of_duration):
	def browse_attendance(event):
		directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Select the Attendance Folder")
		if directory:
			attendance_path_display.configure(text=directory)
	

	def browse_history(event):
		directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Select the History Folder")
		if directory:
			history_path_display.configure(text=directory)
	

	def browse_reference(event):
		directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Select the Reference Folder")
		if directory:
			reference_path_display.configure(text=directory)


	def start_program(event):
		global attendance_path_returned
		global history_path_returned
		global reference_path_returned
		global open_files_returned
		global percentage_of_duration_returned

		attendance_path_returned = attendance_path_display.cget("text")
		history_path_returned = history_path_display.cget("text")
		reference_path_returned = reference_path_display.cget("text")
		open_files_returned = open_files_var.get()

		# Forbids program to start if user does not input an number
		try:
			percentage_of_duration_returned = float(percentage_of_duration_var.get())
		except:
			return
		# Forbids program to start if user does not choose paths
		if attendance_path_returned == '' or history_path_returned == '' or reference_path_returned == '':
			return

		# If everything is fine, close window and start the program
		window.destroy()
	
	window = tk.Tk()
	window.title(app_name)
	window.iconbitmap(app_icon_path)
	
	# Define 3 Frames:
	header = tk.Frame()
	paths = tk.Frame()
	settings = tk.Frame()
	footer = tk.Frame()
	
	# Gets Browse Icon
	browse_img = Image.open(r'.\Icons\Browse Icon.png').resize((35, 35))
	browse_img = ImageTk.PhotoImage(browse_img)

	
	#===== HEADER (credits)
	credits = tk.Label(master=header, text="Written by Patrick Oweijane", width=45, height=1, bg="black", fg='white')
	credits.pack()
	
	#===== PATHS (browse directories)

	# Attendance
	attendance_text = tk.Label(master=paths, text='Your attendance files are in this folder:')
	attendance_text.grid(row=0, column=0, sticky='nsew')

	attendance_path_display = tk.Label(master=paths, text=attendance_path, bg='white')
	attendance_path_display.grid(row=0, column=1, sticky='nsew')

	attendance_path_btn = tk.Button(master=paths, image=browse_img, cursor="X_cursor")
	attendance_path_btn.grid(row=0, column=2, sticky='nsew')
	attendance_path_btn.bind("<Button-1>", browse_attendance)
	
	# History
	history_text = tk.Label(master=paths, text='Your history files are in this folder:')
	history_text.grid(row=1, column=0, sticky='nsew')

	history_path_display = tk.Label(master=paths, text=history_path, bg='white')
	history_path_display.grid(row=1, column=1, sticky='nsew')

	history_path_btn = tk.Button(master=paths, image=browse_img, cursor="X_cursor")
	history_path_btn.grid(row=1, column=2, sticky='nsew')
	history_path_btn.bind("<Button-1>", browse_history)

	# Reference
	reference_text = tk.Label(master=paths, text='Your reference files are in this folder:')
	reference_text.grid(row=2, column=0, sticky='nsew')

	reference_path_display = tk.Label(master=paths, text=reference_path, bg='white')
	reference_path_display.grid(row=2, column=1, sticky='nsew')

	reference_path_btn = tk.Button(master=paths, image=browse_img, cursor="X_cursor")
	reference_path_btn.grid(row=2, column=2, sticky='nsew')
	reference_path_btn.bind("<Button-1>", browse_reference)

	#===== SETTINGS

	# Open output excel files
	open_files_var = tk.IntVar(value=open_files)
	open_files_btn = tk.Checkbutton(master=settings, text='Open files in Excel',variable=open_files_var, onvalue=1, offvalue=0, cursor='plus')
	open_files_btn.grid(row=0, columnspan=2, sticky='nsew')

	# Percentage of duration
	percentage_of_duration_text = tk.Label(master=settings, text='Meeting duration minimum percentage:')
	percentage_of_duration_text.grid(row=1, column=0, sticky='nsew')

	percentage_of_duration_var = tk.StringVar(value=str(percentage_of_duration))
	percentage_of_duration_btn = tk.Entry(master=settings, textvariable=percentage_of_duration_var, bg='white')
	percentage_of_duration_btn.grid(row=1, column=1, sticky='nsew')	
	
	#FOOTER (execution of code)
	execute_btn = tk.Button(master=footer, text="EXECUTE", width=45, height=5, bg="black", fg='white', cursor="X_cursor")
	execute_btn.pack()
	execute_btn.bind("<Button-1>", start_program)

	header.pack()
	paths.pack()
	settings.pack()
	footer.pack()
	
	window.mainloop()

	return {"attendance path": attendance_path_returned, "history path": history_path_returned, "reference path": reference_path_returned, 'open files':open_files_returned, 'percentage of duration':percentage_of_duration_returned}