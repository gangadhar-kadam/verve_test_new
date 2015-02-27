# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.desk.reportview import get_match_cond

@frappe.whitelist()
def loadftv():
	return {
		"ftv": [frappe.db.sql("select name,ftv_name,sex,date_of_birth from `tabFirst Time Visitor` where (approved=0 or  approved is null) and name in (select member from (select count(member) as count,member from `tabInvitation Member Details` where  member like 'FTV%' and present=1 group by member) a where a.count>0)")]
	}

@frappe.whitelist()
def approveftv(ftv):
	ftvs=eval(ftv)
	for i in range(len(ftvs)):    
		frappe.db.sql("""update `tabFirst Time Visitor` set approved=1,date_of_approval=CURDATE() where name='%s' """ % (ftvs[i]))
	return "Done"
