# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.desk.reportview import get_match_cond
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def loadftv():
	return {
		"ftv": [frappe.db.sql("select name,ftv_name,sex,date_of_birth from `tabFirst Time Visitor` where (approved=0 or  approved is null) and name in (select member from (select count(member) as count,member from `tabInvitation Member Details` where  member like 'FTV%' and present=1 group by member) a where a.count>=3)")]
	}

@frappe.whitelist()
def approveftv(ftv):
	ftvs=eval(ftv)
	for i in range(len(ftvs)):    
		frappe.db.sql("""update `tabFirst Time Visitor` set approved=1,date_of_approval=CURDATE() where name='%s' """ % (ftvs[i]))
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
				"date_of_visit":"date_of_join",
				"member_designation":"Member"
			}
		}}, target_doc)
	return target_doc
