# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint
from frappe.utils import getdate, validate_email_add, cint

class Member(Document):
	
	def on_update(self):
		usr_id=frappe.db.sql("select name from `tabUser` where name='%s'"%(self.email_id),as_list=1)
		if self.flag=='not':
			if self.member_designation=='Region Pastor':
				c_user = self.region
				r_user = 'Regional Pastor'
				perm = 'Region Master'
			elif self.member_designation=='Zone Pastor':
				c_user = self.zone
				r_user = 'Zonal Pastor'
				perm = 'Zone Master'
			elif self.member_designation=='Church Group Pastor':
				c_user = self.church_group
				r_user = 'Group Church Pastor'
				perm = 'Church Group Master'
			elif self.member_designation=='Church Pastor':
				c_user = self.church
				r_user = 'Church Pastor'
				perm = 'Church Master'
			elif self.member_designation=='PCF Leader':
				c_user = self.pcf
				r_user = 'PCF Leader'
				perm = 'PCF Master'
			elif self.member_designation=='Sr.Cell Leader':
				c_user = self.senior_cell
				r_user = 'Senior Cell Leader'
				perm = 'Senior Cell Master'
			elif self.member_designation=='Cell Leader':
				c_user = self.cell
				r_user = 'Cell Leader'
				perm = 'Cell Master'
			elif self.member_designation=='Member':
				c_user = self.name
				r_user = 'Member'
				perm = 'Member'
			elif self.member_designation=='Bible Study Class Teacher':
				c_user = self.church
				r_user = 'Bible Study Class Teacher'
				perm = 'Church Master'

			if not usr_id:
				u = frappe.new_doc("User")
				u.email=self.email_id
				u.first_name = self.member_name
				u.new_password = 'password'
				u.insert()
			r=frappe.new_doc("UserRole")
			r.parent=self.email_id
			r.parentfield='user_roles'
			r.parenttype='User'
			r.role=r_user
			r.insert()
			v = frappe.new_doc("DefaultValue")
			v.parentfield = 'system_defaults'
			v.parenttype = 'User Permission'
			v.parent = self.email_id
			v.defkey = perm
			v.defvalue = c_user 
			v.insert()
			frappe.db.sql("update `tabMember` set flag='SetPerm' where name='%s'"%(self.name))
			frappe.db.commit()

	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,church_group,church,pcf,senior_cell,name from `tabCell Master` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,church_group,church,pcf,senior_cell,name from `tabCell Master` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone,church,pcf,senior_cell,name from `tabCell Master` where church_group='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.church:
			value = frappe.db.sql("select region,zone,church_group,pcf,senior_cell,name from `tabCell Master` where church='%s'"%(self.church),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.pcf:
			value = frappe.db.sql("select region,zone,church_group,church,senior_cell,name from `tabCell Master` where pcf='%s'"%(self.pcf),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.senior_cell:
			value = frappe.db.sql("select region,zone,church_group,church,pcf,name from `tabCell Master` where senior_cell='%s'"%(self.senior_cell),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"pcf" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.cell:
			value = frappe.db.sql("select region,zone,church_group,church,pcf,senior_cell from `tabCell Master` where name='%s'"%(self.cell),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"pcf" : value[0][4],
					"senior_cell" : value[0][5]
				}
			return ret

def validate_birth(doc,method):
		#frappe.errprint("in date of birth ")
		if doc.date_of_birth and doc.date_of_join and getdate(doc.date_of_birth) >= getdate(doc.date_of_join):		
			frappe.throw(_("Date of Joining '{0}' must be greater than Date of Birth '{1}'").format(doc.date_of_join, doc.date_of_birth))
		
		if doc.baptisum_status=='Yes':
			if not doc.baptism_when or doc.baptism_where :
				frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))

		if self.email_id:
			if not validate_email_add(self.email_id):
				frappe.throw(_('{0} is not a valid email id').format(self.email_id))
