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
	val=frappe.db.sql("select defkey,defvalue from `tabDefaultValue` where defkey in ('Cells','Senior Cells','PCFs','Churches','Group Churches','Zones','Regions') and parent='%s' limit 1"%(frappe.user.name))
	#frappe.errprint(val)
	if val:
		if val[0][0]=='Cells':
			key='cell'
			value=val[0][1]
		elif val[0][0]=='Senior Cells':
			key='senior_cell'
			value=val[0][1]
		elif val[0][0]=='PCFs':
			key='pcf'
			value=val[0][1]
		elif val[0][0]=='Churches':
			key='Church'
			value=val[0][1]
		elif val[0][0]=='Group Churches':
			key='church_group'
			value=val[0][1]
		elif val[0][0]=='Zones':
			key='zone'
			value=val[0][1]
		elif val[0][0]=='Regions':
			key='region'
			value=val[0][1]
		return {
		"ftv": [frappe.db.sql("select name,ftv_name,sex,date_of_birth,age_group from `tabFirst Timer` where (approved=0 or  approved is null) and name in (select member from (select count(a.member) as count,a.member from `tabInvitation Member Details` a, `tabAttendance Record` b where a.parent= b.name and b.attendance_type='Meeting Attendance' and a.docstatus=1 and a.member like 'FT%' and a.present=1 group by a.member) a where a.count>=3) and "+key+"='"+value+"'")]
		}
	else:
		return {
			"ftv": [frappe.db.sql("select name,ftv_name,sex,date_of_birth,age_group from `tabFirst Timer` where (approved=0 or  approved is null) and name in (select member from (select count(a.member) as count,a.member from `tabInvitation Member Details` a, `tabAttendance Record` b where a.parent= b.name and b.attendance_type='Meeting Attendance' and a.docstatus=1 and a.member like 'FT%' and a.present=1 group by a.member) a where a.count>=3)")]
		}

@frappe.whitelist()
def approveftv(ftv):
	ftvs=eval(ftv)
	for i in range(len(ftvs)):
		res=frappe.db.sql("""select name from `tabFirst Timer` where name='%s' and cell is not null and senior_cell is not null and pcf is not null""" % (ftvs[i])) 
		if res:
			ftvc=convert_ftv(ftvs[i])
			ftvc.save()
			frappe.db.sql("""update `tabFirst Timer` set approved=1,date_of_approval=CURDATE() where name='%s' """ % (ftvs[i]))
		else:
			frappe.msgprint("The Cell or Senior Cell or PCF for %s is not set . Please update it before conversion"%ftvs[i])
	return "Done"


def convert_ftv(source_name, target_doc=None):
	target_doc = get_mapped_doc("First Timer", source_name,
		{"First Timer": {
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
