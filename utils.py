from datetime import datetime

def date_to_datetime(d):
	return datetime.fromordinal(d.toordinal())

def default_if_not(v1, v2):
	return v1 if v1 else v2