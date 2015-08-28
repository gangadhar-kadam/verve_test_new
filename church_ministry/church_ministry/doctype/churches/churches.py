# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint
from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
from gcm import GCM

class Churches(Document):
	# pass
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname(self.zone + '/' + 'CHR' + '.####')

	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,name from `tabGroup Churches` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group" : value[0][1]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,name from `tabGroup Churches` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group" : value[0][1]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone from `tabGroup Churches` where name='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1]
				}
			return ret


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabChurches` where church_name='%s' and church_group='%s' and church_code='%s'"%(doc.church_name,doc.church_group,doc.church_code))
		if res:
			frappe.throw(_("Another Church '{3}' With Church Name '{0}' and Church Code '{2}'' exist in Church Group '{1}'").format(doc.church_name, doc.church_group,doc.church_code,res[0][0]))

		notify_msg = """Dear User,\n
			Region is created with name '%s' for Group Church '%s' \n
			\n
			Regards,\n
			Love World Synergy"""%(doc.church_name,doc.church_group)
		notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field='on_creation_of_a_new_cell_pcf_church'""",as_list=1)
		if "Email" in notify[0][0]:
			if doc.email_id:
				frappe.sendmail(recipients=doc.email_id, content=notify_msg, subject='Region Creation Notification')
		if "SMS" in notify[0][0]:
			if doc.phone_no:
				send_sms(doc.phone_no, notify_msg)
		if "Push Notification" in notify[0][0]:
			data={}
			data['Message']=notify_msg
			gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
			res1=frappe.db.sql("select device_id from tabUser where name ='%s'" %(doc.email_id),as_list=1)
			frappe.errprint(res1)
			if res1:
				res1 = gcm.json_request(registration_ids=res1, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)

