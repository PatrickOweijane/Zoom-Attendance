# =============================================================================
# CHOOSE YOUR SETTINGS
# =============================================================================

# Regex used to find attendance files
regex = '^participants_\d{11}(?: \(\d+\)|).csv$'

# =============================================================================
# FUNCTIONS AND MODULES USED
# =============================================================================

from os import remove, rename, system
import json
from pathlib import Path

from csv_functions import *
from general_functions import *
from specific_functions import *
import pre_gui
import post_gui

# =============================================================================
# START OF PROGRAM
# =============================================================================

# Get info from config file
try:
	with open('config.json') as f:
		config = json.load(f)
		attendance_PATH = config['attendance path']
		reference_PATH = config['reference path']
		history_PATH = config['history path']
		open_files = config['open files']
		percentage_of_duration = config['percentage of duration']
		default_settings = config['default settings']
except:
	attendance_PATH = ''
	reference_PATH = ''
	history_PATH = ''
	open_files = 0
	percentage_of_duration = 0
	default_settings = {
		'parents are opened': False,
		
		'intruder email': {
			'subject': 'Intruder Automatic Message',
			'message text': \
f'''Hello STUDENT,

You are reveiving this message because you have joined \
the zoom meeting of class CLASS at DATE \
without permission.

Thank you,
Patrick'''
},
		'absent email': {
			'subject': 'Absent Automatic Message',
			'message text': \
f'''Hello STUDENT,

You are reveiving this message because you were absent in \
the zoom meeting of class CLASS at DATE.

Thank you,
Patrick'''
},

		'irregular email': {
			'subject': 'Absent Automatic Message',
			'message text': \
f'''Hello STUDENT,

You are reveiving this message because you attended \
the zoom meeting of class CLASS at DATE for less than \
DURATION_PERCENTAGE% of the meeting duration.

Thank you,
Patrick'''
},

		'keywords dict' : {
			'student email': 'STUDENT EMAIL',
			'student duration': 'STUDENT DURATION',
			'student name': 'STUDENT',
			'meeting duration': 'MEETING DURATION',
			'date': 'DATE',
			'class name': 'CLASS',
		}
	}

new_config = pre_gui.main(attendance_PATH, history_PATH, reference_PATH, open_files, percentage_of_duration)

if new_config['percentage of duration'] == int(new_config['percentage of duration']):
	new_config['percentage of duration'] = int(new_config['percentage of duration'])

# Get the settings from the new config
attendance_PATH = new_config['attendance path']
history_PATH = new_config['history path']
reference_PATH = new_config['reference path']
open_files = new_config['open files']
percentage_of_duration = new_config['percentage of duration']

# Initialize dictionary that will be used for the output GUI
files_dict = {}

#=====GET attendances filenames
attendances_filenames = get_filenames(regex, attendance_PATH)
#=====GET the classname and time of the attendance files
attendances_tuples = []
for attendance_filename in attendances_filenames:
	class_name, time = retrieve_info(attendance_filename, attendance_PATH, [(1,1), (1,2)])
	datetime = get_datetime(time)
	datetime = f"{datetime['date']} {datetime['time']}"
	attendances_tuples.append((class_name, datetime, attendance_filename))
#=====SORT the filenames WRT (class, time)
attendances_tuples.sort(key=lambda element: (element[0], element[1], get_suffix(element[2])))

#=====REMOVE files that have the same class/time but different filename (remove from attendance_tuples and PATH)
lst = attendances_tuples.copy()
for elem1, elem2 in zip(lst, lst[1:]):
	if elem1[:2] == elem2[:2]:
		attendances_tuples.remove(elem1)
		remove(f'{attendance_PATH}\\{elem1[2]}')

attendances_filenames = [tup[2] for tup in attendances_tuples]

#=====LOOP through the attendance files
for attendance_filename in attendances_filenames:

	#=====READ attendance file
	attendance_lines = read_csv(attendance_filename, attendance_PATH)
	#ANALYZE attendance: {email:duration}
	attendance = get_attendance(attendance_lines)

	class_name = attendance['class']
	string_date = attendance['start time']
	date = get_datetime(string_date)
	time, date = date['time'], date['date']
	base_filename = f'{class_name}.{date}'

	#=====READ reference file
	reference_lines = read_csv(f'Reference {class_name}.csv', reference_PATH)
	#ANALYZE reference {email:name}
	reference = get_reference(reference_lines)

	#=====COMPUTE absents {email:{name, has attended, duration}}
	absents = get_absents(attendance, reference, percentage_of_duration)

	#=====TRANSFORM absents to a list of tuples in order to add info to attendance_lines
	absents_list = []
	for email, absent in absents.items():
		if absent['has attended']:
			absents_list.append((absent['name'], f'<{percentage_of_duration}%'))
		else:
			absents_list.append((absent['name'],))

	#=====COMPUTE intruders {email:{'name':name, 'duration':duration}}
	intruders = get_intruders(attendance, reference)

	#=====TRANSFORM intruders to a list of tuples in order to add info to attendance_lines
	intruders_list = [(person['name'], email, person['duration'], 'Intruder') for email, person in intruders.items()]

	#COMPUTE the head
	n_of_absents = len(absents)
	n_of_intruders = len(intruders)
	n_of_attendees = 0
	for email in attendance['attendants']:
		if email != attendance['host']:
			n_of_attendees += 1
	n_of_students = n_of_attendees - n_of_intruders

	head = [('Absents', 'Intruders', 'Students Nb', 'Attendees Nb'), 
			(str(n_of_absents), str(n_of_intruders), str(n_of_students), str(n_of_attendees))]

	#CONCATENATE head, absents, intruders
	new_info = head + [''] + absents_list + intruders_list

	#=====ADD new_info to attendance lines
	add_info(attendance_lines, new_info, 7)

	#=====GET history filenames of same class and date
	history_filenames = get_filenames(f"^{base_filename}'*.csv$", history_PATH)

	#=====GET start times + history filename [(time,filename)] to SORT them WRT start time
	history_tuples = []
	for filename in history_filenames:
		start_time = get_datetime(retrieve_info(filename, history_PATH, coordinates=[(1, 2)])[0])['time']
		history_tuples.append((start_time, filename))
	history_tuples.sort(reverse=True)

	#=====RENAME history filenames so that the number of quotes in the filename indicates time
	counter = 0
	overwrite = False
	for start_time, filename in history_tuples:
		#if there exist a history file with the same start time as the attendance file,
		#then the history file will be overwritten by the attendance file and that's all
		if start_time == time:
			new_filename = filename
			write_csv(attendance_lines, new_filename, history_PATH)
			overwrite = True
			break
		if start_time < time:
			break
		counter += 1
	if not overwrite:
		#if the attendance start time is UNIQUE,
		#then we add quotes to the most recent files
		#and write the attendance file in the history folder with the correct name
		files_to_rename = history_tuples[:counter]
		for counter, (_, filename) in enumerate(files_to_rename):
			n_of_quotes = len(history_tuples) - counter
			rename(f"{history_PATH}\\{filename}",f'''{history_PATH}\\{base_filename}{"'"*n_of_quotes}.csv''')

		n_of_quotes = len(history_tuples) - len(files_to_rename)
		new_filename = f'''{base_filename}{"'"*n_of_quotes}.csv'''
		write_csv(attendance_lines, new_filename, history_PATH)

	#=====DELETE attendance_filename
	remove(f'{attendance_PATH}\\{attendance_filename}')

	#=====GET new history file path
	new_filepath = f'{history_PATH}/{new_filename}'

	#=====OPEN files using excel
	if open_files:
		system(f'start excel "{new_filepath}"')

	#=====ADDING info to file_dict that will be used for the output GUI
	files_dict[Path(new_filepath)] = {
		'class name': class_name,
		'date': string_date,
		'absents': absents,
		'intruders': intruders,
		'number of students':n_of_students,
		'number of attendees':n_of_attendees,
		'meeting duration': 90,
	}

new_config['default settings'] = post_gui.main(files_dict, default_settings)

# Overwrite config file
with open('config.json', 'w') as f:
	json.dump(new_config, f, indent=4)