# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint
from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
from gcm import GCM

class Regions(Document):
	pass

def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		frappe.errprint("not save...")
		res=frappe.db.sql("select name from `tabRegions` where region_name='%s' and region_code='%s'"%(doc.region_name,doc.region_code))
		if res:
			frappe.throw(_("Another Region '{0}' With Region Name '{1}' and Region Code '{2}' exist ..!").format(res[0][0],doc.region_name,doc.region_code))

		notify_msg = """Dear User,\n\n Region is created with name '%s' . \n\nRegards,\n\nLove World Synergy"""%(doc.region_name)

		notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field='on_creation_of_a_new_cell_pcf_church'""",as_list=1)
		if notify:
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
				# frappe.errprint(res1)
				if res1:
					res1 = gcm.json_request(registration_ids=res1, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)

		ofc = frappe.new_doc("Offices")
		ofc.office_id = doc.name
		ofc.office_name = doc.region_name
		ofc.office_code = doc.region_code
		ofc.insert()
