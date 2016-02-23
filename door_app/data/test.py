import hashlib
with open(".yolo") as f:
	data = f.readline().strip()
	if hashlib.sha224('18981898').hexdigest() == data:
		print hashlib.sha224('18981898').hexdigest()
		print data
		print 'good'
	else:
		print 'no'
		print hashlib.sha224('18981898').hexdigest()
		print data 
