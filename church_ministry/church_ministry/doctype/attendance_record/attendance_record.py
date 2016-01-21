# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import throw, _, msgprint
import frappe.share
from frappe.utils import cstr,now,add_days,nowdate,cint

class AttendanceRecord(Document):
	def validate(self):
		if self.attendance_type=='Meeting Attendance':
			if (not self.cell ) :
				frappe.throw(_("Please enter Cell "))
		self.valedate_dates()
		self.validate_meetings()

	def valedate_dates(self):
		if self.from_date:
			if self.from_date < nowdate():
				frappe.throw(_("From Date should be todays or greater than todays date."))
				
		if self.from_date:
			if self.from_date > self.to_date:
				frappe.throw(_("To Date should be greater than start date."))

	def validate_meetings(self):
		if self.meeting_category=="Cell Meeting" and not self.meeting_subject:
			frappe.throw(_("Please Enter Meeting Subject before save document.!"))

		if self.meeting_category=="Church Meeting" and not self.meeting_sub:
			frappe.throw(_("Please Enter Meeting Subject before save document.!"))


	def on_update(self):
	# def validate_event_dates(self):
		event_data = frappe.db.sql("""select sh.date from `tabEvent` e, `tabEvent Schedule` sh where 
				sh.parent = '%s' and sh.parent=e.name"""%(self.event),as_list=1)
		# frappe.errprint(event_data[0][0])
		att_data = frappe.db.sql("""select name,from_date,to_date from `tabAttendance Record` where 
				attendance_type = 'Event Attendance' and event = '%s' """%(self.event),as_list=1)
		# frappe.errprint(att_data)

	def autoname(self):
		from frappe.model.naming import make_autoname
		if self.attendance_type=='Event Attendance':
			sub=self.meeting_sub[:3].upper()
			self.name = make_autoname('EVATT' + '.####')
		else:
			if self.meeting_category=='Cell Meeting':
				self.name = make_autoname(self.cell + '/' + 'CELL' + 'ATT' + '.####')
			else :
				sub=self.meeting_sub[:3].upper()
				self.name = make_autoname(self.cell + '/' + sub + 'ATT' + '.####')			
	
	def load_participents(self):
		self.set('invitation_member_details', [])
		member_ftv=''
		if self.cell:
			member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Timer` where cell='%s' and approved=0 union select name,member_name,email_id from `tabMember` where cell='%s' "%(self.cell,self.cell))
		elif self.church:
			member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Timer` where church='%s' and approved=0 union select name,member_name,email_id from `tabMember` where church='%s'"%(self.church,self.church))	
		for d in member_ftv:
			child = self.append('invitation_member_details', {})
			child.member = d[0]
			child.member_name = d[1]
			child.email_id = d[2]


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		if not doc.invitation_member_details:
			doc.load_participents()
		fdate=doc.from_date.split(" ")
		f_date=fdate[0]
		tdate=doc.to_date.split(" ")
		t_date=tdate[0]
		res=frappe.db.sql("select name from `tabAttendance Record` where (cell='%s' or church='%s') and from_date like '%s%%' and to_date like '%s%%'"%(doc.cell,doc.church,f_date,t_date))
		#frappe.errprint(res)
		if res:
			frappe.throw(_("Attendance Record '{0}' is already created for same details on same date '{1}'").format(res[0][0],f_date))

		if doc.from_date and doc.to_date:
			if doc.from_date >= doc.to_date:
				frappe.throw(_("To Date should be greater than From Date..!"))

		if len(doc.invitation_member_details)<1:
			pass
			#rappe.throw(_("Attendance Member table is empty.There should be at least 1 member in attendance list. Please load members in table."))

		if doc.data_17 and cint(doc.data_17) <= 0 :
				frappe.throw(_("Total Attendance cannot be negative..!"))
		if doc.number_of_first_timers and cint(doc.number_of_first_timers) <= 0 :
				frappe.throw(_("Number of First Timers cannot be negative..!"))
		if doc.data_19 and cint(doc.data_19) <= 0 :
				frappe.throw(_("Number of New Converts cannot be negative..!"))
		if doc.data_20 and cint(doc.data_20) <= 0 :
				frappe.throw(_("Total Cell Offering cannot be negative..!"))


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return None
	else:
		abc="""
			`tabAttendance Record`.cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Cells')
			or
			`tabAttendance Record`.senior_cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Senior Cells')
			or
			`tabAttendance Record`.pcf=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='PCFs')
			or
			`tabAttendance Record`.church=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Churches')
			or
			`tabAttendance Record`.church_group=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Group Churches')
			or
			`tabAttendance Record`.zone=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Zones')
			or
			`tabAttendance Record`.region=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Regions')
			""" % {
				"user": frappe.db.escape(user),
				"roles": "', '".join([frappe.db.escape(r) for r in frappe.get_roles(user)])
			}
		frappe.errprint(abc)
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

	return False
