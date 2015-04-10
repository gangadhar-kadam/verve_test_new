# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.desk.reportview import get_match_cond
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def loadftv():
	query="select name,invitee_contact_name,sex,date_of_birth,age_group from `tabInvitees and Contacts` where date_of_convert is null"
	return {
		"ftv": [frappe.db.sql(query)]
	}

@frappe.whitelist()
def approveftv(ftv):
	frappe.errprint(ftv)
	ftvs=eval(ftv)
	frappe.errprint(ftvs)
	for i in range(len(ftvs)):
		frappe.errprint(ftvs[i])
		ftvc=convert_ftv(ftvs[i])
		ftvc.save()
		frappe.db.sql("update `tabInvitees and Contacts` set convert_invitee_contact_to_ft=1 ,date_of_convert=CURDATE()where name='%s'"%(ftvs[i]))
	return "Done"

def convert_ftv(source_name, target_doc=None):
	target_doc = get_mapped_doc("Invitees and Contacts", source_name,
		{"Invitees and Contacts": {
			"doctype": "First Timer",
			"field_map": {
				"invitee_contact_name": "ftv_name",
				"designation":"designation",
				"address":"address_manual"
			}
		}}, target_doc)
	return target_doc


@frappe.whitelist()
def loadmemberdetails(invited_by):
	res=frappe.db.sql("select cell,senior_cell,pcf,church,church_group,zone,region from tabMember where name='%s'"%(invited_by))
	return res


@frappe.whitelist()
def loadrec():
	ftv1=[]
	import os
	for file in os.listdir("/home/gangadhar/Desktop/red5/webapps/openmeetings/streams/1"):
		if file.endswith(".wav"):
			ftv1.append(file)
	return ftv1
