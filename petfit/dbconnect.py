import MySQLdb

def connection():
	conn = MySQLdb.connect(host="localhost", user="root", passwd="rhcp2138", db="petfit_flask")
	c = conn.cursor()

	return c, conn