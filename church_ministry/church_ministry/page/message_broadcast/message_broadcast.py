# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
import json
from frappe.desk.reportview import get_match_cond
from frappe import throw, _, msgprint
import frappe.share
import time
import datetime
from frappe.model.document import Document
from frappe.utils import cstr,cint,now,add_days,nowdate
from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
import json

@frappe.whitelist()
def get_list(arg):
	arg = json.loads(arg)
	mapper = get_mapper(arg['type'])
	return {
		"members": query_builder(mapper, arg)
	}

def get_mapper(contype):
	return {
		'Members':{'columns':["member_name", "phone_1","email_id"], 'table': '`tabMember`'},
		'First Timers':{'columns':["ftv_name", "phone_1","email_id"], 'table': '`tabFirst Timer`'},
		'Invitees and Contacts':{'columns':["invitee_contact_name", "phone_1","email_id"], 'table': '`tabInvitees and Contacts`'},
		'All Leaders':{'columns':["member_name", "phone_1","email_id"], 'table': '`tabMember`'}
	}.get(contype)

def query_builder(mapper,arg):
	filters=condition(arg)
	return frappe.db.sql("""select %s from %s 
			where phone_1 is not null %s"""%(', '.join(mapper['columns']), mapper['table'],filters),as_list=1)

def condition(arg):
	cond = []
	for key in arg:
		if key != 'type':
			cond.append("%s='%s'"%(key,arg[key]))
		if arg['type']=='All Leaders':
			cond.append(" email_id in (select distinct parent from tabUserRole where role in ('PCF Leader','Cell Leader','Senior Cell Leader','Church Pastor','Group Church Pastor','Regional Pastor','Zonal Pastor'))")
	if cond:
		return ' and '+ ' and '.join(cond)
	else:
		return ''

@frappe.whitelist()
def send_sms1(numbers,msg,user):
	import math
	num=json.loads(numbers)
	i = datetime.datetime.now()
	today=datetime.date.today()
	if msg:		
		counter = frappe.db.sql("select sms_credits from `tabUser` where name='%s'"%(user),as_list=1)
		sms_len = math.ceil(len(msg)/160.0)
		count = len(num)*cint(sms_len)
		if counter and count<=cint(counter[0][0]):
			credit_count = counter[0][0] - count
			send_sms(num, cstr(msg))
			log = frappe.new_doc("SMS Log")
			log.sender_name = user
			log.sent_on = today
			log.receiver_list = numbers
			log.message = msg
			log.sms_sending_status = 'SMS Sent Successfully'
			log.insert()
			frappe.db.sql("update `tabUser` set sms_credits='%s' where name='%s'"%(credit_count,user))
			frappe.db.commit()
			frappe.msgprint(_("SMS Sent Successfully..."))
		else:
			log = frappe.new_doc("SMS Log")
			log.sender_name = user
			log.sent_on = today
			log.receiver_list = numbers
			log.message = msg
			log.sms_sending_status = 'Sending Fail'
			log.insert(ignore_permissions=True)
			frappe.db.commit()
			frappe.throw(_("SMS credit is not available for sending SMS, Sending fail..!"))
	else:
		frappe.throw(_("Message should not be blank,Please enter text message..."))


@frappe.whitelist()
def user_send_mail(member_name,user,msg):
	member_list=json.loads(member_name)
	if msg:	
		for usr in member_list:
			frappe.sendmail(recipients=usr, content=msg, subject='Verve')
		frappe.msgprint(_("Email Sent Successfully..."))		
	else:
		frappe.throw(_("Message should not be blank,Please enter text message..."))