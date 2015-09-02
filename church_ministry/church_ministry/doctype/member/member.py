# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe import throw, _, msgprint
from erpnext.accounts.utils import get_fiscal_year
from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
from frappe.utils import getdate, validate_email_add, cint,cstr,now,flt, nowdate
import base64
from gcm import GCM

class Member(Document):

	
	def on_update(self):
		# pass
		usr_id=frappe.db.sql("select name from `tabUser` where name='%s'"%(self.email_id),as_list=1)
		if self.flag=='not' and self.email_id:
			# frappe.errprint("user creation")
			# if  self.member_designation=='PCF Leader':
			# 	c_user = self.pcf
			# 	r_user = 'PCF Leader'
			# 	perm = 'PCFs'
			# elif self.member_designation=='Sr.Cell Leader':
			# 	c_user = self.senior_cell
			# 	r_user = 'Senior Cell Leader'
			# 	perm = 'Senior Cells'
			# elif self.member_designation=='Cell Leader':
			# 	c_user = self.cell
			# 	r_user = 'Cell Leader'
			# 	perm = 'Cells'
			# elif self.member_designation=='Member':
			# 	c_user = self.name
			# 	r_user = 'Member'
			# 	perm = 'Member'
			# elif self.member_designation=='Bible Study Class Teacher':
			# 	c_user = self.church
			# 	r_user = 'Bible Study Class Teacher'
			# 	perm = 'Churches'

			if not usr_id:
				u = frappe.new_doc("User")
				u.email=self.email_id
				u.first_name = self.member_name
				u.new_password = 'password'
				frappe.flags.mute_emails = False
				u.insert()
				frappe.flags.mute_emails = True
			r=frappe.new_doc("UserRole")
			r.parent=self.email_id
			r.parentfield='user_roles'
			r.parenttype='User'
			r.role='Member'
			r.insert()
			v = frappe.new_doc("DefaultValue")
			v.parentfield = 'system_defaults'
			v.parenttype = 'User Permission'
			v.parent = self.email_id
			v.defkey = 'Member'
			v.defvalue = self.name 
			v.insert()
			frappe.db.sql("update `tabMember` set flag='SetPerm' where name='%s'"%(self.name))
			frappe.db.commit()
			self.user_id = self.email_id

def get_list(doctype, txt, searchfield, start, page_len, filters):
	conditions=get_conditions(filters)
	if conditions:
		value=frappe.db.sql("select name from `tab%s` where %s"%(filters.get('doctype'),conditions))
		return value
	else :
		value=frappe.db.sql("select name from `tab%s`"%(filters.get('doctype')))
		return value


def get_conditions(filters):
	cond=[]
	if filters.get('cell'):
		cond.append('cell="%s"'%(filters.get('cell')))
	elif filters.get('senior_cell'):
		cond.append('senior_cell="%s"'%(filters.get('senior_cell')))
	elif filters.get('pcf'):
		cond.append('pcf="%s"'%(filters.get('pcf')))
	elif filters.get('church'):
		cond.append('church="%s"'%(filters.get('church')))
	elif filters.get('church_group'):
		cond.append('church_group="%s"'%(filters.get('church_group')))
	elif filters.get('zone'):
		cond.append('zone="%s"'%(filters.get('zone')))
	elif filters.get('region'):
		cond.append('region="%s"'%(filters.get('region')))
	return ' or '.join(cond)  


def validate_birth(doc,method):
		#frappe.errprint("in date of birth ")
		if doc.date_of_birth and doc.date_of_join and getdate(doc.date_of_birth) >= getdate(doc.date_of_join):		
			frappe.throw(_("Date of Joining '{0}' must be greater than Date of Birth '{1}'").format(doc.date_of_join, doc.date_of_birth))
		
		# if doc.baptisum_status=='Yes':
		# 	if not doc.baptism_when or not doc.baptism_where :
		# 		frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))

		if doc.email_id:
			if not validate_email_add(doc.email_id):
				frappe.throw(_('{0} is not a valid email id').format(doc.email_id))


@frappe.whitelist(allow_guest=True)
def get_attendance_points(args):
	"""
	Get employee id and return points according to his attendance assumed the working days are 365 and points are 100
	"""
	frappe.errprint("deleting documents")
	frappe.delete_doc('DocType','Employee task Details')
	frappe.errprint("deleted Call Center Details")
	present,working=0,0
	total_att=frappe.db.sql("select count(name) as attendance from `tabAttendance` where status='Present' and fiscal_year=%(fiscal_year)s and employee=%(user)s", {"user":args,"fiscal_year":get_fiscal_year(nowdate())[0]},as_list=True)
	holidays=frappe.db.sql("select count(a.name) from tabHoliday a,`tabHoliday List` b where b.name=a.parent and fiscal_year=EXTRACT(YEAR FROM CURDATE()) and is_default=1")
	if holidays:
		global working
		working=365-holidays[0][0]
	if total_att:
		global present
		present =total_att[0][0]
	points=(100.00*present)/working
	return round(points,2)




### web sevices
# gangadhar

@frappe.whitelist(allow_guest=True)
def user_roles(data):
	"""
	Get user name and password from user and returns roles and its def key and defvalue
	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	if not valid:
		return {
			"status":"401",
			"message":"User name or Password is incorrect"
		}
	else:
		data={}
		roles=frappe.db.sql("select role from `tabUserRole` where parent=%(user)s", {"user":dts['username']},as_dict=True)
		data['roles']=roles
		qry="select defkey,defvalue from `tabDefaultValue`  where defkey not like '_list_settings:%' and defkey not like '_desktop_items%' and parent='"+dts['username']+"'"
		user_values=frappe.db.sql(qry,as_dict=True)
		#user_values=frappe.db.sql("select defkey,defvalue from `tabDefaultValue`  where parent=%(user)s", {"user":dts['username']},as_dict=True)
		data['user_values']=user_values
		return data



@frappe.whitelist(allow_guest=True)
def create_senior_cells(data):
	"""
	Need to check validation/ duplication  etc

	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	if not valid:
		return {
		  "status":"401",
		  "message":"User name or Password is incorrect"
		}
        if not frappe.has_permission(doctype="Senior Cells", ptype="create",user=dts['username']):
                return {
                  "status":"403",
                  "message":"You have no permission to create Senior Cell"
                }
	else:
		obj=frappe.new_doc("Senior Cells")
		obj.senior_cell_name=dts['senior_cell_name']
		obj.senior_cell_code=dts['senior_cell_code']
		obj.meeting_location=dts['meeting_location']
		obj.zone=dts['zone']
		obj.region=dts['region']
		obj.church_group=dts['church_group']
		obj.church=dts['church']
		obj.pcf=dts['pcf']
		obj.contact_phone_no=dts['contact_phone_no']
		obj.contact_email_id=dts['contact_email_id']
		obj.insert(ignore_permissions=True)
		return "Successfully created senior Cell '"+obj.name+"'"
		                


@frappe.whitelist(allow_guest=True)
def create_cells(data):
	"""
	Need to check validation/ duplication  etc

	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	if not valid:
		return {
		  "status":"401",
		  "message":"User name or Password is incorrect"
		}
        if not frappe.has_permission(doctype="Cells", ptype="create",user=dts['username']):
                return {
                  "status":"403",
                  "message":"You have no permission to create Senior Cell"
                }

	else:
		obj=frappe.new_doc("Cells")
		obj.cell_name=dts['cell_name']
		obj.cell_code=dts['cell_code']
		obj.meeting_location=dts['meeting_location']
		obj.address=dts['address']
		obj.senior_cell=dts['senior_cell']
		obj.zone=dts['zone']
		obj.region=dts['region']
		obj.church_group=dts['church_group']
		obj.church=dts['church']
		obj.pcf=dts['pcf']
		obj.contact_phone_no=dts['contact_phone_no']
		obj.contact_email_id=dts['contact_email_id']
		obj.insert(ignore_permissions=True)
		ret={
			"message":"Successfully created Cell '"+obj.name+"'"
		}
		return ret



@frappe.whitelist(allow_guest=True)
def create_event(data):
        """
        Need to check validation/ duplication  etc
        """
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        if not frappe.has_permission(doctype="Event", ptype="create",user=dts['username']):
                return {
                  "status":"403",
                  "message":"You have no permission to create Cell"
                }
        else:
                obj=frappe.new_doc("Event")
                obj.subject=dts['subject']
                #obj.type=dts['type']
                obj.starts_on=dts['starts_on']
                obj.ends_on=dts['ends_on']
                obj.address=dts['address']
                obj.description=dts['description']
                obj.insert(ignore_permissions=True)
                ret={
                        "message":"Successfully created Event '"+obj.name+"'"
                }
                return ret

@frappe.whitelist(allow_guest=True)
def update_event(data):
        """
        Need to check validation/ duplication  etc
        """
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        if not frappe.has_permission(doctype="Event", ptype="create",user=dts['username']):
                return {
                  "status":"403",
                  "message":"You have no permission to create Cell"
                }
        else:
                obj=frappe.get_doc("Event",dts['name'])
                obj.subject=dts['subject']
                obj.type=dts['type']
                obj.starts_on=dts['starts_on']
                obj.ends_on=dts['ends_on']
                obj.address=dts['address']
                obj.description=dts['description']
                obj.save(ignore_permissions=True)
                ret={
                        "message":"Successfully updated Event '"+obj.name+"'"
                }
                return ret

@frappe.whitelist(allow_guest=True)
def create_meetings(data):
	"""
	No Need to send sms,push notification and email , it should be on attendence update on every user.
        Need to check validation/ duplication  etc
	"""
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }

	if not frappe.has_permission(doctype="Attendance Record", ptype="create",user=dts['username']):
		        return {
				"status":"403",
				"message":"You have no permission to create Meeting Attendance Record"
		        }
	#return "hello"
        fdate=dts['from_date'].split(" ")
        f_date=fdate[0]
        tdate=dts['to_date'].split(" ")
        t_date=tdate[0]
        res=frappe.db.sql("select name from `tabAttendance Record` where (cell='%s' or church='%s') and from_date like '%s%%' and to_date like '%s%%'"%(dts['cell'],dts['church'],f_date,t_date))
        if res:
            return {
                "status":"401",
                "message":"Attendance Record is already created for same details on same date "
                }
        if dts['from_date'] and dts['to_date']:
            if dts['from_date'] >= dts['to_date']:
                return {
                "status":"402",
                "message":"To Date should be greater than From Date..!"
                }	
        #return "hello"
	print data
        obj=frappe.new_doc("Attendance Record")
        obj.meeting_category=dts['meeting_category']
	if dts['meeting_category']=="Cell Meeting":
		obj.meeting_subject=dts['meeting_sub']
	else:
	        obj.meeting_sub=dts['meeting_sub']
        obj.from_date=f_date
        obj.to_date=t_date
        obj.venue=dts['venue']
        obj.cell=dts['cell']
        obj.senior_cell=dts['senior_cell']
        obj.zone=dts['zone']
        obj.region=dts['region']
        obj.church_group=dts['church_group']
        obj.church=dts['church']
        obj.pcf=dts['pcf']
        obj.insert(ignore_permissions=True)
	print "Successfully created Cell '"+obj.name+"'"
        ret={
                        "message":"Successfully created Cell '"+obj.name+"'"
        }
        return ret


@frappe.whitelist(allow_guest=True)
def meetings_list(data):
	"""
	Need to add filter of permitted records for user
	"""
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
               qry="select name as meeting_name,meeting_subject , from_date as meeting_date ,venue from `tabAttendance Record` where attendance_type='Meeting Attendance'"
               data=frappe.db.sql(qry,as_dict=True)
               return data


@frappe.whitelist(allow_guest=True)
def meetings_members(data):
	"""
	Get all participents of selected meeting
	"""
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
                data=frappe.db.sql("select b.name,b.member,b.member_name,b.present from `tabAttendance Record` a,`tabInvitation Member Details` b  where a.name=b.parent and  a.name=%s",dts['meeting_id'],as_dict=True)
                return data


@frappe.whitelist(allow_guest=True)
def meetings_attendance(data):
	# frappe.errprint("notify")
	"""
	Need to add provision to send sms,push notification and emails on present and absent
	"""
        dts=json.loads(data)
        # frappe.errprint(dts)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        frappe.errprint(valid)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
        	for record in dts['records']:
        		if record['present']=='0' or record['present']=='1' :
        			frappe.db.sql("update `tabInvitation Member Details` set present=%s where name=%s",(record['present'],record['name']))
				mail_notify_msg = """Dear User, \n\n \t\t Your Attendance is updated by Leader '%s'. Please Check. \n\n Records, \n\n Love World Synergy"""%(dts['username'])
				membr = frappe.db.sql("select member,email_id from `tabInvitation Member Details` where name=%s",(record['name']),as_list=1)
				frappe.errprint(membr)
				notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field = 'attendance_updated_by_leader'""",as_list=1)
				# user = frappe.db.sql("""select parent from `tabDefaultValue` where defkey='Cells' and 
				# 	defvalue in (select cell from `tabMember` where email_id='%s')"""%(dts['username']),as_list=1)
				user = frappe.db.sql("""select phone_1 from `tabMember` where email_id='%s'"""%(membr[0][1]),as_list=1)
				if user:
					if "Email" in notify[0][0]:
						frappe.sendmail(recipients=membr[0][1], content=mail_notify_msg, subject='Attendance Record Update Notification')
					if "SMS" in notify[0][0]:
						send_sms(user[0], mail_notify_msg)
					if "Push Notification" in notify[0][0]:
						data={}
						data['Message']=mail_notify_msg
						gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
						res=frappe.db.sql("select device_id from tabUser where name ='%s'" %(user[0][0]),as_list=1)
						# frappe.errprint(res)
						if res:
							res = gcm.json_request(registration_ids=res, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)
			return "Updated Attendance"


@frappe.whitelist(allow_guest=True)
def meetings_list_member(data):
	"""
	Meeting list of member user
	"""
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
        	frappe.errprint(dts)
        	data=frappe.db.sql("select a.name as meeting_name,a.meeting_category as meeting_category, a.meeting_subject as meeting_subject,a.from_date as from_date,a.to_date as to_date,a.venue as venue,b.name as name,ifnull(b.present,0) as present, b.member from `tabAttendance Record`  a,`tabInvitation Member Details` b where a.name=b.parent and b.email_id=%s",dts['username'],as_dict=True)
        	return data


@frappe.whitelist(allow_guest=True)
def mark_my_attendance(data):
	"""
	Member can mark their attandence of meeting
	"""
        dts=json.loads(data)
        frappe.errprint("hi")
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
			for record in dts['records']:
				# print(record['present'])
				if not record['present']:
					record['present']=0
					frappe.db.sql("update `tabInvitation Member Details` set present=%s where name=%s",(record['present'],record['name']))
				mail_notify_msg = """Dear User, \n\n \t\tYour Attendance is updated by Member '%s'. Please Check. \n\n Records, \n\n Love World Synergy"""%(dts['username'])
				notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field='attendance_updated_by_member'""",as_list=1)
				membr = frappe.db.sql("select member,email_id from `tabInvitation Member Details` where name=%s",(record['name']),as_list=1)
				user = frappe.db.sql("""select parent from `tabDefaultValue` where defkey='Cells' and 
					defvalue in (select cell from `tabMember` where email_id='%s')"""%(membr[0][1]),as_list=1)
				if user:
					member_details = frappe.db.sql("""select phone_1 from `tabMember` where email_id='%s'"""%(user[0][0]),as_list=1)
					if "Email" in notify[0][0]:
						frappe.sendmail(recipients=user[0][0], content=mail_notify_msg, subject='Attendance Record Update Notification')
					if "SMS" in notify[0][0]:
						send_sms(member_details[0], mail_notify_msg)
					if "Push Notification" in notify[0][0]:
						data={}
						data['Message']=mail_notify_msg
						gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
						res=frappe.db.sql("select device_id from tabUser where name ='%s'" %(user[0][0]),as_list=1)
						if res:
							res = gcm.json_request(registration_ids=res, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)

				return "Updated Attendance"



@frappe.whitelist(allow_guest=True)
def get_masters(data):
	"""
	Member can mark their attandence of meeting
	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	if not valid:
		return {
				"status":"401",
				"message":"User name or Password is incorrect"
		}
    	match_conditions=get_match_conditions(dts['tbl'],dts['username'])
    	colmns=frappe.db.sql("select fieldname from tabDocField where fieldtype !='Section Break' and fieldtype !='Column Break' and parent='%s' and fieldname like '%%_name%%' order by idx limit 6 " %(dts['tbl']),as_list=1 )
    	if match_conditions   :
		cond =  ' or '.join(match_conditions) 
	else:
	        cond =' 1=1'	
	#return "hello"
	return frappe.db.sql("""select name ,%s from `tab%s` where %s"""%(','.join([x[0] for x in colmns ]),dts['tbl'], ' or '.join(match_conditions)), as_dict=1)


@frappe.whitelist(allow_guest=True)
def event_list(data):
    """
    Event List for user
    """
    dts=json.loads(data)
    from frappe.model.db_query import DatabaseQuery
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }    
    from frappe.desk.doctype.event.event import get_permission_query_conditions
    qry=" select name as event_name,address,starts_on as event_date,subject from tabEvent where "+get_permission_query_conditions(dts['username'])
    #return qry
    data=frappe.db.sql(qry,as_dict=True)
    return data

        
@frappe.whitelist(allow_guest=True)
def event_participents(data):
    """
    Event details og selected event
    """
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }       
    data=frappe.db.sql("select a.name as `name` ,a.member_name,ifnull(a.present,0) as present,a.comments from `tabInvitation Member Details`  a,`tabAttendance Record` b  where b.attendance_type='Event Attendance' and a.parent=b.name and b.event=%s",dts['event_id'],as_dict=True)
    return data
                

@frappe.whitelist(allow_guest=True)
def event_attendance(data):
    """
    Give provisin for sms email and push notification
    update Attendance Record
    """
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
       
    for record in dts['record']:
	#frappe.errprint(type(record))
	#return record
        if not record['present'] :
            record['present']=0
        frappe.db.sql("update `tabInvitation Member Details` set present=%s where id=%s",(record['present'],record['name']))
    return "Updated Attendance"

@frappe.whitelist(allow_guest=True)
def my_event_list(data):
    """
    Member Event list
    """
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }       
    data=frappe.db.sql("select a.subject ,a.starts_on as event_date, a.address,c.name,c.person_name,ifnull(c.present,0) as present,comments from `tabEvent` a, `tabAttendance Record` b,`tabInvitation Member Details` c \
                         where attendance_type='Event Attendance' and a.name=b.event_name and b.name=c.parent and c.id in (select a.name from tabMember a,tabUser b where a.email_id=b.name and b.name=%s) ",dts['username'],as_dict=True)
    return data

@frappe.whitelist(allow_guest=True)
def my_event_attendance(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }     
    for record in dts['records']:
        if not record['present'] :
            record['present']=0
        frappe.db.sql("update `tabInvitation Member Details` set present=%s where name=%s",(record['present'],record['name']))
    return "Updated Your Event Attendance"



@frappe.whitelist(allow_guest=True)
def get_hierarchy(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    dictnory={
        "Cells":"senior_cell,pcf,church,church_group,zone,region",
        "Senior Cells":"pcf,church,church_group,zone,region",
        "PCFs":"church,church_group,zone,region",
        "Churches":"church_group,zone,region",
        "Group Churches":"zone,region",
        "Zones":"region"
    }
    tablename=dts['tbl']
    res=frappe.db.sql("select %s from `tab%s` where name='%s'"  %(dictnory[tablename],dts['tbl'],dts['name']),as_dict=True)
    return res


@frappe.whitelist(allow_guest=True)
def get_lists(data):
    dts=json.loads(data)
    #print dts
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    wheres={
            "Senior Cells":"senior_cell",
            "PCFs":"pcf",
            "Churches":"church",
            "Group Churches":"church_group",
            "Zones":"zone",
            "Regions":"region"
    }
    tablename=dts['tbl']
    #fields={
    #        "Senior Cells":"name",
    #        "PCFs":"senior_cell",
    #        "Churches":"pcf",
    #        "Group Churches":"church",
    #        "Zones":"church_group",
    #        "Regions":"zone"
    #}
    fields={
            "Senior Cells":"Cells",
            "PCFs":"Senior Cells",
            "Churches":"PCFs",
            "Group Churches":"Churches",
            "Zones":"Group Churches",
            "Regions":"Zones"
    }
    fieldname=dts['tbl']
    res=frappe.db.sql("select name from `tab%s` where %s='%s'"  %(fields[fieldname],wheres[tablename],dts['name']),as_dict=True)
    return res



@frappe.whitelist(allow_guest=True)
def task_list(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }    
    data=frappe.db.sql("""select name ,subject ,exp_end_date,status,priority,description,cell from `tabTask` where status in ('Open','Working' ) and exp_start_date is not null and owner='%s' or _assign like '%%%s%%' """ %(dts['username'],dts['username']),as_dict=True)
    return data


@frappe.whitelist(allow_guest=True)
def task_update(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }         
    if dts['followup_task']:
        dts['exp_start_date']=now()
        dts['doctype']='Task'
        dts['subject']='followup task for '+dts['name']
        del dts['assignee']
        ma = frappe.get_doc(dts)
        ma.insert(ignore_permissions=True)
        frappe.db.sql("update `tabTask` set description=%s,status='Closed',closing_date=%s where name=%s",('Closed the task and created followup task '+ma.name ,now(),dts['name']),as_dict=True)
        return "Created followup taks "+ma.name+" and closed old task "+dts['name']
    else:
        frappe.db.sql("update `tabTask` set description=%s,status=%s,_assign=%s where name=%s",(dts['description'],dts['status'],dts['_assign'],dts['name']),as_dict=True)
        return "Task Details updated Successfully"

@frappe.whitelist(allow_guest=True)
def cell_members(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }  
    data=frappe.db.sql("select a.member_name from tabMember a,tabUser b where a.user_id=b.name and a.cell=%s",dts['cell'],as_dict=True)
    return data


@frappe.whitelist(allow_guest=True)
def create_task(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }  
    dts['exp_start_date']=now()
    dts['doctype']='Task'
    dts['owner']=dts['username']
    del dts['assignee']
    del dts['name']
    ma = frappe.get_doc(dts)
    ma.insert(ignore_permissions=True)
    return ma.name+" created Successfully"



@frappe.whitelist(allow_guest=True)
def dashboard(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }  
        data={}
        new_visitor=frappe.db.sql("select a.`Week`,b.`Month`,c.`Year` from (select count(name) as `Week` from `tabInvitees and Contacts` where creation between date_sub(now(),INTERVAL 1 WEEK) \
        and now()) a,(select count(name) as `Month` from `tabInvitees and Contacts` where creation between date_sub(now(),INTERVAL 1 Month) and now()) b,\
        (select count(name) as `Year` from `tabInvitees and Contacts` where creation between date_sub(now(),INTERVAL 1 Year) and now())c", as_dict=1)
        data['invities_contacts']=new_visitor

        new_born=frappe.db.sql("select a.`Week`,b.`Month`,c.`Year` from (select count(name) as `Week` from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 WEEK) and now() and \
        	is_new_born='Yes') a,(select count(name) as `Month` from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 Month) and now() and is_new_born='Yes') b,(select count(name) \
        	as `Year` from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 Year) and now() and is_new_born='Yes')c" , as_dict=1)
        data['new_converts']=new_born
	
        first_timers=frappe.db.sql("select a.`Week`,b.`Month`,c.`Year` from (select count(name) as `Week` from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 WEEK) and now() ) \
        	a,(select count(name) as `Month` from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 Month) and now()) b,(select count(name) as `Year` from `tabFirst Timer` where \
        		creation between date_sub(now(),INTERVAL 1 Year) and now())c" , as_dict=1)
        data['first_timers']=first_timers
	membership_strength=frappe.db.sql("select a.month,a.total_member_count,b.conversion as `new_converts` from ( SELECT COUNT(name) AS total_member_count,MONTHNAME(creation) as month FROM `tabMember` WHERE creation BETWEEN date_sub(now(),INTERVAL 90 day) AND now() GROUP BY YEAR(creation),MONTH(creation)) a, (select MONTHNAME(creation) as month ,count(ftv_id_no) as conversion from tabMember where ftv_id_no is not null group by YEAR(creation), MONTH(creation)) b where a.month=b.month",as_dict=1)
        if membership_strength:
                data['membership_strength']=membership_strength
        else:
                data['membership_strength']='0'
        partnership=frappe.db.sql("select MONTHNAME(creation) as Month, ifnull((select sum(amount) from `tabPartnership Record` where giving_or_pledge='Giving' and partnership_arms=p.partnership_arms and year(creation)=year(p.creation) and MONTH(creation)=MONTH(p.creation)),0) as `giving`,ifnull((select sum(amount) from `tabPartnership Record` where giving_or_pledge='Pledge' and partnership_arms=p.partnership_arms and year(creation)=year(p.creation) and MONTH(creation)=MONTH(p.creation)),0) as pledge,partnership_arms from `tabPartnership Record` p where creation between date_sub(now(),INTERVAL 120 day) and now() and  partnership_arms is not null group by year(creation), MONTH(creation),partnership_arms",as_dict=1)
        data['partnership']=partnership
        return data

@frappe.whitelist(allow_guest=True)
def partnership_arm(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }  
    data=frappe.db.sql("select church,giving_or_pledge,sum(amount) from `tabPartnership Record` group by church,giving_or_pledge ",as_dict=True)
    return data


@frappe.whitelist(allow_guest=True)
def search_glm(data):
        import frappe.sessions
        #frappe.response.update(frappe.sessions.get())
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }         
        qry=''
        if dts['church']:
                key='church'
                value=dts['church']
                key1='church_name'
        elif dts['group_church']:
                key='group_church'
                value=dts['group']
                key1='church_group'
        elif dts['zone']:
                key='zone'
                value=dts['zone']
        elif dts['region']:
                key='region'
                value=dts['region']
        else:
                key='1'
                value=1
        if dts['search']=='Group':
                qry="select church,pcf,senior_cell,name as cell from tabCells where "+cstr(key)+"='"+cstr(value)+"'"
        elif dts['search']=='Leader':
                qry="SELECT ttl.church_name AS church,ttl.church_group AS group_type,ttl.member_name AS member_name,ttl.phone_no AS phone_no FROM ( SELECT cc.name AS church_name, cc.church_group AS church_group, mmbr.member_name AS member_name, mmbr.phone_1 AS phone_no, cc.zone As zone, cc.region as regin FROM tabChurches cc, ( SELECT m.member_name, m.phone_1, userrol.defvalue AS defvalue FROM tabMember m , ( SELECT a.name AS name, c.defvalue AS defvalue FROM tabUser a, tabUserRole b, tabDefaultValue c WHERE a.name=b.parent AND a.name=c.parent AND b.role='Church Pastor' AND c.defkey='Churches' ) userrol WHERE m.user_id=userrol.name) mmbr WHERE cc.name=mmbr.defvalue) ttl WHERE ttl."+key1+"='"+value+"'"
        elif 'member' in dts:
                qry="select name , member_name, church,church_group,zone,region,phone_1,email_id from tabMember where member_name like '%"+cstr(dts['member'])+"%'"
	else:
		 qry="select name , member_name, church,church_group,zone,region,phone_1,email_id from tabMember "
        #return qry
        data=frappe.db.sql(qry,as_dict=True)
        return data

@frappe.whitelist(allow_guest=True)
def file_upload(data):
        dts=json.loads(data)
	#print dts
	#frappe.errprint(dts)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
        from frappe.utils.file_manager import  save_file
        filedata=save_file(fname=dts['filename'],content=base64.b64decode(dts['fdata']),dt=dts['tbl'],dn=dts['name'])
        comment = frappe.get_doc(dts['tbl'], dts['name']).add_comment("Attachment",
            _("Added {0}").format("<a href='{file_url}' target='_blank'>{file_name}</a>".format(**filedata.as_dict())))

	if dts['tbl']=='Member':
             frappe.db.sql("update tabMember set image=%s where name=%s",(filedata.file_url,dts['name']))
	#frappe.errprint(filedata.name,filedata.file_name,filedata.file_url,comment.as_dict())
        return {
            "name": filedata.name,
            "file_name": filedata.file_name,
            "file_url": filedata.file_url,
            "comment": comment.as_dict()
        }

@frappe.whitelist(allow_guest=True)
def member(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
        for rr in dts['records']:
            #del rr['name']
            del rr['password']
            ma = frappe.get_doc(rr)
            ma.insert(ignore_permissions=True)
            return ma.name


@frappe.whitelist(allow_guest=True)
def list_members(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
        res=frappe.db.sql("select name from tabMember",as_dict=1)
	return res

@frappe.whitelist(allow_guest=True)
def list_members_details(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
	qr1="select name,member_name,date_of_birth,phone_1,phone_2,email_id,email_id2,address,office_address,employment_status,industry_segment,yearly_income,experience_years,core_competeance,educational_qualification,null AS `password`,image,marital_info from tabMember where name='"+dts['name']+"'"
        res=frappe.db.sql(qr1,as_dict=1)
	print res
        return res

@frappe.whitelist(allow_guest=True)
def get_my_profile(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
        qr1="select m.name,m.member_name,m.date_of_birth,m.phone_1,m.phone_2,m.email_id,m.email_id2,m.address,m.office_address,m.employment_status,m.industry_segment,m.yearly_income,m.experience_years,m.core_competeance,m.educational_qualification,null AS `password`,m.image,m.marital_info from tabMember m,tabUser u where m.email_id=u.name and u.name='"+dts['username']+"'"
	#rappe.errprint(qr1)
        res=frappe.db.sql(qr1,as_dict=1)
        return res

@frappe.whitelist(allow_guest=True)
def update_my_profile(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
	obj=frappe.get_doc('Member',dts['name'])
	obj.yearly_income=dts['yearly_income']
	obj.office_address=dts['office_address']
	#obj.email_id=dts['email_id']
	obj.industry_segment=dts['industry_segment']
	obj.employment_status=dts['employment_status']
	obj.address=dts['address']
	obj.image=dts['image']
	obj.date_of_birth=dts['date_of_birth']
	obj.educational_qualification=dts['educational_qualification']
	obj.core_competeance=dts['core_competeance']
	obj.member_name=dts['member_name']
	obj.email_id2=dts['email_id2']
	obj.phone_2=dts['phone_2']
	obj.marital_info=dts['marital_info']
	obj.experience_years=dts['experience_years']
	obj.phone_1=dts['phone_1']
	obj.save(ignore_permissions=True)
	obj1=frappe.get_doc('User',dts['username'])
        obj1.new_password=dts['password']
        obj1.save(ignore_permissions=True)
        return "Your profile updated successfully"


@frappe.whitelist(allow_guest=True)
def get_match_conditions(doctype,username):
	meta = frappe.get_meta(doctype)
	role_permissions = frappe.permissions.get_role_permissions(meta, username)
	user_permissions=frappe.db.sql("select defkey,defvalue from tabDefaultValue where parent=%s ",username,as_dict=1)  
	match_conditions = []	
	for item in user_permissions:
	    if item['defkey']==doctype:
	    	match_conditions.append(""" name ='{values}'""".format(values=item['defvalue']))
	    else:
		qry="select fieldname from tabDocField where options='"+cstr(item['defkey'])+"' and parent='"+cstr(doctype)+"'"
        	res=frappe.db.sql(qry)
        	if res:	
			match_conditions.append(""" {fieldname} is null or {fieldname} ='{values}'""".format(doctype=doctype,fieldname=res[0][0],values=item['defvalue']))
	return match_conditions


@frappe.whitelist(allow_guest=True)
def send_notification_member_absent():
	senior_cell_list=frappe.db.sql("select distinct(senior_cell) from tabCells",as_list=1)
	for sc in senior_cell_list:
		cell_list=frappe.db.sql("select name from tabCells where senior_cell='%s'"%(sc[0]),as_list=1)
		for cc in cell_list:
			memeber_list={}
			meeting_list=frappe.db.sql("select name from `tabAttendance Record` where attendance_type='Meeting attendance' and cell='%s' and docstatus=1"%(cc[0]),as_list=1)
			# frappe.errprint(meeting_list)
			if meeting_list:
				absent=frappe.db.sql("select a.member,a.member_name,count(a.email_id) from `tabInvitation Member Details` a ,`tabAttendance Record` b where  \
					b.name=a.parent and a.present<>1 and a.parent in ('%s') group by a.email_id "%("','".join ([x[0] for x in meeting_list])))
				# frappe.errprint(absent)
				for abs_member in absent:
					frappe.errprint(abs_member)
					if abs_member[2]>=3:
						memeber_list[abs_member[0]]=abs_member[1]
						# frappe.errprint(memeber_list)
			cell_leader=frappe.db.sql("""select a.name,a.first_name ,dv.defvalue,dv.defkey from tabUser a,tabUserRole ur,tabDefaultValue dv where a.name=ur.parent and a.name=dv.parent
				and (ur.role='Cell Leader' or ur.role='Senior Cell Leader') and (dv.defkey='Cells' or dv.defkey='Senior Cells') and (dv.defvalue='%s' or dv.defvalue='%s')"""%(sc[0],cc[0]),as_list=1)
			if memeber_list and cell_leader:
				for leaders in cell_leader :
					msg="""Hello '%s',\n\n Following members have not attended last three meetings \n\n %s \n\n Regards,\n\n Love world Synergy"""%(leaders[1]," \n".join([" \n \t\t\t\t\t\t Member Id : '%s'  Member Name : '%s'" % (k,v) for k,v in memeber_list.iteritems()]) )
					abc = [" \n Member Id : '%s'  Member Name : '%s'" % (k,v) for k,v in memeber_list.iteritems()]
					frappe.errprint(msg)
					phone = frappe.db.sql("select phone_1 from `tabMember` where email_id='%s'"%(leaders[0]))
					notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field='member_is_absent_in_meeting'""",as_list=1)
					# frappe.errprint(phone[0][0])
					if "Email" in notify[0][0]:
						frappe.sendmail(recipients=leaders[0], content=msg, subject='Absent Member Notification')
					if "SMS" in notify[0][0]:
						if phone:
							send_sms(phone[0], msg)
					if "Push Notification" in notify[0][0]:
						data={}
						data['Message']=msg
						gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
						res1=frappe.db.sql("select device_id from tabUser where name ='%s'" %(leaders[0]),as_list=1)
						if res1:
							res1 = gcm.json_request(registration_ids=res1, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)

					#frappe.sendmail(recipients="email.kadam@gmail.com", sender='gangadhar.k@indictranstech.com', content=msg, subject='Member Absent')
					# frappe.sendmail(recipients=leaders[0], sender='gangadhar.k@indictranstech.com', content=msg, subject='Member Absent')
	return "sent emails"


			# res=frappe.db.sql("select name,senior_cell,pcf from tabCells where name not in (select distinct(cell) from `tabAttendance Record`  \
			# where attendance_type='Meeting attendance' and creation BETWEEN DATE_SUB(NOW(), INTERVAL 7 DAY)  AND DATE_SUB(NOW(), INTERVAL 15 DAY)) and senior_cell='%s'"%(sc[0]),as_list=1)
			# cell_leader=frappe.db.sql("select a.name,a.first_name ,dv.defvalue,dv.defkey from tabUser a,tabUserRole ur,tabDefaultValue dv where a.name=ur.parent and a.name=dv.parent \
			# and (ur.role='PCF Leader' or ur.role='Senior Cell Leader') and (dv.defkey='PCFs' or dv.defkey='Senior Cells') and \
			# (dv.defvalue='%s' or dv.defvalue='%s') "%(res[0][1],res[0][2]))
	# res=frappe.db.sql("select name,member_name,cell from tabMember where cell='Zone-0001/CHR0001/CEL0001' limit 3",as_dict=1)
	# for r in res:
	# 	cell_leader=frappe.db.sql("select a.name,a.first_name from tabUser a,tabUserRole ur,tabDefaultValue dv where a.name=ur.parent and a.name=dv.parent and ur.role='Cell Leader' and dv.defkey='Cells' and dv.defvalue=%s",r['cell'])
	# 	if cell_leader:
	# 		msg="Hello '%s',<br><br> The member id '%s'  ad name '%s' is absent in last 3 consecatve meeting. <br><br>Regards,<br>Love world Synergy"%(cell_leader[0][1],r['name'],r['member_name'])
	# 		frappe.sendmail(recipients=cell_leader[0][0], sender='gangadhar.k@indictranstech.com', content=msg, subject='Member Absent')
	# 		frappe.sendmail(recipients="email.kadam@gmail.com", sender='gangadhar.k@indictranstech.com', content=msg, subject='Cell Meeting not held in last week')
	# return "Sent member absent emails"


@frappe.whitelist(allow_guest=True)
def send_notification_cell_meeting_not_hold():
	frappe.errprint("hi")
	senior_cell_list=frappe.db.sql("select distinct(senior_cell) from tabCells",as_list=1)
	# frappe.errprint(senior_cell_list)
	for sc in senior_cell_list:
		res=frappe.db.sql("select name,senior_cell,pcf from tabCells where name not in (select distinct(cell) \
			from `tabAttendance Record` where attendance_type='Meeting attendance' and creation BETWEEN \
			DATE_SUB(NOW(), INTERVAL 7 DAY)  AND DATE_SUB(NOW(), INTERVAL 15 DAY)) and senior_cell='%s'"%(sc[0]),as_list=1,debug=1)
		frappe.errprint(res)
		cell_leader=frappe.db.sql("select a.name,a.first_name ,dv.defvalue,dv.defkey from tabUser a,tabUserRole ur,\
			tabDefaultValue dv where a.name=ur.parent and a.name=dv.parent and (ur.role='PCF Leader' or \
			ur.role='Senior Cell Leader') and (dv.defkey='PCFs' or dv.defkey='Senior Cells') and \
			(dv.defvalue='%s' or dv.defvalue='%s') "%(res[0][1],res[0][2]))
		for recipents in cell_leader :
			msg="""Hello '%s',\n\n \t\t The cell meeting is not held in last week for cell '%s'. \n\n Regards,\n\n Love world Synergy"""%(recipents[1],' , '.join([x[0] for x in res]) )
			frappe.sendmail(recipients=recipents[0], content=msg, subject='Cell Meeting not held in last week')
			frappe.sendmail(recipients="email.kadam@gmail.com", sender='gangadhar.k@indictranstech.com', content=msg, subject='Cell Meeting not held in last week')
	return "Sent cell meeting not held emails"


@frappe.whitelist(allow_guest=True)
def message_braudcast_send(data):
    """
    this will return recipents details
    """
    dts=json.loads(data)
    from frappe.model.db_query import DatabaseQuery
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    msg=''
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }   
    if dts['sms']:
    	from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
    	rc_list=frappe.db.sql("select phone_1 from tabMember where phone_1 is not null and email_id in ('%s') limit 3" %(dts['recipents'].replace(",","','")),as_list=1)      
    	if rc_list:
    		send_sms([ x[0] for x in rc_list ], cstr(dts['message']))
    		msg+= "SMS "
    rc_list=dts['recipents'].split(',')
    if dts['push']:
        data={}
        data['Message']=dts['message']
        gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
        res=frappe.db.sql("select device_id from tabUser where name in ('%s')" % "','".join(map(str,rc_list)),as_list=1)
        if res:
                res = gcm.json_request(registration_ids=res, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)
                msg+= "Push notification"
    if dts['email']:
        frappe.sendmail(recipients=dts['recipents'], sender='verve@lws.com', content=dts['message'], subject='Broadcast Message')
        msg+=" Email"
    return msg +" sent Successfully"


@frappe.whitelist(allow_guest=True)
def task_esclate():
	"""
	this will return recipents details
	"""
	print "running task exclation"
	task_list=[]
	task_to_esclate=frappe.db.sql("""select name,owner,_assign,concat('["',owner,'"]') from tabTask where status<>'Closed' and exp_end_date<=curdate() and owner<> REPLACE (REPLACE (_assign, '["', ''), '"]', '')""",as_dict=1)
	for task in task_to_esclate:
		frappe.db.sql("update tabToDo set status='Closed' where reference_type='Task' and status='Open' and reference_name= '%s'" % task['name'])
		task_obj = frappe.new_doc("ToDo")
		task_obj.description = 'Task esclated du to not tesolved on time'
		task_obj.status = 'Open'
		task_obj.priority = 'Medium'
		task_obj.date = nowdate()
		task_obj.owner = task['owner']
		task_obj.reference_type = 'Task'
		task_obj.reference_name = task['name']
		task_obj.assigned_by = 'Administrator'
		task_obj.insert(ignore_permissions=True)
		task_list.append(task['name'])
	return task_list