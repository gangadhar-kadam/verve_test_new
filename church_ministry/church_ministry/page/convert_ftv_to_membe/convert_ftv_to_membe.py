# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.desk.reportview import get_match_cond
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def loadftv():
	query="select name,ftv_name,sex,date_of_birth from `tabFirst Time Visitor` where approved=1 and name not in (select ftv_id_no from tabMember)"
	return {
		"ftv": [frappe.db.sql(query)]
	}

@frappe.whitelist()
def approveftv(ftv):
	ftvs=eval(ftv)
	for i in range(len(ftvs)):
		ftvc=convert_ftv(ftvs[i])
		ftvc.save()
	return "Done"

def convert_ftv(source_name, target_doc=None):
	target_doc = get_mapped_doc("First Time Visitor", source_name,
		{"First Time Visitor": {
			"doctype": "Member",
			"field_map": {
				"ftv_name": "member_name",
				"name": "ftv_id_no",
				"address_manual":"home_address",
				"date_of_visit":"date_of_join"
			}
		}}, target_doc)
	return target_doc
