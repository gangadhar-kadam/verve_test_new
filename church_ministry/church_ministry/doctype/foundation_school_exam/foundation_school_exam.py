# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, cint,getdate,nowdate
from frappe import throw, _, msgprint

class FoundationSchoolExam(Document):
	
	def get_grade(self,score):
			query="select name from `tabFoundation School Grades` where to_score>='"+cstr(score)+"' and from_score<='"+cstr(score)+"'"
			grade = frappe.db.sql(query)
			if not grade:
				frappe.msgprint(_("Grade not found for the score {0}").format(score))
			return {
				"grade": grade[0][0]
			}
	
@frappe.whitelist()
def get_grade(score):
			query="select name from `tabFoundation School Grades` where to_score>='"+cstr(score)+"' and from_score<='"+cstr(score)+"'"
			grade = frappe.db.sql(query)
			if not grade:
				frappe.msgprint(_("Grade not found for the score {0}").format(score))
			return {
				"grade": grade[0][0]
			}

@frappe.whitelist()
def loadftv(church,visitor_type):
 	if visitor_type=='FTV':
		return {
		"ftv": [frappe.db.sql("select name,ftv_name,cell from `tabFirst Timer` where church='%s' and school_status='Completed Class 1, 2 , 3 , 4 , 5 & 6' and approved=0"%(church))]
		}
	else:
		return {
		"ftv": [frappe.db.sql("select name,member_name,cell from `tabMember` where church='%s' and school_status='Completed Class 1, 2 , 3 , 4 , 5 & 6'"%(church))]
		}

def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabFoundation School Exam` where foundation__exam='%s' and church='%s' and date='%s' and docstatus!=2"%(doc.foundation__exam,doc.church,doc.date))
		if res:
			frappe.throw(_("Another Foundation School Exam '{0}' With Exam Name '{1}' , church Code '{2}' and date  '{3}' exist..!").format(res[0][0],doc.foundation__exam,doc.church,doc.date))
	today=nowdate()
	if getdate(doc.date) >= getdate(today):		
		frappe.throw(_("Exam Date Should not be Future date"))

def update_attendance(doc,method):
	for d in doc.get('attendance'):
		greeting=''
		if d.grade!='D':
			greeting='Congratulations..!'
		else:
			greeting='Sorry..! You Failed.'
		if doc.visitor_type=='FTV':
			ftvdetails=frappe.db.sql("select ftv_name,email_id,phone_1 from `tabFirst Timer` where name='%s'"%(d.ftv_id))
		else:
			ftvdetails=frappe.db.sql("select member_name,email_id,phone_1 from `tabMember` where name='%s'"%(d.member_id))
		msg_member="""Hello %s,<br><br>
		%s You have grade '%s' in exam '%s' <br><br>Regards,<br>Verve
		"""%(ftvdetails[0][0],greeting,d.grade,doc.foundation__exam)
		frappe.sendmail(recipients=ftvdetails[0][1], sender='gangadhar.k@indictranstech.com', content=msg_member, subject='Verve Exam Result')
		from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
		receiver_list=[]
		baptism=''
		if d.baptism_when and d.baptism_where:
			baptism=", baptisum_status='Yes' , baptism_when='"+d.baptism_when+"' , baptism_where='"+cstr(d.baptism_where)+"' "
			# frappe.errprint(baptism)
		if d.grade!='D':
			exm=''
			if doc.foundation__exam=='Class 1':
				exm='Completed Class 1'
			elif doc.foundation__exam=='Class 2':
				exm='Completed Class 1&2'
			elif doc.foundation__exam=='Class 3':
				exm='Completed Class 1, 2 & 3'
			elif doc.foundation__exam=='Class 4':
				exm='Completed Class 1, 2 , 3 & 4'
			elif doc.foundation__exam=='Class 5':
				exm='Completed Class 1, 2 , 3 , 4 & 5'
			elif doc.foundation__exam=='Class 6':
				exm='Completed All Classes and Passed Exam'
			if doc.visitor_type=='FTV':
				frappe.db.sql("""update `tabFirst Timer` set school_status='%s' %s where name='%s' """ % (exm,baptism,d.ftv_id))
			else:
				frappe.db.sql("""update `tabMember` set school_status='%s' %s where name='%s' """ % (exm, baptism, d.member_id))
		
		if ftvdetails[0][2]:
			receiver_list.append(ftvdetails[0][2])			
			send_sms(receiver_list, cstr(msg_member))
	return "Done"
