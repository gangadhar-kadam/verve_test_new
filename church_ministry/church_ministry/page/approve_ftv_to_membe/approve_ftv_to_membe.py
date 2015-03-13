# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.desk.reportview import get_match_cond
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def loadftv():
	# frappe.errprint(frappe.user.name)
	roles=frappe.get_roles(frappe.user.name)
	# frappe.errprint(frappe.get_roles(frappe.user.name))
	# frappe.errprint('Cell Leader' in roles)
	val=frappe.db.sql("select defkey,defvalue from `tabDefaultValue` where defkey in ('Cell Master','Senior Cell Master','PCF Master','Church Master','Church Group Master','Zone Master','Region Master') and parent='%s' limit 1"%(frappe.user.name))
	frappe.errprint(val)
	if val:
		if val[0][0]=='Cell Master':
			key='cell'
			value=val[0][1]
		elif val[0][0]=='Senior Cell Master':
			key='senior_cell'
			value=val[0][1]
		elif val[0][0]=='PCF Master':
			key='pcf'
			value=val[0][1]
		elif val[0][0]=='Church Master':
			key='Church'
			value=val[0][1]
		elif val[0][0]=='Church Group Master':
			key='church_group'
			value=val[0][1]
		elif val[0][0]=='Zone Master':
			key='zone'
			value=val[0][1]
		elif val[0][0]=='Region Master':
			key='region'
			value=val[0][1]
		return {
		"ftv": [frappe.db.sql("select name,ftv_name,sex,date_of_birth from `tabFirst Time Visitor` where (approved=0 or  approved is null) and name in (select member from (select count(member) as count,member from `tabInvitation Member Details` where  member like 'FTV%' and present=1 group by member) a where a.count>=3) and '"+key+"'='"+value+"'")]
		}
	else:
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
