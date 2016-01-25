# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_add, cint
from frappe import throw, _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint, _
import frappe, os, json

class FirstTimer(Document):
	# pass
	def validate(self):
		if self.date_of_birth and self.date_of_visit and getdate(self.date_of_birth) >= getdate(self.date_of_visit):		
			frappe.throw(_("Date of First Visit '{0}' must be greater than Date of Birth '{1}'").format(self.date_of_visit, self.date_of_birth))

		# if self.baptisum_status=='Yes':
		# 	if not self.baptism_when or not self.baptism_where :
		# 		frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))

		if self.email_id:
			if not validate_email_add(self.email_id):
				frappe.throw(_('{0} is not a valid email id').format(self.email_id))


@frappe.whitelist()
def make_member(source_name, target_doc=None):
	return _make_member(source_name, target_doc)

def _make_member(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		pass

	doclist = get_mapped_doc("First Timer", source_name,
		{"First Timer": {
			"doctype": "Member",
			"field_map": {				
				"name":"ftv_id_no",
				"ftv_name":"member_name"
			}
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	return doclist

def validate_birth(doc,method):
		if doc.date_of_birth and doc.date_of_visit and getdate(doc.date_of_birth) >= getdate(doc.date_of_visit):		
			frappe.throw(_("Date of Visit '{0}' must be greater than Date of Birth '{1}'").format(doc.date_of_visit, doc.date_of_birth))
		# if doc.baptisum_status=='Yes':
		# 	if not doc.when or doc.where :
		# 		frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))

@frappe.whitelist()
def ismember(name):
	converted=frappe.db.sql("select name from `tabMember` where ftv_id_no='%s'"%(name))
	if converted:
		return "Yes"
	else:
		return "No"


@frappe.whitelist()
def set_higher_values(args):
    args = json.loads(args)
    mapper={
		"name":"cell_name,senior_cell,senior_cell_name,pcf,pcf_name,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name",
		"senior_cell":"senior_cell_name,pcf,pcf_name,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name",
		"pcf":"pcf_name,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name",
		"church":"church_name,church_group,group_church_name,zone,zone_name,region,region_name",
		"church_group":"group_church_name,zone,zone_name,region,region_name",
		"zone":"zone_name,region,region_name",
		"region":"region_name"
		}
    out = []
    for key, val in args.items():
    	out = frappe.db.sql("""select %s from `tabCells` where %s='%s'"""%(mapper[key],key,val),as_dict=1)
    if out:
          return out[0]


@frappe.whitelist()
def get_event_roles(doctype, txt, searchfield, start, page_len, filters):
    roles=frappe.get_roles(frappe.session.user)
    fltr=''
    if "System Manager" in roles :
 		fltr= "'Regional Pastor,Zonal Pastor,Bible Study Class Teacher,Foundation School Teacher,Partnership Rep,Welfare user,Call Center Operator,Group Church Pastor,Church Pastor,PCF Leader,Senior Cell Leader,Cell Leader,Member'"
    elif "Regional Pastor" in roles:
    	fltr= "'Zonal Pastor,Bible Study Class Teacher,Foundation School Teacher,Partnership Rep,Welfare user,Call Center Operator,Group Church Pastor,Church Pastor,PCF Leader,Senior Cell Leader,Cell Leader,Member'"

    elif "Zonal Pastor" in roles:
    	fltr= "'Bible Study Class Teacher,Foundation School Teacher,Partnership Rep,Welfare user,Call Center Operator,Group Church Pastor,Church Pastor,PCF Leader,Senior Cell Leader,Cell Leader,Member'"

    elif "Group Church Pastor" in roles:
    	fltr= "'Bible Study Class Teacher,Foundation School Teacher,Partnership Rep,Welfare user,Call Center Operator,Church Pastor,PCF Leader,Senior Cell Leader,Cell Leader,Member'"
    elif "Church Pastor" in roles:
    	fltr= "'Bible Study Class Teacher,Foundation School Teacher,Partnership Rep,Call Center Operator,Welfare user,PCF Leader,Senior Cell Leader,Cell Leader,Member'"
    elif "PCF Leader" in roles:
    	fltr= "'Senior Cell Leader,Cell Leader,Member'"
    elif "Senior Cell Leader" in roles:
    	fltr="'Cell Leader,Member'"
    elif "Cell Leader" in roles:
    	fltr= "'Member'"
   
    return frappe.db.sql("select name from tabRole where name in (%s)"%("','".join(fltr.split(','))))


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return None
	else:
		abc="""
			`tabFirst Timer`.cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Cells')
			or
			`tabFirst Timer`.senior_cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Senior Cells')
			or
			`tabFirst Timer`.pcf=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='PCFs')
			or
			`tabFirst Timer`.church=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Churches')
			or
			`tabFirst Timer`.church_group=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Group Churches')
			or
			`tabFirst Timer`.zone=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Zones')
			or
			`tabFirst Timer`.region=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Regions')
			or 
			`tabFirst Timer`.ftv_owner=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Member')
			""" % {
				"user": frappe.db.escape(user),
				"roles": "', '".join([frappe.db.escape(r) for r in frappe.get_roles(user)])
			}
		return abc

def has_permission(doc, user):

	if "System Manager" in frappe.get_roles(user):
		return True

	if doc.cell:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Cells'"%(user))
		if res:
			return True

	if doc.senior_cell:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Senior Cells'"%(user))
		if res:
			return True

	if doc.pcf:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='PCFs'"%(user))
		if res:
			return True

	if doc.church:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Churches'"%(user))
		if res:
			return True

	if doc.church_group:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Churches'"%(user))
		if res:
			return True

	if doc.zone:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Churches'"%(user))
		if res:
			return True

	if doc.region:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Churches'"%(user))
		if res:
			return True
	if doc.ftv_owner:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Member'"%(user))
		if res:
			return True

	return False
