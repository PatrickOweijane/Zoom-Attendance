import os
import re

def get_filenames(regex:str, PATH):
	"""
	returns the list of filenames in the PATH that match with the regex
	"""
	paths = os.listdir(path=PATH)
	files = []
	for path in paths:
		file = re.findall(regex, path)
		if not file:
			continue
		files.append(file[0])
	return files

def get_suffix(filename):
	"""
	participants_12141.csv --> 0
	participants_12141 (10).csv --> 10
	"""
	suffix = re.findall('\((\d+)\)\.csv$', filename)
	if not suffix:
		return 0
	else:
		return int(suffix[0])

def get_datetime(full_date:str):
	"""
	takes MM/DD/YYYY hh:mm:ss tt
	returns {date: YYYY.MM.DD, time: tt.hh:mm:ss}
	Notes: 12 PM becomes 00 PM for comparison purposes
	"""
	date, time, midday = full_date.split()

	month, day, year = date.split('/')
	date = f'{year}.{month}.{day}'

	hour, minute, second = time.split(':')

	if midday == 'PM' and hour == '12':
		time = f'00:{minute}:{second}'

	time = f'{midday}.{time}'
	return {'date':date, 'time':time}

def histogram(lst):
	out_dict = {}
	for row, column in lst:
		if row not in out_dict:
			out_dict[row] = [column]
		else:
			out_dict[row].append(column)
	return out_dict
