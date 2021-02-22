import csv

def read_csv(filename:str, PATH):
	with open(f'{PATH}\\{filename}') as file:
		data = csv.reader(file)
		data = list(data)
	return data

def write_csv(lines:list, filename:str, PATH):
	with open(f'{PATH}\\{filename}', 'w') as f:
		write = csv.writer(f, lineterminator='\n')
		write.writerows(lines)