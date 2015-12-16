import frappe
import requests
import json
from frappe.utils import cstr
from frappe.utils.data import getdate

@frappe.whitelist()
def get_children(from_date, to_date):
	args = frappe.local.form_dict
	if args['parent'] == 'Users':
		acc = frappe.db.sql("""select concat('<b>',name,'</b> : ', 
				email_id__if_administrator) as value, 1 as expandable 
			from `tabSite Master`""", as_dict=1,debug=1)

	else: 
		acc	= frappe.db.sql(""" select name as value, 0 as expandable 
			from `%s`.`tabUser` where name not in ('Administrator', 'Guest') %s """%(get_db_name(get_site_name(args['parent'])), 
				get_cond(from_date, to_date)), as_dict=1,debug=1)

	return acc

def get_cond(from_date, to_date):
	if from_date and to_date:
		return " and validity_end_date between '%s' and '%s'"%(format_date(cstr(from_date)), format_date(cstr(to_date)))
	return ''

def get_db_name(site_name):
	# site_name = get_site_name(parent)

	if site_name.find('.')!= -1:
		return site_name.split('.')[0][:16]

	else:
		return site_name[:16]

def get_site_name(raw_site_name):
	return raw_site_name[3:len(raw_site_name.split(':')[0])-5]

@frappe.whitelist()
def manage_mail_ticker(recipient, purpose, message):
	validate(recipient)

	recipient = eval(recipient)

	if purpose == 'Mail':
		send_mail(recipient, message)
	
	if purpose == 'Ticker':
		add_ticker(recipient, message)

def validate(recipient):
	if not recipient:
		frappe.msgprint("Recipient Not Fount. Please select Recipient!!!!!",raise_exception=1)

def send_mail(recipient, message):
	import itertools
	from frappe.utils.email_lib import sendmail

	emails = [value for key, value in recipient.items()]
	sendmail(list(itertools.chain(*emails)), subject="Notification", msg=cstr(message))

def add_ticker(recipient, message):
	[(key,site_list)] = recipient.items()

	for site_name in site_list:
		site_name = get_site_name(site_name)
		headers = {'content-type': 'application/x-www-form-urlencoded'}

		#login
		sup={'usr':'administrator','pwd':'admin'}
		url = 'http://'+cstr(site_name)+'/api/method/login'
		response = requests.get(url, data=sup, headers=headers)

		#update_ticker
		for site_user in frappe.db.sql("""select name from `%s`.`tabUser`
			 where name not in ('Guest') """%(get_db_name(site_name))):
			url="http://%(site_name)s/api/resource/User/%(user)s"%{'site_name':cstr(site_name), 'user':site_user[0]}
			frappe.errprint(url)
			user = {}
			user['ticker'] = cstr(message)
			user['disable_ticker'] = 1
			response = requests.put(url, data='data='+json.dumps(user), headers=headers)

@frappe.whitelist()
def get_ticker(user):
	return {
		'ticker': frappe.db.get_value('User', 'Administrator', 'ticker'),
		'is_ticker_enable': frappe.db.get_value('User', user, 'ifnull(disable_ticker, 0)')
	}
	


@frappe.whitelist()
def get_email_body(template_name):
	return frappe.db.get_value('Email Template', template_name, 'message')

def format_date(str_date):
	import datetime
	return datetime.datetime.strptime(str_date, '%d-%m-%Y').strftime('%Y-%m-%d')


@frappe.whitelist()
def hide_ticker(user):
	frappe.db.set_value("User", user, 'disable_ticker', 0)
