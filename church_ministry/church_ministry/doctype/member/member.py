# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe import throw, _, msgprint
from frappe.utils import getdate, validate_email_add, cint,cstr,now
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
def create_push_notification(device_id,username,userpass):
        """
        Need to check validation/ duplication  etc

        """
        #dts=json.loads(data)
	#print dts
        qry="select user from __Auth where user='"+cstr(username)+"' and password=password('"+cstr(userpass)+"') "
	#print qry
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
		obj=frappe.get_doc("User",username)
                obj.device_id=device_id
		obj.save(ignore_permissions=True)
		#print obj.device_id
                return "Successfully updated device id '"+obj.device_id+"'"


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
	#print dts
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
	       from erpnext.controllers.queries import get_match_cond
	       #print dts['username']
	       #print frappe.session.user
	       #mcond=get_match_cond("Attendance Record")
	       #print mcond
               qry="select name as meeting_name,meeting_subject , from_date as meeting_date ,venue from `tabAttendance Record` where 1=1 "
	       #print qry
               data=frappe.db.sql(qry,as_dict=True)
	       #print data
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
		#frappe.local.session_obj = Session(user=dts['username'], resume=resume,full_name=dts['username'], user_type="System User")
		#frappe.session.user=dts['username']
                data=frappe.db.sql("select name,member,member_name,present from `tabInvitation Member Details` where parent=%s",dts['meeting_id'],as_dict=True)
                return data


@frappe.whitelist(allow_guest=True)
def meetings_attendance(data):
	"""
	Need to add provision to send sms,push notification and emails on present and absent
	"""
        dts=json.loads(data)
	#print dts
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
                for record in dts['records']:
                        if record['present']=='0' or record['present']=='1' :
                                frappe.db.sql("update `tabInvitation Member Details` set present=%s where name=%s",(record['present'],record['name']))
				res=frappe.db.sql("select device_id from tabUser where name=(select email_id from `tabInvitation Member Details` where name=%s) ",record['name'],as_list=True,debug=1)
				#print res
				if res and dts['push']=='1':
					from gcm import GCM
					gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
					data = {'param1': 'new attendance updated sussessfully ....'}
					reg_ids=['APA91bGKibKhhg2RssK2eng8jXW7Gzhmq5_nDcxr8OiAxPSB62xlMdJdSPKCGO9mPF7uoLpT_8b-V0MdY33lc7fTNdh6U965YTQD3sIic_-sY3C45fF5dUEwVuVo8e2lmDduN4EUsHBH','APA91bHXuIe7c8JflytJnTdCOXlWzfJCM2yt5hGgwaqzIbNfGjANhqzLgrVCoSno70hKtygzg_W7WbE4lHeZD_LeQ6CSc_5AteGY1Gh6R7NXihVnE45K91DOPxgtnF5ncN4gSJYiX0_N']
					#print reg_ids
					#print res[0]
					res = gcm.json_request(registration_ids=res[0], data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)
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
                data=frappe.db.sql("select a.name as meeting_name,a.meeting_category as meeting_category, a.meeting_subject as meeting_subject,a.from_date as from_date,a.to_date as to_date,a.venue as venue,b.name as name,ifnull(b.present,0) as present from `tabAttendance Record`  a,`tabInvitation Member Details` b where a.name=b.parent and b.email_id=%s",dts['username'],as_dict=True)
                return data


@frappe.whitelist(allow_guest=True)
def mark_my_attendance(data):
	"""
	Member can mark their attandence of meeting
	"""
        dts=json.loads(data)
	#print(dts)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
                for record in dts['records']:
                        if not record['present'] :
                                record['present']=0
                        frappe.db.sql("update `tabInvitation Member Details` set present=%s where name=%s",(record['present'],record['name']),debug=1)
                return "Updated Attendance"



@frappe.whitelist(allow_guest=True)
def get_masters(data):
	"""
	Member can mark their attandence of meeting
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
	meta = frappe.get_meta(dts['tbl'])
	role_permissions = frappe.permissions.get_role_permissions(meta, dts['username'])
	#user_permissions = frappe.defaults.get_user_permissions(dts['username'])
	#user_permissions1 =frappe.db.sql("""select defkey,defvalue from tabDefaultValue where parent=%s and parenttype='User Permission'""", (dts['username']),as_dict=True)
	user_permissions=frappe.db.sql("select defkey,defvalue from tabDefaultValue where parent=%s " ,dts['username'],as_dict=1)  
	match_conditions = []
	
	for item in user_permissions:
	    if item['defkey']==dts['tbl']:
	    	match_conditions.append(""" name ='{values}'""".format(values=item['defvalue']))
	    else:
		qry="select fieldname from tabDocField where options='"+cstr(item['defkey'])+"' and parent='"+cstr(dts['tbl'])+"'"
        	res=frappe.db.sql(qry)
        	if res:	
			match_conditions.append(""" {fieldname} is null or {fieldname} ='{values}'""".format(doctype=dts['tbl'],fieldname=res[0][0],values=item['defvalue']))
	#for doctypes in user_permissions:
	#	#print doctypes
	#	for df in meta.get_fields_to_check_permissions(doctypes):
	#		#print df.options
	#		match_conditions.append("""(ifnull(`tab{doctype}`.`{fieldname}`, "")=""
	#				or `tab{doctype}`.`{fieldname}` in ({values}))""".format(doctype=dts['tbl'],fieldname=df.fieldname,values=", ".join([('"'+v+'"') for v in user_permissions[df.options]])
	#		))
	cond = ''
	user_roles = frappe.get_roles(dts['username'])
	if match_conditions   :
		cond = 'where ' + ' or '.join(match_conditions)
		return frappe.db.sql("""select name from `tab%s` where %s"""%(dts['tbl'], ' or '.join(match_conditions)), as_dict=1)
	elif ("System Manager" in user_roles ):
		return frappe.db.sql("""select name from `tab%s` """%(dts['tbl']), as_dict=1)
	else:
		return {
				"status":"200",
				"message":"No Records Found"
		}


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
    data=frappe.db.sql("select a.id as `name` ,a.person_name,ifnull(a.present,0) as present,a.comments from `tabEvent Attendace Details`  a,`tabEvent Attendance` b  where a.parent=b.name and b.event_name=%s",dts['event_id'],as_dict=True)
    return data
                

@frappe.whitelist(allow_guest=True)
def event_attendance(data):
    """
    Give provisin for sms email and push notification
    update Event attendance
    """
    dts=json.loads(data)
    #print dts
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
        frappe.db.sql("update `tabEvent Attendace Details` set present=%s where id=%s",(record['present'],record['name']))
	qry="select device_id from tabUser where name=(select email_id from tabMember where name='"+cstr(record['name'])+"')"
	#print qry
	res=frappe.db.sql(qry,as_list=True)
	#print res
	if res and dts['push']=='1':
		#print res[0]
		from gcm import GCM
		gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
		data = {'param1': 'event attendance updated sussessfully ....'}
		res = gcm.json_request(registration_ids=res[0], data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)
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
    data=frappe.db.sql("select a.subject ,a.starts_on as event_date, a.address,c.name,c.person_name,ifnull(c.present,0) as present,comments from `tabEvent` a, `tabEvent Attendance` b,`tabEvent Attendace Details` c \
                         where a.name=b.event_name and b.name=c.parent and c.id in (select a.name from tabMember a,tabUser b where a.email_id=b.name and b.name=%s) ",dts['username'],as_dict=True)
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
        frappe.db.sql("update `tabEvent Attendace Details` set present=%s where name=%s",(record['present'],record['name']))
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
    data=frappe.db.sql("""select name ,owner as assignee,subject ,exp_end_date,status,priority,description,replace(replace(replace(SUBSTRING_INDEX(_assign,',',1),'"',''),'[',''),']','') as _assign,cell,senior_cell,pcf from `tabTask` where status in ('Open','Working' ) and exp_start_date is not null and owner='%s' or _assign like '%%%s%%' """ %(dts['username'],dts['username']),as_dict=True)
    return data


@frappe.whitelist(allow_guest=True)
def task_list_team(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }    
    data=frappe.db.sql("""select name ,owner as assignee,subject ,exp_end_date,status,priority,description,replace(replace(replace(SUBSTRING_INDEX(_assign,',',1),'"',''),'[',''),']','') as _assign,cell,senior_cell,pcf from `tabTask` where status in ('Open','Working' ) and exp_start_date is not null """ ,as_dict=True)
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
	del dts['_assign']
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
        new_visitor=frappe.db.sql("select count(name) from `tabInvitees and Contacts` where creation between date_sub(now(),INTERVAL 1 WEEK) and now()")
        if new_visitor :
                data['new_visitor']=new_visitor[0][0]
        else:
                data['new_visitor']='0'


        new_born=frappe.db.sql("select count(name) from `tabMember` where creation between date_sub(now(),INTERVAL 1 YEAR) and now() and is_new_born='Yes'")
        if new_born:
                data['new_born']=new_born[0][0]
        else:
                data['new_born']='0'   
	
        first_timers=frappe.db.sql("select count(name) from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 YEAR) and now()")
        if first_timers:
                data['first_timers']=first_timers[0][0]
        else:
                data['first_timers']='0'
        visitor_last_months=frappe.db.sql("select count(name) from `tabInvitees and Contacts` where creation between date_sub(now(),INTERVAL 1 WEEK) and now()")
        if visitor_last_months:
                data['visitor_last_months']=visitor_last_months[0][0]
        else:
                data['visitor_last_months']='0'
        #membership_strength=frappe.db.sql("select MONTHNAME(creation) as Month, count(name) as `New Users`,count(name) as Revisited from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 Year) and now() group by year(creation), MONTH(creation)",as_list=1)
	membership_strength=frappe.db.sql("select a.month,a.total_member_count,b.conversion as `new_converts` from ( SELECT COUNT(name) AS total_member_count,MONTHNAME(creation) as month FROM `tabMember` WHERE creation BETWEEN date_sub(now(),INTERVAL 1 YEAR) AND now() GROUP BY YEAR(creation),MONTH(creation)) a, (select MONTHNAME(creation) as month ,count(ftv_id_no) as conversion from tabMember where ftv_id_no is not null group by YEAR(creation), MONTH(creation)) b where a.month=b.month",as_dict=1)
        if membership_strength:
                data['membership_strength']=membership_strength
        else:
                data['membership_strength']='0'
        #partnership=frappe.db.sql("select MONTHNAME(creation) as Month, count(name) as `giving`,count(name) as pledge from `tabFirst Timer` where creation between date_sub(now(),INTERVAL 1 Year) and now() group by year(creation), MONTH(creation)",as_dict=1)
	partnership=frappe.db.sql("select MONTHNAME(creation) as Month, ifnull(sum(amount),0) as `giving`,ifnull(sum(amount),0) as pledge from `tabPartnership Record` where creation between date_sub(now(),INTERVAL 1 Year) and now() group by year(creation), MONTH(creation)",as_dict=1)
        if partnership:
                data['partnership']=partnership
        else:
                data['partnership']='0'
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
    data=frappe.db.sql("select name,church,partnership_arms,giving_or_pledge,sum(amount) as amount from `tabPartnership Record` group by church,giving_or_pledge ",as_dict=True)
    return data

@frappe.whitelist(allow_guest=True)
def partnership_arm_details(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    data=frappe.db.sql("select name,partnership_arms,ministry_year,is_member,member,date,church,giving_or_pledge,amount from `tabPartnership Record`  where name='%s'" %(dts['name']) ,as_dict=True)
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
def message_braudcast_details(data):
    """
    this will return recipents details
    """
    dts=json.loads(data)
    #print dts
    from frappe.model.db_query import DatabaseQuery
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    if dts['tbl']=='FT':
       qry="select name,ftv_name ,email_id,phone_1 from `tabFirst Timer` where email_id in (select u.name from tabUser u,tabUserRole ur where u.enabled=1 and ur.role='Member' )"
    elif dts['tbl']=='Member':
       qry="select name,member_name as ftv_name,email_id,phone_1 from tabMember where email_id in (select u.name from tabUser u,tabUserRole ur where u.enabled=1 and ur.role='Member') "
    else:
        qry="select name,member_name as ftv_name,email_id,phone_1 from tabMember where email_id in (select distinct parent from tabUserRole where role in ('PCF Leader','Cell Leader','Senior Cell Leader','Church Pastor','Group Church Pastor','Regional Pastor','Zonal Pastor'))"
    res=frappe.db.sql(qry,as_dict=1)
    #print res
    return res


@frappe.whitelist(allow_guest=True)
def message_braudcast_send(data):
    """
    this will return recipents details
    """
    dts=json.loads(data)
    #print dts
    from frappe.model.db_query import DatabaseQuery
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    if dts['sms']:
        from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
	rc_list=frappe.db.sql("select phone_1 from tabMember where phone_1 is not null and email_id in ('%s')" %(dts['recipents'].replace(",","','")),as_list=1)      
    	if rc_list:
    		send_sms([ x[0] for x in rc_list ], cstr(dts['message']))
		print "sending sms"
    rc_list=dts['recipents'].split(',')
    if dts['push']:
	data={}
	data['Message']=dts['message']
	gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
	res=frappe.db.sql("select device_id from tabUser where name in ('%s')" % "','".join(map(str,rc_list)),as_list=1)
	if res:
        	res = gcm.json_request(registration_ids=res, data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)
		print "sending push notification"
    if dts['email']:
	print "sending email"
        frappe.sendmail(recipients=dts['recipents'], sender='verve@lws.com', content=dts['message'], subject='Message Broadcast')
    return "Successfully message has been sent"

