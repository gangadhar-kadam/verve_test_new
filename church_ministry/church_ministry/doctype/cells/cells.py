# Copyright (c) 2013, New Indictrans technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint
from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
from gcm import GCM

class Cells(Document):
	# pass
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname(self.church + '/' + 'CEL' + '.####')

	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,church_group,church,pcf,name from `tabSenior Cells` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,church_group,church,pcf,name from `tabSenior Cells` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone,church,pcf,name from `tabSenior Cells` where church_group='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.church:
			value = frappe.db.sql("select region,zone,church_group,pcf,name from `tabSenior Cells` where church='%s'"%(self.church),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.pcf:
			value = frappe.db.sql("select region,zone,church_group,church,name from `tabSenior Cells` where pcf='%s'"%(self.pcf),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.senior_cell:
			value = frappe.db.sql("select region,zone,church_group,church,pcf from `tabSenior Cells` where name='%s'"%(self.senior_cell),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"pcf" : value[0][4]
				}
			return ret

def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabCells` where cell_name='%s' and cell_code='%s' and senior_cell='%s'"%(doc.cell_name,doc.cell_code,doc.senior_cell))
		if res:
			frappe.throw(_("Another Cell '{0}' With Cell Name '{1}' and Cell Code '{2}' exist in Senior Cell '{3}'..!").format(res[0][0],doc.cell_name,doc.cell_code,doc.senior_cell))

		notify_msg = """Dear User,\n
			Region is created with name '%s' for Senior Cell '%s' \n
			\n
			Regards,\n
			Love World Synergy"""%(doc.cell_name,doc.senior_cell)
		notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field='on_creation_of_a_new_cell_pcf_church'""",as_list=1)
		if "Email" in notify[0][0]:
			if doc.contact_email_id:
				frappe.sendmail(recipients=doc.contact_email_id, content=notify_msg, subject='Region Creation Notification')
		if "SMS" in notify[0][0]:
			if doc.contact_phone_no:
				send_sms(doc.contact_phone_no, notify_msg)
		if "Push Notification" in notify[0][0]:
			data={}
			data['Message']=notify_msg
			gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
			res1=frappe.db.sql("select device_id from tabUser where name ='%s'" %(doc.contact_email_id),as_list=1)
			frappe.errprint(res1)
			if res1:
				res1 = gcm.json_request(registration_ids=res1, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)


