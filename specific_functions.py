import os
import csv
import itertools

from csv_functions import write_csv
from general_functions import histogram

def get_attendance(attendance:list):
	"""
	gets all possible information from a list
	the list should the result of read_csv on attendance/history
	returns dictionary for easier use
	"""
	class_name = attendance[1][1]
	start_time = attendance[1][2]
	meeting_host = attendance[1][4]
	meeting_duration = attendance[1][5]
	attendants = {email:{'name':name, 'duration':int(duration)} for name,email,duration,_ in attendance[4:]}
	return {'class':class_name,
			'start time':start_time,
			'host':meeting_host,
			'duration':int(meeting_duration),
			'attendants':attendants}

def get_reference(reference:list):
	"""
	takes a list of the reference | list = read_csv(reference)
	returns a dict | email --> name in the order of the inputted list
	"""
	return {email:name for name,email in reference}

def get_absents(attendance:dict, reference:dict, percentage_of_duration:int):
	"""
	computes absents using attendance and reference
	attendance, reference = get_attendance(), get_reference()
	returns {email:{name, has attended, duration}}
	"""
	min_time = percentage_of_duration/100 *attendance['duration']
	attendants = attendance['attendants']
	absents = {}
	for email, name in reference.items():
		if email in attendants:
			duration = attendants[email]['duration']
			if duration < min_time:
				absents[email] = {'name':name, 'has attended':True, 'duration':duration}
		else:
			absents[email] = {'name':name, 'has attended':False, 'duration':0}
	return absents

def get_intruders(attendance:dict, reference:dict):
	attendants = attendance['attendants']
	meeting_host = attendance['host']
	intruders = []
	for email, person in attendants.items():
		if email not in reference and email != meeting_host:
			intruders.append((person['name'], email, person['duration']))
	intruders.sort()
	intruders = {email:{'name':name, 'duration':duration} for name, email, duration in intruders}
	return intruders


def add_info(lines:list, infos:list, start_index:int):
	"""
	takes 2, 2D lists, and modifies the lines list in place, using infos, starting at a specific index
	typically use to add a column in a 2D list to later use for csv
	"""
	for line, info in zip(lines,infos):
		end_index = start_index + len(info)
		line.extend(['']*(end_index-len(line)))
		line[start_index:end_index] = info

def retrieve_info(filename, PATH, coordinates:list):
	'''
	Takes a csv filenames, its PATH, and a list of coordinates.
	Each coordinate represents (row, column) of the info that you want to retrieve,
	so each coordinate represent an item.
	Returns a list of items that looks like [item1, item2, ...]
	'''
	coordinates = histogram(sorted(coordinates))
	items = []
	with open(f'{PATH}/{filename}') as f:
		data = csv.reader(f)
		pointer = 0
		for row, columns in coordinates.items():
			line = next(itertools.islice(data, row-pointer, None))
			items.extend(line[column] for column in columns)
			pointer = row + 1
	return items

def rename_history_files(history_tuples:list, trigger_name, base_name, to_PATH):
	"""
	adds necessary "'" to the newer history filenames
	write the attendance file in history PATH with the correct name
	used when attendance_file has a UNIQUE start time
	"""
	history_tuples.sort(key=lambda element: (element[0], os.path.splitext(element[1])[0]), reverse=True)
	for counter, (_, filename) in enumerate(history_tuples):
		quotes = "'"*(len(history_tuples) - counter - 1)
		new_filename = f'{base_name}{quotes}.csv'
		if filename == trigger_name:
			write_csv(attendance_lines, new_filename, to_PATH)
			return new_filename
		os.rename(f"{to_PATH}\\{filename}",f"{to_PATH}\\{new_filename}")