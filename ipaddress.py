import urllib2
import requests
import datetime
import sqlite3

class HoverException(Exception):
	pass
	
class HoverAPI(object):
	def __init__(self, username, password):
		params = {"username": username, "password": password}
		r = requests.post("https://www.hover.com/api/login", params=params)
		if not r.ok or "hoverauth" not in r.cookies:
			raise HoverException(r)
		self.cookies = {"hoverauth": r.cookies["hoverauth"]}
	def call(self, method, resource, data=None):
		url = "https://www.hover.com/api/{0}".format(resource)
		r = requests.request(method, url, data=data, cookies=self.cookies)
		if not r.ok:
			raise HoverException(r)
		if r.content:
			body = r.json()
			if "succeeded" not in body or body["succeeded"] is not True:
				raise HoverException(body)
			return body

def get_public_ip():
	return requests.get("http://ifconfig.me/ip").content

def update_dns(username, password, fqdn, ip):
	try:
		client = HoverAPI(username, password)
	except HoverException as e:
		raise HoverException("Authentication failed")
	dns = client.call("get", "dns")
	dns_id = None
	for domain in dns["domains"]:
		if fqdn == domain["domain_name"]:
			fqdn = "@.{domain_name}".format(**domain)
		for entry in domain["entries"]:
			if entry["type"] != "A": continue
			if "{0}.{1}".format(entry["name"], domain["domain_name"]) == fqdn:
				dns_id = entry["id"]
				break
	
	if dns_id is None:
		raise HoverException("No DNS record found for {0}".format(fqdn))
						
	response = client.call("put", "dns/{0}".format(dns_id), {"content": ip})
	
	if "succeeded" not in response or response["succeeded"] is not True:
		raise HoverException(response)
		
username = 'YOUR_USERNAME'
password = 'YOUR_PASSWORD'
domain = 'YOUR_DOMAIN'

conn = sqlite3.connect('ip.db')
c = conn.cursor()
c.execute('''create table if not exists ip_history
             (date text, ip text)''')
c.execute('select count(*) from ip_history')

result = c.fetchone()

old_ip = '0.0.0.0'
if (result[0] != 0):
	c.execute('select ip from ip_history order by date desc')
	result = c.fetchone()
	old_ip = result[0]

ip = get_public_ip()
print 'IP Check'
print datetime.datetime.today()

if (ip != old_ip):
	try:
		update_dns(username, password, domain, ip)
		print 'DNS Updated'
		print 'Old IP: ' + old_ip
		print 'New IP: ' + ip
		date = datetime.datetime.today()
		c.execute('insert into ip_history (date,ip) values (?, ?)', (date, ip))
		conn.commit()
	except HoverException as e:
		print "Unable to update DNS: {0}".format(e)
		
conn.close()
