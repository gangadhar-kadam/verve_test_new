# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, cint,getdate,nowdate
from frappe import throw, _, msgprint

class FoundationSchoolClassAttendance(Document):
	pass


@frappe.whitelist()
def loadftv(church,visitor_type,foundation__exam):
	school_status=''
	if foundation__exam=='Class 1':
		school_status='Nil'
	elif foundation__exam=='Class 2':
		school_status='Completed Class 1'
	elif foundation__exam=='Class 3':
		school_status='Completed Class 1&2'
	elif foundation__exam=='Class 4':
		school_status='Completed Class 1, 2 & 3'
	elif foundation__exam=='Class 5':
		school_status='Completed Class 1, 2 , 3 & 4'
	elif foundation__exam=='Class 6':
		school_status='Completed Class 1, 2 , 3 , 4 & 5'
	if visitor_type=='FTV':
		return {
		"ftv": [frappe.db.sql("select name,ftv_name from `tabFirst Timer` where church='%s' and school_status='%s' and approved=0"%(church,school_status))]
		}
	else:
		return {
		"ftv": [frappe.db.sql("select name,member_name from `tabMember` where church='%s' and school_status='%s'"%(church,school_status))]
		}

def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabFoundation School Class Attendance` where fc_class='%s' and church='%s' and date='%s' and docstatus!=2"%(doc.fc_class,doc.church,doc.date))
		if res:
			frappe.throw(_("Another Foundation School Class Attendance '{0}' With Class Name '{1}' , Cell Code '{2}' and date  '{3}'..!").format(res[0][0],doc.fc_class,doc.church,doc.date))
	today=nowdate()
	if getdate(doc.date) >= getdate(today):		
		frappe.throw(_("Calss Date Should not be Future date"))

def update_attendance(doc,method):
	for d in doc.get('attendance'):	
		if doc.visitor_type=='FTV':
			ftvdetails=frappe.db.sql("select ftv_name,email_id,phone_1 from `tabFirst Timer` where name='%s'"%(d.ftv_id))
		else:
			ftvdetails=frappe.db.sql("select member_name,email_id,phone_1 from `tabMember` where name='%s'"%(d.member_id))
		msg_member="""Hello %s,<br><br>
		You have '%s' for Foundation Class '%s' <br><br>Regards,<br>Verve
		"""%(ftvdetails[0][0],d.attendance,doc.fc_class)
		frappe.sendmail(recipients=ftvdetails[0][1], sender='gangadhar.k@indictranstech.com', content=msg_member, subject='Verve Class Attendance')
		from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
		receiver_list=[]
		baptism=''
		if d.baptism_when and d.baptism_where:
			baptism=", baptisum_status='Yes' , baptism_when='"+d.baptism_when+"' , baptism_where='"+cstr(d.baptism_where)+"' "
		if d.attendance=='Present':
			if doc.fc_class=='Class 1':
				exm='Completed Class 1'
			elif doc.fc_class=='Class 2':
				exm='Completed Class 1&2'
			elif doc.fc_class=='Class 3':
				exm='Completed Class 1, 2 & 3'
			elif doc.fc_class=='Class 4':
				exm='Completed Class 1, 2 , 3 & 4'
			elif doc.fc_class=='Class 5':
				exm='Completed Class 1, 2 , 3 , 4 & 5'
			elif doc.fc_class=='Class 6':
				exm='Completed All Classes and Passed Exam'
			if doc.visitor_type=='FTV':
				frappe.db.sql("""update `tabFirst Timer` set school_status='%s' %s where name='%s' """ % (exm,baptism,d.ftv_id),debug=1)
			else:
				frappe.db.sql("""update `tabMember` set school_status='%s' %s where name='%s' """ % (exm, baptism, d.member_id))
		if ftvdetails[0][2]:
			receiver_list.append(ftvdetails[0][2])			
			send_sms(receiver_list, cstr(msg_member))
	return "Done"
			


