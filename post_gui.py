import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import askyesno

from pathlib import Path

from message import Message

app_icon_path = Path('./Icons/App Icon.ico')
app_name = 'Attendance Tool'


def commit_send(email):
	print(email)


def get_child_id(parent_id, child_last_digits, sep='.'):
	return f'{parent_id}{sep}{child_last_digits}'


class attendance_tree(ttk.Treeview):
	'''
	This object is a tree view containing the attendance.
	It is used in the main window
	'''

	def __init__(self, files_dict:dict, screen_width:int, parents_are_opened:bool, **kwargs):
		super().__init__(**kwargs)
		self['columns'] = (
			'Class',
			'Number of students',
			'Number of attendees',
			'Absents',
			'Intruders',
			'Date',
		)
		col_width = screen_width//8

		self.column('#0', width=col_width//2, minwidth=80)
		self.column('Class', anchor='center', width=col_width*2, minwidth=80)
		self.column('Number of students', anchor='center', width=int(col_width*1.5), minwidth=80)
		self.column('Number of attendees', anchor='center', width=col_width, minwidth=80)
		self.column('Absents', anchor='center', width=int(col_width/1.5), minwidth=80)
		self.column('Intruders', anchor='center', width=int(col_width/1.5), minwidth=80)
		self.column('Date', anchor='center', width=col_width, minwidth=80)

		self.heading('#0', text='Filename')
		self.heading('Class', text='Class')
		self.heading('Number of students', text='# of students')
		self.heading('Number of attendees', text='# of attendees')
		self.heading('Absents', text='# of absents')
		self.heading('Intruders', text='# of intruders')
		self.heading('Date', text='Date')

		self.tag_configure('parent', background='#C5C5C5', font=('Calibri', 13, 'bold',))
		self.tag_configure('child', background='#C5C5C5', font=('Calibri', 11, 'bold',))
		self.tag_configure('info_absent', background='lightblue', font=('Calibri', 11))
		self.tag_configure('info_intruder', background='pink', font=('Calibri', 11))

		# Add Data
		for i, (filename, info) in enumerate(files_dict.items()):
			# Add first child row
			parent_id = f'{i}'
			self.insert(
				parent='', 
				index='end', 
				iid=parent_id, 
				text=f'{filename.stem}',
				values=(
					f'{info["class name"]}',
					f'{info["number of students"]}',
					f'{info["number of attendees"]}',
					f'{len(info["absents"])}',
					f'{len(info["intruders"])}',
					f'{info["date"]}',
				),
				tags=('parent',)
			)
			# Add second child row which is 
			child_last_digits = 0
			self.item(parent_id, open=parents_are_opened)
			self.insert(
				parent=parent_id,
				index='end', 
				iid=get_child_id(parent_id, child_last_digits), 
				text='Type', 
				values=(
					'Name',
					'Email',
					'Time Attended (minutes)',
					'Has Attended',
				),
				tags = ('child',)
			)
			child_last_digits += 1
			# Add rows of absents
			for email, absent in info['absents'].items():
				if absent['has attended']:
					has_attended = 'Yes'
				else:
					has_attended = 'No'
				self.insert(
					parent=parent_id, 
					index='end', 
					iid=get_child_id(parent_id, child_last_digits), 
					text='Absent',
					values=(
						absent['name'],
						email,
						absent['duration'],
						has_attended,
					),
					tags = ('info_absent',),
				)
				child_last_digits += 1
			# Add rows of intruders
			for email, intruder in info['intruders'].items():
				self.insert(
					parent=parent_id, 
					index='end', 
					iid=get_child_id(parent_id, child_last_digits), 
					text='Intruder',
					values=(
						intruder['name'],
						email,
						intruder['duration'],
						'Yes',
					),
					tags = ('info_intruder',),
				)
				child_last_digits += 1


class keywords_tree(ttk.Treeview):
	identifier_to_description ={
	'student email': 'Email of the student receiving the email',
	'student duration': 'Duration attended in minutes of the student receiving the email',
	'student name': 'Reference or display name of the student receiving the email',
	'meeting duration': 'Duration in minutes of the zoom meeting',
	'date': 'Date of the zoom meeting',
	'class name': 'Class name of the zoom meeting',
	}
	keyword_colwidth = 200
	description_colwidth = 500

	def __init__(self, keywords_dict, **kwargs):
		super().__init__(**kwargs) #show=["headings"] argument in initialization to remove #0

		self['columns'] = (
			'Key Word',
			'Description',
		)

		self.column('Key Word', anchor='center', width=keywords_tree.keyword_colwidth, minwidth=20)
		self.column('Description', anchor='center', width=keywords_tree.description_colwidth, minwidth=20)

		self.heading('Key Word', text='Key Word')
		self.heading('Description', text='Description')

		self.tag_configure('even', background='lightgrey', font=('Calibri', 11))
		self.tag_configure('odd', background='white', font=('Calibri', 11))

		# Add Data
		for i, (identifier, keyword) in enumerate(keywords_dict.items()):
			if i % 2 == 0:
				tag = 'odd'
			else:
				tag = 'odd'
			# Add first child row
			parent_id = f'{i}'
			self.insert(
				parent='', 
				index='end', 
				iid=parent_id,
				values=(
					keyword,
					keywords_tree.identifier_to_description[identifier],
				),
				tags=(tag,)
			)

class main_window(tk.Tk):
	'''
	This is the main window.
	Additional attributes: 
		parents_are_opened: Boolean value that keeps track of whether or not
							the parents in the treeview are opened at the moment,
		manage_parents_btn_text: tk.StrinVar object that is either 'Close All Rows'
								 or 'Open All Rows'.
		files_dict: Dictionary used by the method send_all to send emails to everyone.
		default_settings: Dictionary containing all the default settings. Gets updated
						  by the default_settings_window object
	'''
	manage_parents_btn_dict = {
		True: 'Close All Rows',
		False: 'Open All Rows'
	}

	def __init__(self, files_dict:dict, default_settings:dict):
		super().__init__()
		self.title(app_name)
		self.iconbitmap(app_icon_path)
		# Positions the window in the center of the page.
		self.geometry('+0+0')
		# Adding new attributes used to keep track of whether
		# parents in tree are opened or not
		self.parents_are_opened = default_settings['parents are opened']
		self.manage_parents_btn_text = tk.StringVar(
			value=main_window.manage_parents_btn_dict[self.parents_are_opened]
		)
		self.files_dict = files_dict
		self.default_settings = default_settings
		# Configuring style used by attendance_tree
		style = ttk.Style(master=self)
		style.theme_use('clam')
		style.configure('mystyle.Treeview', font=('Calibri', 11)) # Modify the font of the body
		style.configure('mystyle.Treeview.Heading', font=('Calibri', 13,'bold')) # Modify the font of the headings
		style.layout('mystyle.Treeview', [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) # Remove the borders
		style.map('Treeview', background=[('selected', 'darkblue')])
		#========== Tree frame
		tree_frame = tk.Frame(master=self)
		# Tree
		tree = attendance_tree(
			files_dict=files_dict,
			screen_width=self.winfo_screenwidth(),
			parents_are_opened =self.parents_are_opened,
			master=tree_frame,
			style='mystyle.Treeview',
			height=20
		)
		tree.pack(side='left')
		# Tree scrollbar
		scrollbar = tk.Scrollbar(master=tree_frame, command=tree.yview)
		scrollbar.pack(side='left', expand=True, fill='y')
		tree.configure(yscrollcommand=scrollbar.set)

		tree_frame.pack(padx=self.winfo_screenwidth()//32)
		#========== Table Interaction frame
		table_interaction_frame = tk.Frame(master=self)
		# Manage parents button
		manage_parents_btn = tk.Button(
			master=table_interaction_frame,
			textvariable=self.manage_parents_btn_text,
			width=11,
			font=('Calibri', 11),
		)
		manage_parents_btn.bind('<Button-1>', lambda e:self.manage_parents(e, tree))
		manage_parents_btn.pack(side='left', padx=25)

		# Send emails to all button
		send_all_btn = tk.Button(
			master=table_interaction_frame,
			text='Send Personalized Emails to Everyone',
			font=('Calibri', 11),
		)
		send_all_btn.bind('<Button-1>', lambda e:self.send_all(e))
		send_all_btn.pack(side='left', padx=25)

		table_interaction_frame.pack(pady=35)
		#========== Default Settings Frame
		default_settings_frame = tk.Frame(master=self)
		change_settings_btn = tk.Button(
			master=default_settings_frame,
			text='Change Default Settings',
			width=20
		)
		change_settings_btn.bind('<Button-1>', lambda e:default_settings_window(self))
		change_settings_btn.pack(side='left', padx=25)
		default_settings_frame.pack(pady=35)

		self.mainloop()

	def manage_parents(self, event, tree):
		'''
		This method closes and opens the attendance_tree present
		in self
		'''
		self.parents_are_opened = not self.parents_are_opened
		self.manage_parents_btn_text.set(
			main_window.manage_parents_btn_dict[self.parents_are_opened]
		)
		for parent_id in tree.get_children(''):
			tree.item(parent_id, open=self.parents_are_opened)

	def send_all(self, event):
		'''
		This method sends emails to all absents and intruders
		'''
		def parse_email(email:str, key_words:dict):
			for key, value in key_words.items():
				email = email.replace(key, str(value))
			return email
		if not askyesno(
			title='Attendance Tool (Automatic Emails)',
			message='Clicking "Yes" will automatically send emails to all absents '\
					'and intruders. If you do not wish to proceed, click "No".'
			):
			return
		word_key = self.default_settings['keywords dict']
		key_words = {key:value for value, key in word_key.items()}
		for info in self.files_dict.values():
			key_words[word_key['class name']] = info['class name']
			key_words[word_key['date']] = info['date']
			key_words[word_key['meeting duration']] = info['meeting duration']
			
			for email, absent in info['absents'].items():
				if absent['has attended']:
					continue
				key_words[word_key['student email']] = email
				key_words[word_key['student name']] = absent['name']
				key_words[word_key['student duration']] = absent['duration']

				parsed_email_text = parse_email(self.default_settings['absent email']['message text'], key_words)
				parsed_email_subject = parse_email(self.default_settings['absent email']['subject'], key_words)
				Message('me', email, parsed_email_subject, parsed_email_text).send_message()

			for email, intruder in info['intruders'].items():
				key_words[word_key['student email']] = email
				key_words[word_key['student name']] = intruder['name']
				key_words[word_key['student duration']] = intruder['duration']

				parsed_email_text = parse_email(self.default_settings['intruder email']['message text'], key_words)
				parsed_email_subject = parse_email(self.default_settings['intruder email']['subject'], key_words)
				Message('me', email, parsed_email_subject, parsed_email_text).send_message()


class default_settings_window(tk.Toplevel):
	'''
	This object pops up when the user clicks on the 'Change Default Settings'
	button present in main_window
	'''
	absent_column = 0
	intruder_column = 1

	def __init__(self, main_window:object, **kwargs):
		screen_width = main_window.winfo_screenwidth()
		super().__init__(**kwargs)
		self.title(f'{app_name} (Default Settings)')
		self.iconbitmap(app_icon_path)
		# Positions the window in the center of the page.
		self.geometry(f'+{screen_width//50}+25')

		#========== Emails Frame
		emails_frame = tk.Frame(master=self)

		absent_label = tk.Label(
			master=emails_frame,
			text='Automatic email sent to the absents.',
			font=('Calibri', 13),
		)
		absent_label.grid(row=0, column=default_settings_window.absent_column)

		intruder_label = tk.Label(
			master=emails_frame,
			text='Automatic email sent to the intruders.',
			font=('Calibri', 13),
		)
		intruder_label.grid(row=0, column=default_settings_window.intruder_column)

		absent_subject = tk.Entry(
			master=emails_frame,
			font=('Calibri', 13),
			width=screen_width//20,
		)
		absent_subject.insert(tk.END, main_window.default_settings['absent email']['subject'])
		absent_subject.grid(row=1, column=default_settings_window.absent_column, sticky='w')

		intruder_subject = tk.Entry(
			master=emails_frame,
			font=('Calibri', 13),
			width=screen_width//20,
		)
		intruder_subject.insert(tk.END, main_window.default_settings['intruder email']['subject'])
		intruder_subject.grid(row=1, column=default_settings_window.intruder_column, sticky='w')

		absent_email_stext = ScrolledText(
			master=emails_frame,
			font=('Calibri', 13),
			width=screen_width//20,
			height=15
		)
		absent_email_stext.insert(tk.END, main_window.default_settings['absent email']['message text'])
		absent_email_stext.grid(row=2, column=default_settings_window.absent_column, pady=10)

		intruder_email_stext = ScrolledText(
			master=emails_frame,
			font=('Calibri', 13),
			width=screen_width//20,
			height=15
		)
		intruder_email_stext.insert(tk.END, main_window.default_settings['intruder email']['message text'])
		intruder_email_stext.grid(row=2, column=default_settings_window.intruder_column, pady=10)

		emails_frame.pack(padx=20)

		# Adding email keywords tree view 
		style = ttk.Style(master=self)
		style.theme_use('default')
		style.configure('mystyle.Treeview', font=('Calibri', 11)) # Modify the font of the body
		style.configure('mystyle.Treeview.Heading', font=('Calibri', 11)) # Modify the font of the headings
		style.layout('mystyle.Treeview', [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) # Remove the borders
		style.map('Treeview', background=[('selected', 'darkblue')])
		tree = keywords_tree(main_window.default_settings['keywords dict'], master=self, show=["headings"], style='mystyle.Treeview', height=6)
		tree.pack(pady=20)

		# Adding checkbox for opened parents
		self.parents_are_opened = tk.BooleanVar(
			master=self,
			value=main_window.default_settings['parents are opened']
		)
		parents_are_opened_checkbox = tk.Checkbutton(
			master=self,
			text='Tick if you want all rows to start opened',
			variable=self.parents_are_opened,
			font=('Calibri', 11),
		)
		parents_are_opened_checkbox.pack(pady=10)

		save_btn = tk.Button(
			master=self,
			text='Save the current settings',
			font=('Calibri', 11),
		)
		save_btn.bind(
			'<Button-1>',
			lambda e: self.save_settings(
				absent_subject=absent_subject,
				absent_email_stext=absent_email_stext,
				intruder_subject=intruder_subject,
				intruder_email_stext=intruder_email_stext,
				main_window=main_window,
			)
		)
		save_btn.pack(pady=10)

	def save_settings(self, absent_subject, absent_email_stext, intruder_subject, intruder_email_stext, main_window):
		'''
		This method modifies the main_window default_settings attribute
		with the current settings found in self.
		'''
		# We remove the last character which is an added '\n'
		main_window.default_settings['absent email']['subject'] = absent_subject.get()
		main_window.default_settings['intruder email']['subject'] = intruder_subject.get()
		main_window.default_settings['absent email']['message text'] = absent_email_stext.get('1.0', tk.END)[:-1]
		main_window.default_settings['intruder email']['message text'] = intruder_email_stext.get('1.0', tk.END)[:-1]
		main_window.default_settings['parents are opened'] = self.parents_are_opened.get()
		self.destroy()


def main(files_dict:dict, default_settings:dict):
	root = main_window(files_dict, default_settings)
	return root.default_settings


'''
================================ATTENTION=======================================
MUST ADD MEETING TOTAL DURATION TO files_dict. WE USE THIS IN
PERSONALIZED EMAIL.
CHANGES MUST BE MADE IN THE main.py SCRIPT.
================================ATTENTION=======================================
'''


# 'keywords dict' : {
# 	'student email': 'STUDENT EMAIL',
# 	'student duration': 'STUDENT DURATION',
# 	'student name': 'STUDENT',
# 	'meeting duration': 'MEETING DURATION',
# 	'date': 'DATE',
# 	'class name': 'CLASS',
# }