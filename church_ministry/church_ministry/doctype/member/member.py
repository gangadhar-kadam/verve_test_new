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
from datetime import datetime
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
			frappe.db.sql("update `tabMember` set flag='SetPerm',user_id='%s' where name='%s'"%(self.email_id,self.name))
			frappe.db.commit()

def get_list(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import get_match_cond
	search_field={
	"Cells":"cell_name",
	"Senior Cells":"senior_cell_name",
	"PCFs":"pcf_name",
	"Churches":"church_name",
	"Group Churches":"church_group",
	"Zones":"zone_name",
	"Regions":"region_name"
	}
	filters.update({
			"txt": txt,
			"mcond": get_match_cond(filters["doctype"]),
			"start": start,
			"page_len": page_len
		})
	search_fields=filters['doctype']
	filters['search_field']=search_field[search_fields]
	res=frappe.db.sql("""select name,%(search_field)s from `tab%(doctype)s` where name like '%%%(txt)s%%' or %(search_field)s like '%%%(txt)s%%'%(mcond)s order by name limit %(start)s, %(page_len)s""" %filters)
	return res


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


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return None
	else:
		abc="""
			`tabMember`.cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Cells')
			or
			`tabMember`.senior_cell=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Senior Cells')
			or
			`tabMember`.pcf=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='PCFs')
			or
			`tabMember`.church=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Churches')
			or
			`tabMember`.church_group=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Group Churches')
			or
			`tabMember`.zone=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Zones')
			or
			`tabMember`.region=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Regions')
			or 
			`tabMember`.name=(select distinct defvalue from `tabDefaultValue` where parent='%(user)s' and defkey='Member')
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
	if doc.name:
		res=frappe.db.sql("select distinct defvalue from `tabDefaultValue` where parent='%s' and defkey='Member'"%(user))
		if res:
			return True

	return False



@frappe.whitelist(allow_guest=True)
def get_attendance_points(args):
	"""
	Get employee id and return points according to his attendance assumed the working days are 365 and points are 100
	"""
	# frappe.errprint("deleting documents")
	frappe.delete_doc('DocType','Employee task Details')
	present , working =0,0
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
		#qry=''
		role,defkey='',''
		user_roles = frappe.get_roles(dts['username'])
                if "Regional Pastor" in user_roles:
			role='Regional Pastor'
			defkey='Regions'
                elif "Zonal Pastor" in user_roles:
			role='Zonal Pastor'
			defkey='Zones'
                elif "Group Church Pastor" in user_roles :
			role='Group Church Pastor'
			defkey='Group Churches'
                elif "Church Pastor"  in user_roles:
			role='Church Pastor'
			defkey='Churches'
                elif "PCF Leader"  in user_roles:
			role='PCF Leader'
			defkey='PCFs'
                elif "Senior Cell Leader"  in user_roles:
			role='Senior Cell Leader'
			defkey='Senior Cells'
                elif "Cell Leader"  in user_roles:
			role='Cell Leader'
			defkey='Cells'
                elif "Bible Study Class Teacher"  in user_roles:
			role='Bible Study Class Teacher'
		elif "Partnership Rep"  in user_roles:
			role='Partnership Rep'
			defkey='Cells'
                elif "Member"  in user_roles:
			role='Member'
			defkey='Member'
                roles=frappe.db.sql("select role from `tabUserRole` where role= %(role)s and parent=%(user)s", {"role":role, "user":dts['username']},as_dict=1)                 
                user_values=frappe.db.sql("select defkey,defvalue from `tabDefaultValue`  where defkey=%(defkey)s and parent=%(user)s", {"defkey":defkey, "user":dts['username']},as_dict=1)
                data['roles']=roles
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
	print dts
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
		obj.pcf=dts['pcf']
		higher_details=frappe.db.sql("select pcf_name,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name from `tabPCFs` where name='%s'"%(dts['pcf']))
		obj.pcf_name=higher_details[0][0]
		obj.church=higher_details[0][1]
		obj.church_name=higher_details[0][2]
		obj.church_group=higher_details[0][3]
		obj.group_church_name=higher_details[0][4]
		obj.zone=higher_details[0][5]
		obj.zone_name=higher_details[0][6]
		obj.region=higher_details[0][7]
		obj.region_name=higher_details[0][8]
		obj.contact_phone_no=dts['contact_phone_no']
		obj.contact_email_id=dts['contact_email_id']
		obj.insert(ignore_permissions=True)
		return "Successfully created senior Cell '"+obj.name+"'"
		                

@frappe.whitelist(allow_guest=True)
def create_ftv(data):
	"""
	Need to check validation/ duplication  etc

	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	#print dts
	if not valid:
		return {
		  "status":"401",
		  "message":"User name or Password is incorrect"
		}
        # if not frappe.has_permission(doctype="First Timer", ptype="create",user=dts['username']):
        #         return {
        #           "status":"403",
        #           "message":"You have no permission to create First Timer"+
        #         }
        
        # mm=frappe.db.get_value("User", dts['email_id'],'name' )
        # if mm:
        #         return {
        #           "status":"402",
        #           "message":"Member not created another member with same email id ('"+mm+"') is exist "
        #         }
	else:
		frappe.set_user(dts['username'])
		obj=frappe.new_doc("First Timer")
		obj.office_address=dts['office_address']
		obj.industry_segment=dts['industry_segment']
		obj.employment_status=dts['employment_status']
		obj.address=dts['address']
		obj.date_of_birth=dts['date_of_birth']
		obj.education_qualification=dts['education_qualification']
		obj.core_competeance=dts['core_competeance']
		obj.ftv_name=dts['ftv_name']
		obj.email_id_2=dts['email_id2']
		obj.ftv_type=dts['ftv_type']
		obj.phone_2=dts['phone_2']
		obj.marital_info=dts['marital_info']
		obj.introduced_by=dts['introduced_by']
		obj.first_contact_by=dts['first_contact_by']
		obj.experience_years=dts['experience_years']
		obj.phone_1=dts['phone_1']
		obj.phone_2=dts['phone_2']
		obj.office_landmark=dts['office_landmark']
		obj.baptism_where=dts['baptism_where']
		obj.title=dts['title']
		obj.baptism_when=dts['baptism_when']
		obj.age_group=dts['age_group']
		obj.baptisum_status=dts['baptisum_status']
		obj.sex=dts['sex']
		obj.school_status=dts['school_status']
		obj.filled_with_holy_ghost=dts['filled_with_holy_ghost']
		obj.is_new_born=dts['is_new_born']
		obj.is_new_convert=dts['is_new_convert']
		obj.address_manual=dts['address_manual']
		obj.date_of_visit=dts['date_of_visit']
		obj.yokoo_id=dts['yokoo_id']
		obj.yearly_income=dts['yearly_income']
		obj.task_description=dts['task_description']
		obj.due_date=dts['due_date']
		if 'cell' in dts:
			obj.cell=dts['cell']
	    	if 'senior_cell' in dts:
			obj.senior_cell=dts['senior_cell']
		if 'pcf' in dts:	
			obj.pcf=dts['pcf']
		obj.church=dts['church']
		obj.church_group=dts['church_group']
		obj.zone=dts['zone']
		obj.region=dts['region']
		obj.email_id=dts['email_id']
		obj.surname=dts['surname']
		if 'short_bio' in dts:
			obj.short_bio=dts['short_bio']
		obj.insert(ignore_permissions=True)
		
		return "Successfully Created First Timer '"+obj.name+"'"




@frappe.whitelist(allow_guest=True)
def create_member(data):
	"""
	Need to check validation/ duplication  etc

	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	#print dts
	if not valid:
		return {
		  "status":"401",
		  "message":"User name or Password is incorrect"
		}
        if not frappe.has_permission(doctype="Member", ptype="create",user=dts['username']):
                return {
                  "status":"403",
                  "message":"You have no permission to create Member"
                }
        
        mm=frappe.db.get_value("User", dts['email_id'],'name' )
        if mm:
                return {
                  "status":"402",
                  "message":"Member not created another member with same email id ('"+mm+"') is exist "
                }
	else:
		frappe.set_user(dts['username'])
		#frappe.errprint(frappe.session.user)
		obj=frappe.new_doc("Member")
		obj.yearly_income=dts['yearly_income']
		obj.office_address=dts['office_address']
		#obj.image=dts['image']
		obj.industry_segment=dts['industry_segment']
		obj.employment_status=dts['employment_status']
		obj.address=dts['address']
		obj.date_of_birth=dts['date_of_birth']
		obj.educational_qualification=dts['educational_qualification']
		obj.core_competeance=dts['core_competeance']
		obj.member_name=dts['member_name']
		obj.email_id2=dts['email_id2']
		obj.phone_2=dts['phone_2']
		obj.marital_info=dts['marital_info']
		obj.experience_years=dts['experience_years']
		obj.phone_1=dts['phone_1']
		obj.phone_2=dts['phone_2']
		obj.office_landmark=dts['office_landmark']
		obj.baptism_where=dts['baptism_where']
		obj.title=dts['title']
		obj.baptism_when=dts['baptism_when']
		obj.age_group=dts['age_group']
		obj.baptisum_status=dts['baptisum_status']
		obj.sex=dts['sex']
		obj.school_status=dts['school_status']
		obj.filled_with_holy_ghost=dts['filled_with_holy_ghost']
		obj.is_new_born=dts['is_new_born']
		obj.is_eligibale_for_follow_up=dts['is_eligibale_for_follow_up']
		obj.date_of_join=dts['date_of_join']
		obj.yokoo_id=dts['yokoo_id']
		obj.cell=dts['cell']
		obj.senior_cell=dts['senior_cell']
		obj.pcf=dts['pcf']
		obj.church=dts['church']
		obj.church_group=dts['church_group']
		obj.zone=dts['zone']
		obj.region=dts['region']
		obj.email_id=dts['email_id']
		obj.surname=dts['surname']

		if 'short_bio' in dts:
			obj.short_bio=dts['short_bio']
		obj.insert(ignore_permissions=True)
		# obj1=frappe.get_doc('User',dts['username'])
	 #        obj1.new_password=dts['password']
	 #        obj1.last_name=dts['last_name']
	 #        obj1.first_name=dts['member_name']
	 #        obj1.save(ignore_permissions=True)
			
		return "Successfully Created Member '"+obj.name+"'"




@frappe.whitelist(allow_guest=True)
def create_cells(data):
	"""
	Need to check validation/ duplication  etc

	"""
	dts=json.loads(data)
	#print data
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
		higher_details=frappe.db.sql("select senior_cell_name,pcf,pcf_name ,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name from `tabSenior Cells` where name='%s'"%(dts['senior_cell']))
		obj.senior_cell=dts['senior_cell']
		obj.senior_cell_name=higher_details[0][0]
		obj.pcf=higher_details[0][1]
		obj.pcf_name=higher_details[0][2]
		obj.church=higher_details[0][3]
		obj.church_name=higher_details[0][4]
		obj.church_group=higher_details[0][5]
		obj.group_church_name=higher_details[0][6]
		obj.zone=higher_details[0][7]
		obj.zone_name=higher_details[0][8]
		obj.region=higher_details[0][9]
		obj.region_name=higher_details[0][10]
		obj.contact_phone_no=dts['contact_phone_no']
		obj.contact_email_id=dts['contact_email_id']
		obj.insert(ignore_permissions=True)
		ret={
			"message":"Successfully created Cell '"+obj.name+"'"
		}
		return ret

@frappe.whitelist(allow_guest=True)
def create_pcf(data):
	"""
	Need to check validation/ duplication  etc

	"""
	dts=json.loads(data)
	print dts
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
                  "message":"You have no permission to create PCFs"
                }
	else:
		obj=frappe.new_doc("PCFs")
		obj.pcf_name=dts['pcf_name']
		obj.pcf_code=dts['pcf_code']
		obj.church=dts['church']
		#return "select church_name,church_group,church_group_name,zone,zone_name,region,region_name from `tabChurches` where name='%s'"%(dts['church'])
		higher_details=frappe.db.sql("select church_name,church_group,church_group_name,zone,zone_name,region,region_name from `tabChurches` where name='%s'"%(dts['church']))
		obj.church_name=higher_details[0][0]
		obj.church_group=higher_details[0][1]
		obj.group_church_name=higher_details[0][2]
		obj.zone=higher_details[0][3]
		obj.zone_name=higher_details[0][4]
		obj.region=higher_details[0][5]
		obj.region_name=higher_details[0][6]
		obj.contact_phone_no=dts['contact_phone_no']
		obj.contact_email_id=dts['contact_email_id']
		obj.insert(ignore_permissions=True)
		ret={
			"message":"Successfully created PCF '"+obj.name+"'"
		}
		return ret



@frappe.whitelist(allow_guest=True)
def create_event(data):
        """
        Need to check validation/ duplication  etc
        """
        dts=json.loads(data)
        #frappe.errprint(dts)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
	#print dts
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        if not frappe.has_permission(doctype="Event", ptype="create",user=dts['username']):
                return {
                  "status":"403",
                  "message":"You have no permission to create Event"
                }
        else:
                obj=frappe.new_doc("Event")
                obj.subject=dts['subject']
                obj.owner=dts['username']
                obj.starts_on=dts['starts_on']
                obj.ends_on=dts['ends_on']
                obj.address=dts['address']
                obj.event_type=dts['type']
                obj.description=dts['description']
                if 'event_group' in dts:
                        column={
				"Regional":"region",
				"Zonal":"zone",
				"Church Group":"church_group",
				"Church":"church",
				"PCF":"pcf",
				"Sr Cell":"senior_cell",
				"Cell":"cell"
			}
                	obj.event_group=dts['event_group']
			if dts['event_group']=='Only Leaders':
				pass
			else:
				#frappe.errprint(column[dts['event_group']])
				setattr(obj, column[dts['event_group']], dts['value'])
                try:
                	if dts['event_group']=='Only Leaders': 
                		for d1 in dts['value'].split(', '):
                		    	#return d1
					child1 = obj.append('roles', {})
					child1.role = d1
	                obj.insert(ignore_permissions=True)
		        obj_att=frappe.new_doc("Attendance Record")
		        obj_att.attendance_type='Event Attendance'
		        obj_att.event=obj.name
			obj_att.meeting_subject=dts['subject']
		        obj_att.from_date=dts['starts_on']
		        obj_att.to_date=dts['ends_on']
		        obj_att.venue=dts['address']
		        obj_att.flags.ignore_mandatory = True
		        obj_att.flags.ignore_validate=True
		        obj_att.insert(ignore_permissions=True)
		        obj_att.set('invitation_member_details', [])
			member_ftv=''
			if dts['event_group']=='Only Leaders':
			        rles=",".join(["'"+x+"'" for x in dts['value'][1:-1].split(',')])
			        qry="select name,member_name,email_id from `tabMember` where  user_id in( select distinct(parent) from tabUserRole where role in ("+rles+"))"
				member_ftv = frappe.db.sql(qry)
			else :  
				member_ftv = frappe.db.sql(" select name,member_name,email_id from `tabMember` where %s='%s'"%(column[dts['event_group']],dts['value']))	
			for d in member_ftv:
				child = obj_att.append('invitation_member_details', {})
				child.member = d[0]
				child.member_name = d[1]
				child.email_id = d[2]
			obj_att.save()	                

	                ret={
	                        "message":"Successfully created Event '"+obj.name+"'"
	                }
	                return ret
	        except Exception,e:
    				return e

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
        res=frappe.db.sql("select name from `tabAttendance Record` where cell='%s' and from_date like '%s%%' and to_date like '%s%%'"%(dts['cell'],f_date,t_date))
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
	#print data
        obj=frappe.new_doc("Attendance Record")
        obj.meeting_category=dts['meeting_category']
	#if dts['meeting_category']=="Cell Meeting":
	obj.meeting_subject=dts['meeting_sub']
	#else:
	#        obj.meeting_sub=dts['meeting_sub']
        obj.from_date=dts['from_date']
        obj.to_date=dts['to_date']
        obj.venue=dts['venue']
        obj.cell=dts['cell']
        higher_details=frappe.db.sql("select senior_cell_name,pcf,pcf_name ,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name,cell_name,senior_cell,senior_cell_name from `tabCells` where name='%s'"%(dts['cell']))
	obj.senior_cell=higher_details[0][12]
	obj.senior_cell_name=higher_details[0][13]
	obj.cell_name=higher_details[0][11]
	obj.senior_cell_name=higher_details[0][0]
	obj.pcf=higher_details[0][1]
	obj.pcf_name=higher_details[0][2]
	obj.church=higher_details[0][3]
	obj.church_name=higher_details[0][4]
	obj.church_group=higher_details[0][5]
	obj.group_church_name=higher_details[0][6]
	obj.zone=higher_details[0][7]
	obj.zone_name=higher_details[0][8]
	obj.region=higher_details[0][9]
	obj.region_name=higher_details[0][10]
        obj.flags.ignore_validate=True
        obj.insert(ignore_permissions=True)
        obj.set('invitation_member_details', [])
	member_ftv=''
	if obj.cell:
		member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Timer` where cell='%s' and approved=0 union select name,member_name,email_id from `tabMember` where cell='%s' "%(obj.cell,obj.cell))
	elif obj.church:
		member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Timer` where church='%s' and approved=0 union select name,member_name,email_id from `tabMember` where church='%s'"%(obj.church,obj.church))	
	for d in member_ftv:
		child = obj.append('invitation_member_details', {})
		child.member = d[0]
		child.member_name = d[1]
		child.email_id = d[2]
	obj.save()
        ret={
                        "message":"Successfully created Meeting Attendance '"+obj.name+"'"
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
	       match_conditions,cond=get_match_conditions('Attendance Record',dts['username'])        	
               qry="select name as meeting_name,CASE meeting_category  WHEN 'Cell Meeting' THEN meeting_subject ELSE meeting_sub END  as meeting_subject , from_date as meeting_date,to_date as end_date ,venue from `tabAttendance Record` where attendance_type='Meeting Attendance' %s  "%( cond)
	       #qry="select name as meeting_name,case meeting_category when 'Cell Meeting' then meeting_subject else meeting_sub end as `meeting_subject` , from_date as meeting_date ,venue from `tabAttendance Record` where 1=1 order by creation desc"

               data=frappe.db.sql(qry,as_dict=True)
               return data
               
@frappe.whitelist(allow_guest=True)
def meetings_list_new(data):
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
		fltr_cnd=''
    		fltrs=[]
		if 'filters' in dts:
   			if 'from_date' in dts['filters']:
    		    		dts['filters']['from_date']=dts['filters']['from_date'][6:]+""+dts['filters']['from_date'][3:5]+""+dts['filters']['from_date'][:2]
  			if 'to_date' in dts['filters']:
    		    		dts['filters']['to_date']=dts['filters']['to_date'][6:]+""+dts['filters']['to_date'][3:5]+""+dts['filters']['to_date'][:2]		      
  			if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
  	     			fltrs.append(" date(creation) >= '%s' and date(a.creation) <= '%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
    			elif 'from_date' in dts['filters'] :
    	        		fltrs.append(" date(creation) >= '%s' " %dts['filters']['from_date'])
    	        
    			elif 'to_date' in dts['filters'] :
    	        		fltrs.append(" date(creation) <= '%s' " %dts['filters']['to_date'])    
    			for key,value in dts['filters'].iteritems():
    	 			if key in ('region','zone','church_group','church','pcf','senior_cell','cell'):
    	       				fltrs.append(" %s = '%s' " %(key,value))
			fltr_cnd=" and "+' and '.join([x for x in fltrs])               
		match_conditions,cond=get_match_conditions('Attendance Record',dts['username'])   
		if match_conditions : 
			fltr_cnd+=cond
			#return fltr_cnd
		total_count= frappe.db.sql("select ifnull(count(name),0) from `tabAttendance Record` where attendance_type='Meeting Attendance' %s " %(fltr_cnd))
		#return total_count
    		if (('page_no' not in dts) or cint(dts['page_no'])<=1):  
			dts['page_no']=1
			start_index=0
    		else:   
			start_index=(cint(dts['page_no'])-1)*20
    		end_index =start_index+20	
    		if total_count[0][0]<=end_index:
			end_index=total_count[0][0] 
		result={}
                result['total_count']=total_count[0][0]
                result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
		result['records']=frappe.db.sql("""select name as meeting_name,CASE meeting_category  WHEN 'Cell Meeting' THEN meeting_subject ELSE meeting_sub END  as meeting_subject , from_date as meeting_date,to_date as end_date ,venue from `tabAttendance Record` where attendance_type='Meeting Attendance'  %s order by name limit %s,20"""%(fltr_cnd,cint(start_index)), as_dict=1)
                return result


@frappe.whitelist(allow_guest=True)
def meetings_members(data):
	"""
	Get all participents of selected meeting
	"""
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
	#print dts
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
		data=frappe.db.sql("select b.name,b.member,b.member_name,ifnull(b.present,'0') as present ,a.venue,case a.meeting_category when 'Cell Meeting' then a.meeting_subject else a.meeting_sub end as `meeting_subject`,a.from_date,a.to_date as end_date from `tabAttendance Record` a,`tabInvitation Member Details` b  where a.name=b.parent and  a.name=%s order by b.member ",dts['meeting_id'],as_dict=True)
                return data


@frappe.whitelist(allow_guest=True)
def meetings_attendance(data):
	# frappe.errprint("notify")
	"""
	Need to add provision to send sms,push notification and emails on present and absent
	"""
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        #frappe.errprint(valid)
	#print dts
        if not valid:
                return {
                  "status":"401",
                  "message":"User name or Password is incorrect"
                }
        else:
        	for record in dts['records']:
        		if record['present']=='0' or record['present']=='1' :
				#print record['name']
        			frappe.db.sql("update `tabInvitation Member Details` set present=%s where name=%s",(record['present'],record['name']))
				#print "update `tabInvitation Member Details` set present="+cstr(record['present'])+" where name="+cstr(record['name'])
				mail_notify_msg = """Dear User, \n\n \t\t Your Attendance is updated by Leader '%s'. Please Check. \n\n Regards, \n\n Love World Synergy"""%(dts['username'])
				membr = frappe.db.sql("select member,email_id from `tabInvitation Member Details` where name=%s",(record['name']),as_list=1)
				#frappe.errprint(membr)
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
	        data=frappe.db.sql("select a.name as meeting_name,a.meeting_category as meeting_category, case a.meeting_category when 'Cell Meeting' then a.meeting_subject else a.meeting_sub end as `meeting_subject`,a.from_date as from_date,a.to_date as to_date,a.venue as venue,b.name as name,ifnull(b.present,0) as present from `tabAttendance Record`  a,`tabInvitation Member Details` b where a.name=b.parent and b.email_id=%s order by a.modified desc",dts['username'],as_dict=True)
                return data
                

@frappe.whitelist(allow_guest=True)
def meetings_list_member_new(data):
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
      		fltr_cnd=''
		fltrs=[]
	        if 'filters' in dts:
	           	if 'from_date' in dts['filters']:
    		    		dts['filters']['from_date']=dts['filters']['from_date'][6:]+""+dts['filters']['from_date'][3:5]+""+dts['filters']['from_date'][:2]
  			if 'to_date' in dts['filters']:
    		    		dts['filters']['to_date']=dts['filters']['to_date'][6:]+""+dts['filters']['to_date'][3:5]+""+dts['filters']['to_date'][:2]
		  	if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
  	     			fltrs.append(" date(a.creation) >= '%s' and date(a.creation) <= '%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
		    	elif 'from_date' in dts['filters'] :
    	        		fltrs.append(" a.creation >= '%s' " %dts['filters']['from_date'])
    	        
		    	elif 'to_date' in dts['filters'] :
    	        		fltrs.append(" a.creation <= '%s' " %dts['filters']['to_date'])    
		    	for key,value in dts['filters'].iteritems():
    	 			if key in ('region','zone','church_group','church','pcf','senior_cell','cell'):
		    	       		fltrs.append(" a.%s = '%s' " %(key,value))
			fltr_cnd=" and "+' and '.join([x for x in fltrs]) 
		#return fltr_cnd       
    		total_count= frappe.db.sql("select count(a.name)  from `tabAttendance Record`  a,`tabInvitation Member Details` b where a.name=b.parent and b.email_id='%s'  %s "%(dts['username'],fltr_cnd))	
		if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
			dts['page_no']=1
			start_index=0
		else:   
			start_index=(cint(dts['page_no'])-1)*20
		end_index =start_index+20	
	        if total_count[0][0]<=end_index:
			end_index=total_count[0][0] 
	        result={}
                result['total_count']=total_count[0][0]
                result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'

	        result['records']=frappe.db.sql("select a.name as meeting_name,a.meeting_category as meeting_category, case a.meeting_category when 'Cell Meeting' then a.meeting_subject else a.meeting_sub end as `meeting_subject`,a.from_date as from_date,a.to_date as to_date,a.venue as venue,b.name as name,ifnull(b.present,0) as present from `tabAttendance Record`  a,`tabInvitation Member Details` b where a.name=b.parent and b.email_id='%s' %s order by name limit %s,20"%(dts['username'],fltr_cnd,cint(start_index)),as_dict=True)
                return result                



@frappe.whitelist(allow_guest=True)
def mark_my_attendance(data):
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
        else:
			#print dts
			for record in dts['records']:
				# print(record['present'])
				if not record['present']:
					record['present']=0
					#print 'in not present'
				frappe.db.sql("update `tabInvitation Member Details` set present=%s where name=%s",(record['present'],record['name']))
				mail_notify_msg = """Dear User, \n\n \t\tYour Attendance is updated by Leader '%s'. Please Check. \n\n Regards, \n\n Love World Synergy"""%(dts['username'])
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
							res = gcm.json_request(registration_ids=res[0], data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)

				return "Updated Attendance"


@frappe.whitelist(allow_guest=True)
def get_match_conditions(doctype,username):
	meta = frappe.get_meta(doctype)
	role_permissions = frappe.permissions.get_role_permissions(meta, username)
	user_permissions=frappe.db.sql("select defkey,defvalue from tabDefaultValue where defkey in ('Member','Group Churches','Zones','Cells','Churches','PCFs','Senior Cells','Cells','Regions') and parent=%s ",username,as_dict=1)  
	match_conditions = []
	#cond=''
	for item in user_permissions:
	    if item['defkey']==doctype:
	    	match_conditions.append(""" name ='{values}'""".format(values=item['defvalue']))
	    else:
		qry="select fieldname from tabDocField where options='"+cstr(item['defkey'])+"' and parent='"+cstr(doctype)+"'"
        	res=frappe.db.sql(qry)
        	if res:	
			match_conditions.append(""" {fieldname} ='{values}'""".format(doctype=doctype,fieldname=res[0][0],values=item['defvalue']))
	cond=''		
	if match_conditions :
		cond =  ' or '.join(match_conditions) 
		cond=' and  ('+ cond +' )'
	return match_conditions,cond


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
	match_conditions,data=get_match_conditions(dts['tbl'],dts['username'])
    	colmns=frappe.db.sql("select fieldname from tabDocField where fieldtype !='Section Break' and fieldtype !='Column Break' and parent='%s' and fieldname like '%%_name%%' order by idx limit 6 " %(dts['tbl']),as_list=1 )
    	cnd1=''
    	if match_conditions   :
		cond =  ' or '.join(match_conditions) 
		cnd1=" where "+ cond
		
	return frappe.db.sql("""select name ,%s as record_name  from `tab%s`  %s """%(','.join([x[0] for x in colmns ]),dts['tbl'], cnd1), as_dict=1)
	return frappe.db.sql("""select name ,%s as record_name  from `tab%s` where %s order by creation desc"""%(','.join([x[0] for x in colmns ]),dts['tbl'], ' or '.join(match_conditions)), as_dict=1)


@frappe.whitelist(allow_guest=True)
def get_database_masters1(data):
	"""
	Member can mark their attandence of meeting
	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	result={}
	if not valid:
		return {
				"status":"401",
				"message":"User name or Password is incorrect"
		}
	
	match_conditions,data=get_match_conditions(dts['tbl'],dts['username'])
    	colmns=frappe.db.sql("select fieldname from tabDocField where fieldtype !='Section Break' and fieldtype !='Column Break' and parent='%s' and fieldname like '%%_name%%' order by idx limit 6 " %(dts['tbl']),as_list=1 )
    	cnd1,cnd2='',''
    	if match_conditions   :
		cond =  ' or '.join(match_conditions) 
		cnd1=" where "+ cond
	total_count= frappe.db.sql("""select ifnull(count(name),0) from `tab%s`  %s """%(dts['tbl'], cnd1))
	start_index=(cint(dts['page_no'])-1)* 20	
	
	if cint(dts['page_no'])==1:
		start_index=0
	else:
		start_index=(cint(dts['page_no'])-1)*20
	end_index =start_index+20	
	if total_count[0][0]<=end_index:
		end_index=total_count[0][0] 
	result['total_count']=total_count[0][0]
	result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
	result['records']=frappe.db.sql("""select name ,%s as record_name from `tab%s`  %s order by name limit %s,20"""%(','.join([x[0] for x in colmns ]),dts['tbl'], cnd1,cint(start_index)), as_dict=1)
	return result



@frappe.whitelist(allow_guest=True)
def get_database_masters(data):
	"""
	this method will give list of all master with filters and pagination logic
	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	result={}
	if not valid:
		return {
				"status":"401",
				"message":"User name or Password is incorrect"
		}

	if dts['tbl']=='New Converts':
		dts['tbl']='First Timer'
		if 'filters' not in dts:
			dts['filters']={}
		dts['filters']['New Converts']=''
	elif dts['tbl']=='Membership Strength' :
		if 'filters' not in dts:
			dts['filters']={}
		if dts['filters']['flag']=='New Converts':
			dts['tbl']='First Timer'
			if 'filters' not in dts:
				dts['filters']={}
			dts['filters']['New Converts']=''
		else:
			dts['tbl']='Member'
	elif dts['tbl']=='Partnership Records' :
		if 'filters' not in dts:
			dts['filters']={}
	  	dts['tbl']='Partnership Record'	
	#return dts
	match_conditions,data=get_match_conditions(dts['tbl'],dts['username'])
	colmns={
	        "Invitees and Contacts":"name,invitee_contact_name,sex,email_id",
		"First Timer":"name,ftv_name,surname,sex,email_id",
		"Member":"name,member_name,surname,email_id",		
		"Partnership Record":"name,partnership_arms,FORMAT(amount,2) as amount,giving_or_pledge",
		"Cells":"name,cell_name,senior_cell,senior_cell_name",
		"PCFs":"name,pcf_name,church,church_name",
		"Senior Cells":"name,senior_cell_name,pcf,pcf_name"
	}
    	cond,match_cond,fltr_cnd='','',''
    	fltrs=[]
    	if 'filters' in dts:
    		if 'from_date' in dts['filters']:
    		    	dts['filters']['from_date']=dts['filters']['from_date'][6:]+"-"+dts['filters']['from_date'][3:5]+"-"+dts['filters']['from_date'][:2]
  		if 'to_date' in dts['filters']:
    		    	dts['filters']['to_date']=dts['filters']['to_date'][6:]+"-"+dts['filters']['to_date'][3:5]+"-"+dts['filters']['to_date'][:2]
    	        if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
    	        	fltrs.append(" date(creation) >= '%s' and date(creation) <='%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
    	        elif 'from_date' in dts['filters'] :
    	        	fltrs.append(" date(creation) >= '%s' " %dts['filters']['from_date'])
    	        elif 'to_date' in dts['filters'] :
    	        	fltrs.append(" date(creation) <= '%s' " %dts['filters']['to_date'])    
    	 	for key,value in dts['filters'].iteritems():
    	 		if key in ('region','zone','church_group','church','pcf','senior_cell','cell'):
    	        		fltrs.append(" %s = '%s' " %(key,value))
     
    	        if 'Week' in dts['filters'] :
    	        	fltrs.append(" date(creation)>= DATE_ADD(CURDATE(), INTERVAL(1-DAYOFWEEK(CURDATE())) DAY) AND date(creation)<= DATE_ADD(CURDATE(), INTERVAL(7-DAYOFWEEK(CURDATE())) DAY) ")    
    	        elif 'Month' in dts['filters'] :
    	        	if isinstance(dts['filters']['Month'], basestring):
    	        		fltrs.append(" YEAR(creation)=YEAR(now()) and MONTH(creation)=MONTH(now()) ")
    	        	else:	
    	        		fltrs.append(" year(creation) = year(curdate() ) and month(creation) = month(curdate())")
    	        elif 'Year' in dts['filters'] :
    	        	fltrs.append(" YEAR(creation)=YEAR(now()) ")  
    	        if 'New Converts' in dts['filters'] :
    	        	fltrs.append(" is_new_convert='Yes' ") 
       	        elif 'Giving' in dts['filters'].values() :
    	        	fltrs.append(" giving_or_pledge='Giving' ")
    	        elif 'Pledge' in dts['filters'].values() :
    	        	fltrs.append(" giving_or_pledge='Pledge' ")    
    	        	   
 		fltr_cnd=' and '.join([x for x in fltrs])
    	if match_conditions   :
		match_cond =  ' or '.join(match_conditions) 
	if len(fltr_cnd)>1 and match_conditions :
		cond+= " where "+ fltr_cnd + " and ("+match_cond+")"
	elif len(fltr_cnd)>1:
	       	cond+= " where "+ fltr_cnd
	elif match_conditions:
	       	cond+= " where "+ match_cond
	#frappe.errprint(cond)
	total_count= frappe.db.sql("""select ifnull(count(name),0) from `tab%s`  %s """%(dts['tbl'], cond))	
	if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
		dts['page_no']=1
		start_index=0
	else:   
		start_index=(cint(dts['page_no'])-1)*20
	end_index =start_index+20	
	if total_count[0][0]<=end_index:
		end_index=total_count[0][0] 
	result['total_count']=total_count[0][0]
	#frappe.errprint(cond)
	result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
	result['records']=frappe.db.sql("""select %s from `tab%s`  %s order by name limit %s,20"""%(colmns[dts['tbl']],dts['tbl'], cond,cint(start_index)), as_dict=1)
	return result

@frappe.whitelist(allow_guest=True)
def get_master_details(data):
	"""
	Get details of selected pcf
	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	if not valid:
		return {
				"status":"401",
				"message":"User name or Password is incorrect"
		}
	dictnory={
		"Cells":"cell_code,cell_name,senior_cell,pcf,church,church_group,zone,region,contact_phone_no,contact_email_id,contact_email_id as cell_leader,meeting_location,address,lat,lon",
		"Senior Cells":"senior_cell_code,senior_cell_name,meeting_location,pcf,church,church_group,zone,region,contact_phone_no,contact_email_id,contact_email_id as senior_cell_leader",
		"PCFs":"pcf_code,pcf_name,church,church_group,zone,region,contact_phone_no,contact_email_id,contact_email_id as pcf_leader",
		"Churches":"church_code,church_name,church_group,zone,region,phone_no,email_id,address",
		"Group Churches":"church_group_code,church_group,zone,region,contact_phone_no,contact_email_id,group_church_hq",
		"Zones":"zone_code,zone_name,region,contact_phone_no,contact_email_id,zonal_hq",
		"Regions":"region_code,region_name,contact_phone_no,contact_email_id",
		"Invitees and Contacts":"name,title,invitee_contact_name,sex,convert_invitee_contact_to_ft,date_of_convert,date_of_birth,age_group,invited_by,source_of_invitation,phone_1,email_id",
		"First Timer":"name,ftv_name ,surname,date_of_birth,marital_info,phone_1,phone_2,email_id,email_id_2,address,office_address,image",
		"Partnership Record":"name,partnership_arms,ministry_year,is_member,member,date,cell,FORMAT(amount,2) as amount,giving_or_pledge,giving_type,type_of_pledge,instrument__no,bank_name,branch"
	}
	tablename=dts['tbl']
	res=frappe.db.sql("select %s from `tab%s` where name='%s'"  %(dictnory[tablename],dts['tbl'],dts['name']),as_dict=True)
	return res


@frappe.whitelist(allow_guest=True)
def update_master_details(data):
	"""
	Get details of selected pcf
	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	if not valid:
		return {
				"status":"401",
				"message":"User name or Password is incorrect"
		}
	dictnory={
		"Cells":"cell_code,cell_name,senior_cell,pcf,church,church_group,zone,region,contact_phone_no,contact_email_id,contact_email_id as cell_leader,meeting_location,address,lat,lon",
		"Senior Cells":"senior_cell_code,senior_cell_name,meeting_location,pcf,church,church_group,zone,region,contact_phone_no,contact_email_id,contact_email_id as senior_cell_leader",
		"PCFs":"pcf_code,pcf_name,church,church_group,zone,region,contact_phone_no,contact_email_id,contact_email_id as pcf_leader",
		"Churches":"church_code,church_name,church_group,zone,region,phone_no,email_id,address",
		"Group Churches":"church_group_code,church_group,zone,region,contact_phone_no,contact_email_id,group_church_hq",
		"Zones":"zone_code,zone_name,region,contact_phone_no,contact_email_id,zonal_hq",
		"Regions":"region_code,region_name,contact_phone_no,contact_email_id",
		"Invitees and Contacts":"title,invitee_contact_name,sex,convert_invitee_contact_to_ft,date_of_convert,date_of_birth,age_group,invited_by,source_of_invitation,phone_1,email_id",
		"First Timer":"ftv_name,surname,date_of_birth,marital_info,phone_1,phone_2,email_id,email_id_2,address,office_address,image",
		"Partnership Record":"partnership_arms,ministry_year,is_member,member,date,cell,FORMAT(amount,2) as amount,giving_or_pledge,giving_type,type_of_pledge,instrument__no,bank_name,branch"
	}
	set_cols = ",".join( [ " {0} = '{1}' ".format(key, value)  for key ,value in dts.get("records").items() if key and key!='name'])
	qry="update `tab%s` set %s where name='%s'" %(dts['tbl'],set_cols,dts['records']['name'])  
	#return qry
	frappe.db.sql(qry)
	return {
				"status":"200",
				"message":"Record Updated Successfully..!"
		}



@frappe.whitelist(allow_guest=True)
def partnership_arms(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        } 
    #match_conditions,data=get_match_conditions('Partnership Record',dts['username'])
    column={
				"Regions":"region",
				"Zones":"zone",
				"Group Churches":"church_group",
				"Churches":"church",
				"PCFs":"pcf",
				"Senior Cells":"senior_cell",
				"Cells":"cell"
			}
    cond="where giving_or_pledge= '%s' "%(dts['giving_or_pledge'])
    if 'flag' in dts:       
   		cond+= " and `tabPartnership Record`.`member`= ( SELECT defvalue FROM tabDefaultValue WHERE defvalue=`tabPartnership Record`.`member` and defkey='Member' and tabDefaultValue.`parent`='"+cstr(dts['username'])+"')"
    else:
    	res=frappe.db.sql("select defkey,defvalue from tabDefaultValue where defkey<>'Member' and defkey in ('Group Churches','Zones','Cells','Churches','PCFs','Senior Cells','Cells','Regions') and parent='%s'" %dts['username'],as_list=1)
    	cond_list=[]
    	for key,value in res:
    		cond_list.append(" %s = '%s' " %(column[key],value))
    	cond+="and ("+" or ".join([x for x in cond_list])+")"
    data=frappe.db.sql("select partnership_arms,ifnull(FORMAT(sum(amount),2),'0.00') as amount from `tabPartnership Record` %s group by partnership_arms" %(cond),as_dict=True)
    return data
    
    
    
@frappe.whitelist(allow_guest=True)
def partnership_arms_list(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        } 
    #match_conditions,data=get_match_conditions('Partnership Record',dts['username'])
    fltr_cnd=''
    fltrs=[]
    if 'filters' in dts:
   	if 'from_date' in dts['filters']:
    	    	dts['filters']['from_date']=dts['filters']['from_date'][6:]+""+dts['filters']['from_date'][3:5]+""+dts['filters']['from_date'][:2]
  	if 'to_date' in dts['filters']:
    	    	dts['filters']['to_date']=dts['filters']['to_date'][6:]+""+dts['filters']['to_date'][3:5]+""+dts['filters']['to_date'][:2]        
  	if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
  	     	fltrs.append(" date(creation) between '%s' and '%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
    	elif 'from_date' in dts['filters'] :
    	        	fltrs.append(" creation >= '%s' " %dts['filters']['from_date'])
    	        
    	elif 'to_date' in dts['filters'] :
    	        	fltrs.append(" creation <= '%s' " %dts['filters']['to_date'])    
    	for key,value in dts['filters'].iteritems():
    	 	if key in ('region','zone','church_group','church','pcf','senior_cell','cell'):
    	       		fltrs.append(" %s = '%s' " %(key,value))
	fltr_cnd=" and "+' and '.join([x for x in fltrs])
	
    cond="where partnership_arms='%s' and giving_or_pledge= '%s' %s "%(dts['partnership_arms'],dts['giving_or_pledge'],fltr_cnd)
    if 'flag' in dts:       
   		cond+= " and `tabPartnership Record`.`member`= ( SELECT defvalue FROM tabDefaultValue WHERE defvalue=`tabPartnership Record`.`member` and tabDefaultValue.`parent`='"+cstr(dts['username'])+"')"
    else:
    	column={
				"Regions":"region",
				"Zones":"zone",
				"Group Churches":"church_group",
				"Churches":"church",
				"PCFs":"pcf",
				"Senior Cells":"senior_cell",
				"Cells":"cell"
			}
	res=frappe.db.sql("select defkey,defvalue from tabDefaultValue where defkey<>'Member' and defkey in ('Group Churches','Zones','Cells','Churches','PCFs','Senior Cells','Cells','Regions') and parent='%s'" %dts['username'],as_list=1)
    	cond_list=[]
    	for key,value in res:
    		cond_list.append(" %s = '%s' " %(column[key],value))
    	cond+="and ("+" or ".join([x for x in cond_list])+")"
    #frappe.errprint(cond)
    total_count= frappe.db.sql("""select ifnull(count(name),0) from `tabPartnership Record`  %s """%(cond))	
    if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
	dts['page_no']=1
	start_index=0
    else:   
	start_index=(cint(dts['page_no'])-1)*20
    end_index =start_index+20	
    if total_count[0][0]<=end_index:
	end_index=total_count[0][0] 
    result={}
    result['total_count']=total_count[0][0]
    result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
    result['records']=frappe.db.sql("""select name,date,cell,ifnull(FORMAT(amount,2),'0.00') as amount,member,member_name,giving_type,type_of_pledge from `tabPartnership Record`  %s order by name limit %s,20"""%(cond,cint(start_index)), as_dict=1)
    return result


@frappe.whitelist(allow_guest=True)
def create_partnership_reocrd(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    #print "request for create_partnership_reocrd request----------------"
    #print dts
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        } 	
    pr=frappe.new_doc("Partnership Record")
    pr.partnership_arms=dts['partnership_arms']
    pr.amount=dts['amount']
    pr.date=dts['date']
    #frappe.errprint(pr.date)
    try :
    	pr.ministry_year=get_fiscal_year(dts['date'])[0]
    except Exception ,e:
    	return {
                "status":"402",
                "message":"Ministry Year not found for %s " %(dts['date'])
        } 
    pr.is_member='Member'
    pr.member=dts['member']
    pr.member_name=dts['member_name']
    pr.giving_or_pledge=dts['giving_or_pledge']
    if dts['giving_or_pledge']=='Giving' :
    	if dts['giving_type'] =='Cheque':
	    pr.giving_type=dts['giving_type']
	    pr.instrument__no=dts['instrument_no']
	    pr.instrument_date=dts['instrument_date']
	    pr.bank_name=dts['bank_name']
	    pr.branch=dts['branch']
    else:
    	pr.type_of_pledge=dts['type_of_pledge']
    hr_details=frappe.db.sql("select cell,cell_name,senior_cell,senior_cell_name,pcf,pcf_name,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name from tabMember where name='%s'" %(dts['member']))
    if hr_details:
    	pr.cell=hr_details and hr_details[0][0] or ''
    	pr.cell_name=hr_details and hr_details[0][1] or ''
    	pr.senior_cell=hr_details and hr_details[0][2] or ''
    	pr.senior_cell_name=hr_details and hr_details[0][3] or ''
    	pr.pcf=hr_details and hr_details[0][4] or ''
    	pr.pcf_name=hr_details and hr_details[0][5] or ''
    	pr.church=hr_details and hr_details[0][6] or ''
    	pr.church_name=hr_details and hr_details[0][7] or ''
    	pr.church_group=hr_details and hr_details[0][8] or ''
    	pr.church_group_name=hr_details and hr_details[0][9] or ''
    	pr.zone=hr_details and hr_details[0][10] or ''
    	pr.zone_name=hr_details and hr_details[0][11] or ''
    	pr.region=hr_details and hr_details[0][12] or ''
    	pr.region_name=hr_details and hr_details[0][13] or ''

    pr.flags.ignore_mandatory = True
    pr.insert(ignore_permissions=True)
    frappe.db.set_value("Partnership Record", pr.name, "date", dts['date'])
    return {
                "status":"200",
                "message":"Successfully created partnership record "+pr.name
        } 


@frappe.whitelist(allow_guest=True)
def get_partnership_arms(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        } 
    return frappe.db.sql("select name from `tabPartnership Arms`",as_dict=1)
    #return res

@frappe.whitelist(allow_guest=True)
def get_db_records(data):
	"""
	Get details of selected master and filter
	"""
	dts=json.loads(data)
	qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
	valid=frappe.db.sql(qry)
	if not valid:
		return {
				"status":"401",
				"message":"User name or Password is incorrect"
		}
	dictnory={
	    "Invitees and Contacts":"name,invitee_contact_name,sex,email_id",
	    "First Timer":"name,ftv_name,sex,email_id",
		"Members":"name,member_name,sex,email_id",		
		"Partnership Record":"name,partnership_arms,FORMAT(amount,2) as amount,giving_or_pledge,member_name"
	}
	res=frappe.db.sql("select %s from `tab%s` limit 20"  %(dictnory[dts['tbl']],dts['tbl']),as_dict=True)
	return res



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
def event_list_new(data):
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
    fltr_cnd=''
    fltrs=[]
    if 'filters' in dts:
   	if 'from_date' in dts['filters']:
    	    	dts['filters']['from_date']=dts['filters']['from_date'][6:]+""+dts['filters']['from_date'][3:5]+""+dts['filters']['from_date'][:2]
  	if 'to_date' in dts['filters']:
    	    	dts['filters']['to_date']=dts['filters']['to_date'][6:]+""+dts['filters']['to_date'][3:5]+""+dts['filters']['to_date'][:2]    
  	if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
  	     	fltrs.append(" date(creation) between '%s' and '%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
    	elif 'from_date' in dts['filters'] :
    	        	fltrs.append(" creation >= '%s' " %dts['filters']['from_date'])
    	        
    	elif 'to_date' in dts['filters'] :
    	        	fltrs.append(" creation <= '%s' " %dts['filters']['to_date'])    
    	if 'event_type' in dts['filters']:
  	     	fltrs.append(" event_type= '%s'" %(dts['filters']['event_type']))
    	for key,value in dts['filters'].iteritems():
    	 	if key in ('region','zone','church_group','church','pcf','senior_cell','cell'):
    	       		fltrs.append(" %s = '%s' " %(key,value))
	fltr_cnd=' and '.join([x for x in fltrs])+ " and "

    tot_qry="""select ifnull(count(name),0) from tabEvent where %s %s """%(fltr_cnd,get_permission_query_conditions(dts['username']))
    total_count= frappe.db.sql(tot_qry)	
    if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
	dts['page_no']=1
	start_index=0
    else:   
	start_index=(cint(dts['page_no'])-1)*20
    end_index =start_index+20	
    if total_count[0][0]<=end_index:
	end_index=total_count[0][0] 
    result={}
    result['total_count']=total_count[0][0]
    result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
    #result['records']=frappe.db.sql("""select name,date,cell,ifnull(FORMAT(amount,2),'0.00') as amount,member,member_name from `tabPartnership Record`  %s order by name limit %s,20"""%(cond,cint(start_index)), as_dict=1)
    #return result    
    qry=" select name as event_name,address,starts_on as event_date,subject from tabEvent where "+ fltr_cnd+" "+ get_permission_query_conditions(dts['username'])+" order by name limit "+cstr(start_index)+",20"
    result['records']=frappe.db.sql(qry,as_dict=True)
    return result    

        
@frappe.whitelist(allow_guest=True)
def event_participents(data):
    """
    Event details og selected event
    """
    dts=json.loads(data)
    # print "request in event_participents"
    # print dts
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }       
    data=frappe.db.sql("select a.name as `name` ,a.member,a.member_name,ifnull(a.present,0) as present,a.comments from `tabInvitation Member Details`  a,`tabAttendance Record` b  where b.attendance_type='Event Attendance' and a.parent=b.name and b.event=%s order by a.member ",dts['event_id'],as_dict=True)
    # print "responce----------------"
    # print data
    return data
                

@frappe.whitelist(allow_guest=True)
def event_attendance(data):
    """
    Give provisin for sms email and push notification
    update Attendance Record
    """
    dts=json.loads(data)
    # print "request in event_attendance"
    # print dts
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

    fltr_cnd=''
    fltrs=[]
    if 'filters' in dts:
   	if 'from_date' in dts['filters']:
    	    	dts['filters']['from_date']=dts['filters']['from_date'][6:]+""+dts['filters']['from_date'][3:5]+""+dts['filters']['from_date'][:2]
  	if 'to_date' in dts['filters']:
    	    	dts['filters']['to_date']=dts['filters']['to_date'][6:]+""+dts['filters']['to_date'][3:5]+""+dts['filters']['to_date'][:2]    
  	if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
  	     	fltrs.append(" date(a.creation) between '%s' and '%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
    	elif 'from_date' in dts['filters'] :
    	        	fltrs.append(" a.creation >= '%s' " %dts['filters']['from_date'])
    	        
    	elif 'to_date' in dts['filters'] :
    	        	fltrs.append(" a.creation <= '%s' " %dts['filters']['to_date'])    
    	if 'event_type' in dts['filters']:
  	     	fltrs.append(" a.event_type= '%s'" %(dts['filters']['event_type']))
    	for key,value in dts['filters'].iteritems():
    	 	if key in ('region','zone','church_group','church','pcf','senior_cell','cell'):
    	       		fltrs.append(" a.%s = '%s' " %(key,value))
	fltr_cnd="and "+' and '.join([x for x in fltrs])
    #return fltr_cnd
    tot_qry="""select ifnull(count(a.subject),0) from `tabEvent` a, `tabAttendance Record` b,`tabInvitation Member Details` c where attendance_type='Event Attendance' and a.name=b.event and b.name=c.parent and c.member in (select a.name from tabMember a,tabUser b where a.email_id=b.name and b.name='%s') %s """%(dts['username'],fltr_cnd)
    total_count= frappe.db.sql(tot_qry)	
    if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
	dts['page_no']=1
	start_index=0
    else:   
	start_index=(cint(dts['page_no'])-1)*20
    end_index =start_index+20	
    if total_count[0][0]<=end_index:
	end_index=total_count[0][0] 
    result={}
    result['total_count']=total_count[0][0]
    result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
    #result['records']=frappe.db.sql("""select name,date,cell,ifnull(FORMAT(amount,2),'0.00') as amount,member,member_name from `tabPartnership Record`  %s order by name limit %s,20"""%(cond,cint(start_index)), as_dict=1)
    #return result    
    qry=" select a.subject ,a.name as `event_code`,a.starts_on as event_date,a.ends_on as `to_date`, c.member_name,a.address,c.name,ifnull(c.present,0) as present,comments from `tabEvent` a, `tabAttendance Record` b,`tabInvitation Member Details` c where attendance_type='Event Attendance' and a.name=b.event and b.name=c.parent and c.member in (select a.name from tabMember a,tabUser b where a.email_id=b.name and b.name='"+dts['username']+"') "+ fltr_cnd+" order by b.name limit "+cstr(start_index)+",20"

    result['records']=frappe.db.sql(qry,as_dict=True)
    return result    

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
    #print dts
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    dictnory={
        "Cells":"senior_cell,senior_cell_name,pcf,pcf_name,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name",
        "Senior Cells":"pcf,pcf_name,church,church_name,church_group,group_church_name,zone,zone_name,region,region_name",
        "PCFs":"church,church_name,church_group,group_church_name,zone,zone_name,region,region_name",
        "Churches":"church_group,church_group_name,zone,zone_name,region,region_name",
        "Group Churches":"zone,zone_name,region,region_name",
        "Zones":"region,region_name"
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
    columns={
            "Senior Cells":"cell_name",
            "PCFs":"senior_cell_name",
            "Churches":"pcf_name",
            "Group Churches":"church_name",
            "Zones":"church_group",
            "Regions":"zone_name"
    }
    tablename=dts['tbl']
    fields={
            "Senior Cells":"Cells",
            "PCFs":"Senior Cells",
            "Churches":"PCFs",
            "Group Churches":"Churches",
            "Zones":"Group Churches",
            "Regions":"Zones"
    }
    fieldname=dts['tbl']
    res=frappe.db.sql("select name,%s from `tab%s` where %s='%s'"  %(columns[tablename],fields[fieldname],wheres[tablename],dts['name']),as_dict=True)
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
    data=frappe.db.sql("""select  a.name ,b.owner as _assign,b.assigned_by as assignee,a.subject ,a.exp_end_date,a.status,a.priority,a.description,a.cell,a.senior_cell,a.pcf from `tabTask` a, `tabToDo` b where a.status in ('Open','Working' )  and a.name=b.reference_name and a.exp_start_date is not null and a.owner='%s' or _assign='%s' """ %(dts['username'],dts['username']),as_dict=True)
    return data


@frappe.whitelist(allow_guest=True)
def task_list_team(data):
	#gangadhar
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }    
    data=frappe.db.sql("""select  a.name ,b.owner as _assign,b.assigned_by as assignee,a.subject ,a.exp_end_date,a.status,a.priority,a.description,a.cell,a.senior_cell,a.pcf from `tabTask` a, `tabToDo` b where a.status in ('Open','Working' )  and a.name=b.reference_name and a.exp_start_date is not null and a.owner='%s' or b.assigned_by='%s' """ %(dts['username'],dts['username']),as_dict=True)
    #data=frappe.db.sql("""select a.name ,REPLACE(REPLACE(SUBSTRING_INDEX(a._assign,'"',2),'"',''),'[','') as _assign,a.owner as assignee,a.subject ,a.exp_end_date,a.status,a.priority,a.description,a.cell,a.senior_cell,a.pcf from `tabTask` a where a.status in ('Open','Working' )  and a.exp_start_date is not null and a.owner='%s'"""%(dts['username']),as_dict=True)
    return data


@frappe.whitelist(allow_guest=True)
def task_list_new(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    fltrs=[]
    result={}
    fltr_cnd=''
    if 'filters' in dts:
   		if 'from_date' in dts['filters']:
    		    	dts['filters']['from_date']=dts['filters']['from_date'][6:]+""+dts['filters']['from_date'][3:5]+""+dts['filters']['from_date'][:2]
  		if 'to_date' in dts['filters']:
    		    	dts['filters']['to_date']=dts['filters']['to_date'][6:]+""+dts['filters']['to_date'][3:5]+""+dts['filters']['to_date'][:2]    
    	        if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
    	        	fltrs.append(" a.exp_end_date between '%s' and '%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
    	        elif 'from_date' in dts['filters'] :
    	        	fltrs.append(" a.exp_end_date >= '%s' " %dts['filters']['from_date'])
    	        elif 'to_date' in dts['filters'] :
    	        	fltrs.append(" a.exp_end_date <= '%s' " %dts['filters']['to_date']) 
    	        for key,value in dts['filters'].iteritems():
    	 		if key in ('status','priority'):
    	        		fltrs.append(" a.%s = '%s' " %(key,value))
    		fltr_cnd=" and "+' and '.join([x for x in fltrs])
    total_count= frappe.db.sql("""select count(a.name) from `tabTask` a, `tabToDo` b where a.status in ('Open','Working' )  and a.name=b.reference_name %s and a.exp_start_date is not null and b.owner='%s' """ %(fltr_cnd,dts['username']))
    #return total_count
    if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
	dts['page_no']=1
	start_index=0
    else:   
	start_index=(cint(dts['page_no'])-1)*20
    end_index =start_index+20	
    if total_count[0][0]<=end_index:
	end_index=total_count[0][0] 
    result['total_count']=total_count[0][0]
    result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
    result['records']=frappe.db.sql("""select a.name ,b.owner as _assign,b.assigned_by as assignee,a.subject ,a.exp_end_date,a.comment,a.status,a.priority,a.description,a.cell,a.senior_cell,a.pcf from `tabTask` a, `tabToDo` b where a.status in ('Open','Working' )  and a.name=b.reference_name %s and a.exp_start_date is not null and b.owner='%s'  order by a.name limit %s,20""" %(fltr_cnd,dts['username'],cint(start_index)),as_dict=True)
    return result

@frappe.whitelist(allow_guest=True)
def task_list_team_new(data):
    #gangadhar
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }

    fltrs=[]
    result={}
    fltr_cnd=''
    if 'filters' in dts:
   		if 'from_date' in dts['filters']:
    		    	dts['filters']['from_date']=dts['filters']['from_date'][6:]+""+dts['filters']['from_date'][3:5]+""+dts['filters']['from_date'][:2]
  		if 'to_date' in dts['filters']:
    		    	dts['filters']['to_date']=dts['filters']['to_date'][6:]+""+dts['filters']['to_date'][3:5]+""+dts['filters']['to_date'][:2]    
    	        if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
    	        	fltrs.append(" t.exp_end_date between '%s' and '%s'" %(dts['filters']['from_date'],dts['filters']['to_date']))
    	        elif 'from_date' in dts['filters'] :
    	        	fltrs.append(" t.exp_end_date >= '%s' " %dts['filters']['from_date'])
    	        elif 'to_date' in dts['filters'] :
    	        	fltrs.append(" t.exp_end_date <= '%s' " %dts['filters']['to_date']) 
    	        for key,value in dts['filters'].iteritems():
    	 		if key in ('status','priority'):
    	        		fltrs.append(" t.%s = '%s' " %(key,value))
    		fltr_cnd=" and "+' and '.join([x for x in fltrs])
    total_count= frappe.db.sql("""select count(t.name) FROM tabTask t, tabToDo d WHERE t.name IN ( SELECT DISTINCT reference_name FROM tabToDo WHERE assigned_by='%s' ) AND t.name=d.reference_name %s  and d.status <>'Closed' AND t.status<>'Closed'""" %(dts['username'],fltr_cnd))
    if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
	dts['page_no']=1
	start_index=0
    else:   
	start_index=(cint(dts['page_no'])-1)*20
    end_index =start_index+20	
    if total_count[0][0]<=end_index:
	end_index=total_count[0][0] 
    result['total_count']=total_count[0][0]
    result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
    #result['records']=frappe.db.sql("""select a.name ,b.owner as _assign,b.assigned_by as assignee,a.subject ,a.exp_end_date,a.status,a.comment,a.priority,a.description,a.cell,a.senior_cell,a.pcf from `tabTask` a, `tabToDo` b where a.status in ('Open','Working' )  and a.name=b.reference_name %s and a.exp_start_date is not null and (a.owner='%s' or b.assigned_by='%s') order by a.name limit %s,20""" %(fltr_cnd,dts['username'],dts['username'],cint(start_index)),as_dict=True)
    result['records']=frappe.db.sql("SELECT DISTINCT (t.name),t.description,t.subject ,t.exp_end_date,t.status,t.priority,d.assigned_by AS asignee,t.comment,t.cell,t.senior_cell,t.pcf,d.owner AS _assign FROM tabTask t, tabToDo d WHERE t.name IN ( SELECT DISTINCT reference_name FROM tabToDo WHERE assigned_by='%s' ) AND t.name=d.reference_name and d.status <>'Closed' and t.status<>'Closed' %s order by t.name limit %s,20" %(dts['username'],fltr_cnd,cint(start_index)),as_dict=1)
    return result



@frappe.whitelist(allow_guest=True)
def task_update(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    #print dts
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    if dts['followup_task']:        
        frappe.db.sql("update `tabToDo` set description=%s,status='Closed' where reference_name=%s",(dts['description'],dts['name']),as_dict=True) 
        dts['exp_start_date']=now()
        dts['doctype']='Task'
        dts['subject']='followup task for '+dts['name']
        assign=dts['_assign'][2:-2]
        if 'cell' in dts:
        	del dts['cell']
        if 'assignee' in dts:
        	del dts['assignee']
        if '_assign' in dts:
        	del dts['_assign']
        ma = frappe.get_doc(dts)
        ma.insert(ignore_permissions=True)
                
	task_obj = frappe.new_doc("ToDo")
	task_obj.description = dts['description']
	task_obj.status = 'Open'
	task_obj.priority = 'Medium'
	task_obj.date = nowdate()
	task_obj.owner = assign
	task_obj.reference_type = 'Task'
	task_obj.reference_name = dts['name']
	task_obj.assigned_by = dts['username']
	task_obj.insert(ignore_permissions=True)
	frappe.db.sql("update `tabTask` set description=%s,status='Closed',closing_date=%s, comment=%s where name=%s",('Closed the task and created followup task '+ma.name ,now(),dts['comment'],dts['name']),as_dict=True)
        return "Created followup taks "+ma.name+" and closed old task "+dts['name']
    else:
        frappe.db.sql("update `tabTask` set description=%s,status=%s,_assign=%s ,comment=%s where name=%s",(dts['description'],dts['status'],dts['_assign'],dts['comment'],dts['name']),as_dict=True)
        frappe.db.sql("update `tabToDo` set description=%s,status='Closed' where reference_name=%s",(dts['description'],dts['name']),as_dict=True)
        task_obj = frappe.new_doc("ToDo")
        task_obj.description = dts['description']
        task_obj.status = 'Open'
        task_obj.priority = 'Medium'
        task_obj.date = nowdate()
        task_obj.owner = dts['_assign'][2:-2]
        task_obj.reference_type = 'Task'
        task_obj.reference_name = dts['name']
        task_obj.assigned_by = dts['username']
        task_obj.insert(ignore_permissions=True)
	
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
    #print dts
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    #print dts
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }  
    dts['exp_start_date']=now()
    dts['doctype']='Task'
    dts['owner']=dts['username']
    del dts['assignee']
    #del dts['name']
    ma = frappe.get_doc(dts)
    ma.insert(ignore_permissions=True)
    #return ma.name
    todo_obj = frappe.new_doc("ToDo")
    todo_obj.description = dts['description']
    todo_obj.status = 'Open'
    todo_obj.priority = 'Medium'
    todo_obj.date = nowdate()
    todo_obj.owner = dts['_assign']
    todo_obj.reference_type = 'Task'
    todo_obj.reference_name = ma.name
    todo_obj.assigned_by = dts['username']
    todo_obj.insert(ignore_permissions=True)
    
    return ma.name+" created Successfully"


@frappe.whitelist(allow_guest=True)
def get_team_members(data):
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
		match_conditions,cond=get_match_conditions('Member',dts['username'])
		qry="select name as ID ,member_name,email_id as user_id from tabMember where user_id<> '"+dts['username']+"' and '1'='1' "+cond
		data=frappe.db.sql(qry,as_dict=True)
		return data



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
	dates={}

        year, month, day=nowdate().split('-')
        last_week=frappe.db.sql("SELECT FLOOR((DayOfMonth(now())-1)/7)+1")
        monthDict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        dates['Week1']='Week : '+cstr(last_week[0][0])
        dates['Month1']='Month : '+cstr(monthDict[int(month)])
        dates['Year1']='Year : '+cstr(year)

        data['dates']=dates

	match_conditions,cond=get_match_conditions('Invitees and Contacts',dts['username'])
	new_visitor=frappe.db.sql("select a.`Week` as `Week1`,b.`Month` as `Month1`,c.`Year` as `Year1` from (select count(name) as `Week` from `tabInvitees and Contacts` where date(creation) >= DATE_ADD(CURDATE(), INTERVAL(1-DAYOFWEEK(CURDATE())) DAY) AND  date(creation) <= DATE_ADD(CURDATE(), INTERVAL(7-DAYOFWEEK(CURDATE())) DAY)  %s ) a,(select count(name) as `Month` from `tabInvitees and Contacts` where YEAR(creation)=YEAR(now()) and MONTH(creation)=MONTH(now()) %s ) b,(select count(name) as `Year` from `tabInvitees and Contacts` where YEAR(creation)=YEAR(now()) %s)c"%( cond,cond,cond), as_dict=1)
        data['invities_contacts']=new_visitor

	match_conditions,cond=get_match_conditions('First Timer',dts['username'])
	new_born=frappe.db.sql("select a.`Week` as `Week2`,b.`Month` as `Month2`,c.`Year` as `Year2` from (select count(name) as `Week` from `tabFirst Timer` where date(creation) >= DATE_ADD(CURDATE(), INTERVAL(1-DAYOFWEEK(CURDATE())) DAY) AND  date(creation) <= DATE_ADD(CURDATE(), INTERVAL(7-DAYOFWEEK(CURDATE())) DAY)   and is_new_convert='Yes' %s ) a,(select count(name) as `Month` from `tabFirst Timer` where YEAR(creation)=YEAR(now()) and MONTH(creation)=MONTH(now()) and is_new_convert='Yes' %s ) b,(select count(name) as `Year` from `tabFirst Timer` where YEAR(creation)=YEAR(now()) and is_new_convert='Yes' %s )c" %( cond,cond,cond), as_dict=1)
        data['new_converts']=new_born
    
	first_timers=frappe.db.sql("select a.`Week` as `Week3`,b.`Month` as `Month3`,c.`Year` as `Year3` from (select count(name) as `Week` from `tabFirst Timer` where date(creation) >= DATE_ADD(CURDATE(), INTERVAL(1-DAYOFWEEK(CURDATE())) DAY) AND  date(creation) <= DATE_ADD(CURDATE(), INTERVAL(7-DAYOFWEEK(CURDATE())) DAY)   %s ) a,(select count(name) as `Month` from `tabFirst Timer` where YEAR(creation)=YEAR(now()) and MONTH(creation)=MONTH(now()) %s ) b,(select count(name) as `Year` from `tabFirst Timer` where YEAR(creation)=YEAR(now()) %s )c" %( cond,cond,cond), as_dict=1)
	
        data['first_timers']=first_timers
	
	match_conditions,cond=get_match_conditions('Member',dts['username'])
	membership_strength=frappe.db.sql("select a.month,a.total_member_count from ( SELECT COUNT(name) AS total_member_count,MONTHNAME(creation) as month FROM `tabMember` WHERE date(creation)>= date_sub(now(),INTERVAL 90 day) AND date(creation)<= CURDATE() %s GROUP BY YEAR(creation),MONTH(creation)  ) a  "%(cond) ,as_dict=1)
        if membership_strength:
               data['membership_strength']=membership_strength
        else:
        	import datetime
		mydate = datetime.datetime.now()
		mydate.strftime("%B")
                data['membership_strength']=[{"new_converts":0,"total_member_count":0,"month":mydate.strftime("%B")}]
	
        match_conditions,cond=get_match_conditions('Partnership Record',dts['username'])
        partnership=frappe.db.sql("SELECT MONTHNAME(creation) as Month,ifnull( ( SELECT SUM(amount) FROM `tabPartnership Record`   WHERE giving_or_pledge='Giving' %s  AND YEAR(creation)=YEAR(p.creation)  AND MONTH(creation)=MONTH(p.creation)),0) AS `giving`,   ifnull(   (  SELECT  SUM(amount)  FROM  `tabPartnership Record`  WHERE  giving_or_pledge='Pledge'  %s  AND YEAR(creation)=YEAR(p.creation)  AND MONTH(creation)=MONTH(p.creation)),0) AS pledge FROM   `tabPartnership Record` p WHERE   date(creation) between date_sub(now(),INTERVAL 120 DAY) AND now() AND partnership_arms IS NOT NULL %s GROUP BY   YEAR(creation),   MONTH(creation)"%(cond,cond,cond),as_dict=1)
        #frappe.errprint("SELECT MONTHNAME(creation) as Month,ifnull( ( SELECT SUM(amount) FROM `tabPartnership Record`   WHERE giving_or_pledge='Giving' %s  AND partnership_arms=p.partnership_arms   AND YEAR(creation)=YEAR(p.creation)  AND MONTH(creation)=MONTH(p.creation)),0) AS `giving`,   ifnull(   (  SELECT  SUM(amount)  FROM  `tabPartnership Record`  WHERE  giving_or_pledge='Pledge'  %s  AND partnership_arms=p.partnership_arms  AND YEAR(creation)=YEAR(p.creation)  AND MONTH(creation)=MONTH(p.creation)),0) AS pledge FROM   `tabPartnership Record` p WHERE   date(creation) between date_sub(now(),INTERVAL 120 DAY) AND now() AND partnership_arms IS NOT NULL %s GROUP BY   YEAR(creation),   MONTH(creation)"%(cond,cond,cond))
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
    match_conditions,cond=get_match_conditions('Partnership Record',dts['username'])
    qry="select name,church,partnership_arms,giving_or_pledge,sum(amount) as amount from `tabPartnership Record` where 1= '1' %s group by church,giving_or_pledge " %( cond)
    data=frappe.db.sql(qry,as_dict=True)
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
    data=frappe.db.sql("select name,partnership_arms,ministry_year,is_member,member,member_name as partner_name,date,church,giving_or_pledge,FORMAT(amount,2) as amount,type_of_pledge from `tabPartnership Record`  where name='%s'" %(dts['name']) ,as_dict=True)
    return data


@frappe.whitelist(allow_guest=True)
def update_partnership_arm(data):
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    frappe.db.sql("update `tabPartnership Record` set giving_or_pledge='%s',amount='%s' where name='%s'" %(dts['giving_or_pledge'],dts['amount'],dts['name']) ,as_dict=True)
    return "The Partnership Record '" +cstr(dts['name'])+ "' Is updated successfully."


@frappe.whitelist(allow_guest=True)
def search_glm(data):
        import frappe.sessions
        #frappe.response.update(frappe.sessions.get())
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
	#print dts
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
        data=frappe.db.sql(qry,as_dict=True)
        return data

@frappe.whitelist(allow_guest=True)
def search_group_member_church(data):
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
        cond=''
    	fltrs=[]
    	result={}        
        if 'church' in dts:
                key='church'
                value=dts['church']
                key1='church_name'
        elif 'group_church' in dts:
                key='group_church'
                value=dts['group']
                key1='church_group'
        elif 'zone' in dts:
                key='zone'
                value=dts['zone']
        elif 'region' in dts:
                key='region'
                value=dts['region']
        else:
                key='1'
                value=1
        cond+="where "+key+"='"+cstr(value)+"'"
    	if 'filters' in dts:
    		if 'from_date' in dts['filters']:
    		    	dts['filters']['from_date']=dts['filters']['from_date'][6:]+"-"+dts['filters']['from_date'][3:5]+"-"+dts['filters']['from_date'][:2]
  		if 'to_date' in dts['filters']:
    		    	dts['filters']['to_date']=dts['filters']['to_date'][6:]+"-"+dts['filters']['to_date'][3:5]+"-"+dts['filters']['to_date'][:2]    
    		if (('from_date' in dts['filters']) and ('to_date' in dts['filters'])):
    	        	cond+=" and date(creation) >= '%s' and date(creation) <='%s'" %(dts['filters']['from_date'],dts['filters']['to_date'])
    		elif 'from_date' in dts['filters'] :
    	        	cond+=" and creation>= '%s' " %dts['filters']['from_date']
    		elif 'to_date' in dts['filters'] :
    	        	cond+=" and creation <= '%s' " %dts['filters']['to_date'] 
        #return cond
        if 'search' in dts and dts['search']=='Group':
        		if 'member' in dts:
        	    		total_count= frappe.db.sql("select count(*) from (select name,cell_name,senior_cell,contact_phone_no,contact_email_id from tabCells %s and (name like '%%%s%%' or cell_name like '%%%s%%' ) union select name,senior_cell_name,pcf,contact_phone_no,contact_email_id from `tabSenior Cells` %s and (name like '%%%s%%' or senior_cell_name like '%%%s%%' ) union select name,pcf_name,church,contact_phone_no,contact_email_id from `tabPCFs` %s  and (name like '%%%s%%' or pcf_name like '%%%s%%' )) x " %(cond ,dts['member'],dts['member'],cond,dts['member'],dts['member'],cond,dts['member'],dts['member']))
        	    	else:
        	    		total_count= frappe.db.sql("select count(*) from (select name,cell_name,senior_cell,contact_phone_no,contact_email_id from tabCells %s union select name,senior_cell_name,pcf,contact_phone_no,contact_email_id from `tabSenior Cells` %s union select name,pcf_name,church,contact_phone_no,contact_email_id from `tabPCFs` %s ) x " %(cond,cond,cond))
    		 	if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
					dts['page_no']=1
					start_index=0
    			else:   
					start_index=(cint(dts['page_no'])-1)*20
    			end_index =start_index+20	
    			if total_count and (total_count[0][0]<=end_index):
					end_index=total_count[0][0] 
    			result['total_count']=total_count[0][0]
    			result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
    			if 'member' in dts:
    				result['records']=frappe.db.sql("select name as id , 'Cells' as type,cell_name as name,contact_phone_no,contact_email_id from tabCells %s  and (name like '%%%s%%' or cell_name like '%%%s%%' ) union select name  as id,'Senior Cells' as type,senior_cell_name as name,contact_phone_no,contact_email_id from `tabSenior Cells` %s and (name like '%%%s%%' or senior_cell_name like '%%%s%%' ) union select name  as id,'PCFs' as type,pcf_name as name,contact_phone_no,contact_email_id from `tabPCFs` %s and (name like '%%%s%%' or pcf_name like '%%%s%%' ) order by type,name limit %s,20" %(cond ,dts['member'],dts['member'],cond,dts['member'],dts['member'],cond,dts['member'],dts['member'],cint(start_index)),as_dict=True)
                        	return result
    			
                        result['records']=frappe.db.sql("select name as id , 'Cells' as type,cell_name as name,contact_phone_no,contact_email_id from tabCells %s union select name  as id,'Senior Cells' as type,senior_cell_name as name,contact_phone_no,contact_email_id from `tabSenior Cells` %s union select name  as id,'PCFs' as type,pcf_name as name,contact_phone_no,contact_email_id from `tabPCFs` %s order by type,name limit %s,20" %(cond,cond,cond,cint(start_index)),as_dict=True)
                        return result
        elif 'search' in dts and dts['search']=='Church':
        		if 'member' in dts:
        	    		total_count= frappe.db.sql("select count(*) from (select name as id , 'Churches' as type,church_name as name,phone_no,email_id from tabChurches %s and (name like '%%%s%%' or church_name like '%%%s%%' ) union select name as id , 'Group Churches' as type,church_group as name,contact_phone_no,contact_email_id from `tabGroup Churches` %s and (name like '%%%s%%' or church_group like '%%%s%%' ) union select name as id , 'Zones' as type,zone_name as name,contact_phone_no,contact_email_id from `tabZones`  %s and (name like '%%%s%%' or zone_name like '%%%s%%' ) union select name as id , 'Regions' as type,region_name as name,contact_phone_no,contact_email_id from `tabRegions` %s and (name like '%%%s%%' or region_name like '%%%s%%' ))x "%(cond,dts['member'],dts['member'],cond,dts['member'],dts['member'],cond,dts['member'],dts['member'],cond,dts['member'],dts['member']))
        	    	else:
        	        	total_count= frappe.db.sql("select count(*) from (select name,church_name,phone_no,email_id from tabChurches %s union select name,church_group,contact_phone_no,contact_email_id from `tabGroup Churches` %s union select name,zone_name,contact_phone_no,contact_email_id from `tabZones`  %s union select name,region_name,contact_phone_no,contact_email_id from `tabRegions` %s)x "%(cond,cond,cond,cond))
    		 	if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
					dts['page_no']=1
					start_index=0
    			else:   
					start_index=(cint(dts['page_no'])-1)*20
    			end_index =start_index+20	
    			if total_count and (total_count[0][0]<=end_index):
					end_index=total_count[0][0] 
    			result['total_count']=total_count[0][0]
    			result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'
    			if 'member' in dts:
    				result['records']=frappe.db.sql("select name as id , 'Churches' as type,church_name as name,phone_no as contact_phone_no,email_id as contact_email_id from tabChurches %s and (name like '%%%s%%' or church_name like '%%%s%%' ) union select name as id , 'Group Churches' as type,church_group as name,contact_phone_no,contact_email_id from `tabGroup Churches` %s and (name like '%%%s%%' or church_group like '%%%s%%' ) union select name as id , 'Zones' as type,zone_name as name,contact_phone_no,contact_email_id from `tabZones`  %s and (name like '%%%s%%' or zone_name like '%%%s%%' ) union select name as id , 'Regions' as type,region_name as name,contact_phone_no,contact_email_id from `tabRegions` %s and (name like '%%%s%%' or region_name like '%%%s%%' ) order by type,id limit %s,20"%(cond,dts['member'],dts['member'],cond,dts['member'],dts['member'],cond,dts['member'],dts['member'],cond,dts['member'],dts['member'],cint(start_index)),as_dict=True)
                		return result
                	result['records']=frappe.db.sql("select name as id , 'Churches' as type,church_name as name,phone_no as contact_phone_no,email_id as contact_email_id from tabChurches %s union select name as id , 'Group Churches' as type,church_group as name,contact_phone_no,contact_email_id from `tabGroup Churches` %s union select name as id , 'Zones' as type,zone_name as name,contact_phone_no,contact_email_id from `tabZones`  %s union select name as id , 'Regions' as type,region_name as name,contact_phone_no,contact_email_id from `tabRegions` %s order by type,id limit %s,20"%(cond,cond,cond,cond,cint(start_index)),as_dict=True)
                	return result
        else:
        	if 'member' in dts:
        	    cond+=" and member_name like '%%%s%%'"%(dts['member'])
        	#frappe.errprint(cond)
        	total_count= frappe.db.sql("select count(name) from tabMember %s "%(cond))
    		if (('page_no' not in dts) or cint(dts['page_no'])<=1): 
				dts['page_no']=1
				start_index=0
    		else:   
				start_index=(cint(dts['page_no'])-1)*20
    		end_index =start_index+20
    		if total_count and (total_count[0][0]<=end_index):
				end_index=total_count[0][0] 
    		result['total_count']=total_count[0][0]
    		result['paging_message']=cstr(cint(start_index)+1) + '-' + cstr(end_index) + ' of ' + cstr(total_count[0][0]) + ' items'           	  
        	result['records']=frappe.db.sql("select a.name as id, 'Members' as type, a.member_name as name, a.phone_1 as contact_phone_no,a.email_id as contact_email_id from tabMember a %s order by a.name limit %s,20 "%(cond,cint(start_index)),as_dict=True)
        	return result


@frappe.whitelist(allow_guest=True)
def file_upload(data):
        dts=json.loads(data)
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
    	if dts['tbl']=='First Timer':
             frappe.db.sql("update `tabFirst Timer` set image=%s where name=%s",(filedata.file_url,dts['name']))
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
	qr1="SELECT name,title, school_status, short_bio,filled_with_holy_ghost, member_name, surname, date_of_birth, phone_1, phone_2, email_id, email_id2, address, office_address, office_landmark, employment_status, industry_segment, yearly_income, experience_years, core_competeance, educational_qualification, NULL AS `password`, image, marital_info, cell, cell_name, senior_cell, senior_cell_name, pcf, pcf_name, church, church_name, church_group, group_church_name, zone, zone_name, region, region_name, member_designation, age_group, baptisum_status, baptism_when, sex, school_status, filled_with_holy_ghost, is_new_born, is_eligibale_for_follow_up, date_of_join, yokoo_id,baptism_where,home_address,user_id,lat,lon,lon1,lat1 from  tabMember where name='"+dts['name']+"'"
	#return qr1
        res=frappe.db.sql(qr1,as_dict=1)
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
        qr1="select m.name,m.member_name,m.surname as last_name,m.home_address,m.office_landmark,m.date_of_birth,m.short_bio,m.phone_1,m.phone_2,m.email_id,m.email_id2,m.address,m.office_address,m.employment_status,m.industry_segment,m.yearly_income,m.experience_years,m.core_competeance,m.educational_qualification,null AS `password`,m.image,m.marital_info,m.member_designation,m.cell,m.cell_name,m.senior_cell,m.senior_cell_name,m.pcf,m.pcf_name,m.church,m.church_name,m.church_group,m.group_church_name,m.zone,m.zone_name,m.region,m.region_name,m.office_landmark,m.baptism_where,m.title,m.home_address,m.baptism_when,m.age_group,m.baptisum_status,m.sex,m.school_status,m.filled_with_holy_ghost,m.is_new_born,m.is_eligibale_for_follow_up,m.date_of_join,m.yokoo_id from tabMember m,tabUser u where m.email_id=u.name and u.name='"+dts['username']+"'"
        res=frappe.db.sql(qr1,as_dict=1)
        return res

@frappe.whitelist(allow_guest=True)
def update_my_profile(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
	#print dts
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
	obj=frappe.get_doc('Member',dts['name'])
	obj.yearly_income=dts['yearly_income']
	obj.office_address=dts['office_address']
	if 'image' in dts:
		obj.image=dts['image']
	obj.industry_segment=dts['industry_segment']
	obj.employment_status=dts['employment_status']
	obj.address=dts['home_address']
	obj.date_of_birth=dts['date_of_birth']
	obj.educational_qualification=dts['educational_qualification']
	obj.core_competeance=dts['core_competeance']
	obj.member_name=dts['member_name']
	obj.email_id2=dts['email_id2']
	obj.phone_2=dts['phone_2']
	obj.marital_info=dts['marital_info']
	obj.experience_years=dts['experience_years']
	obj.phone_1=dts['phone_1']
	obj.phone_2=dts['phone_2']
	obj.office_landmark=dts['office_landmark']
	obj.baptism_where=dts['baptism_where']
	obj.title=dts['title']
	obj.home_address=dts['home_address']
	obj.baptism_when=dts['baptism_when']
	obj.age_group=dts['age_group']
	obj.baptisum_status=dts['baptisum_status']
	obj.sex=dts['sex']
	obj.school_status=dts['school_status']
	obj.filled_with_holy_ghost=dts['filled_with_holy_ghost']
	obj.is_new_born=dts['is_new_born']
	obj.is_eligibale_for_follow_up=dts['is_eligibale_for_follow_up']
	obj.date_of_join=dts['date_of_join']
	obj.yokoo_id=dts['yokoo_id']
	obj.surname=dts['last_name']
	if 'short_bio' in dts:
		obj.short_bio=dts['short_bio']
	obj.save(ignore_permissions=True)
	obj1=frappe.get_doc('User',dts['username'])
        obj1.new_password=dts['password']
        obj1.last_name=dts['last_name']
        obj1.first_name=dts['member_name']
	#print obj1
        obj1.save(ignore_permissions=True)
        return "Your profile updated successfully"


@frappe.whitelist(allow_guest=True)
def get_search_masters(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
        fields={
            "Churches":"name,church_name",
            "Group Churches":"name,church_group",
            "Zones":"name,zone_name",
            "Regions":"name,region_name"
    	}
    	return frappe.db.sql("select %s from `tab%s` "%(fields[dts['tbl']],dts['tbl']))

@frappe.whitelist(allow_guest=True)
def get_group_details(data):
        dts=json.loads(data)
        qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
        valid=frappe.db.sql(qry)
        if not valid:
            return {
                "status":"401",
                "message":"User name or Password is incorrect"
            }
        fields={
            "Churches":"name,church_name",
            "Group Churches":"name,church_group",
            "Zones":"name,zone_name",
            "Regions":"name,region_name"
    	}
    	return frappe.db.sql("select %s from `tab%s` "%(fields[dts['tbl']],dts['tbl']))


@frappe.whitelist(allow_guest=True)
def send_notification_member_absent():
	#frappe.errprint("In send_notification_member_absent")
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
					#frappe.errprint(abs_member)
					if abs_member[2]>=3:
						memeber_list[abs_member[0]]=abs_member[1]
						# frappe.errprint(memeber_list)
			cell_leader=frappe.db.sql("""select a.name,a.first_name ,dv.defvalue,dv.defkey from tabUser a,tabUserRole ur,tabDefaultValue dv where a.name=ur.parent and a.name=dv.parent
				and (ur.role='Cell Leader' or ur.role='Senior Cell Leader') and (dv.defkey='Cells' or dv.defkey='Senior Cells') and (dv.defvalue='%s' or dv.defvalue='%s')"""%(sc[0],cc[0]),as_list=1)
			if memeber_list and cell_leader:
				for leaders in cell_leader :
					msg="""Hello '%s',\n\n Following members have not attended last three meetings \n\n %s \n\n Regards,\n\n Love world Synergy"""%(leaders[1]," \n".join([" \n \t\t\t\t\t\t Member Id : '%s'  Member Name : '%s'" % (k,v) for k,v in memeber_list.iteritems()]) )
					abc = [" \n Member Id : '%s'  Member Name : '%s'" % (k,v) for k,v in memeber_list.iteritems()]
					#frappe.errprint(msg)
					phone = frappe.db.sql("select phone_1 from `tabMember` where email_id='%s'"%(leaders[0]))
					notify = frappe.db.sql("""select value from `tabSingles` where doctype='Notification Settings' and field='member_is_absent_in_meeting'""",as_list=1)
					if "Email" in notify[0][0]:
						#frappe.errprint("absent in 3 meetings")
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
							res1 = gcm.json_request(registration_ids=res1[0], data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)
	
	return "sent emails"


@frappe.whitelist(allow_guest=True)
def send_notification_cell_meeting_not_hold():
	#frappe.errprint("In send_notification_cell_meeting_not_hold")
	senior_cell_list=frappe.db.sql("select distinct(senior_cell) from tabCells",as_list=1)
	for sc in senior_cell_list:
		res=frappe.db.sql("select name,senior_cell,pcf from tabCells where name not in (select distinct(cell) \
			from `tabAttendance Record` where attendance_type='Meeting attendance' and date(creation) between \
			DATE_SUB(NOW(), INTERVAL 7 DAY)  AND DATE_SUB(NOW(), INTERVAL 15 DAY)) and senior_cell='%s'"%(sc[0]),as_list=1)
		#frappe.errprint(res)
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
def message_braudcast_details(data):
    """
    this will return recipents details
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
    if 'tbl' in dts and dts['tbl']=='FT':
       match_conditions,cond=get_match_conditions('First Timer',dts['username'])
       qry="select name,ftv_name ,email_id,phone_1 from `tabFirst Timer` WHERE '1'=1 %s"%(cond)
    elif 'tbl' in dts and dts['tbl']=='Member':
       match_conditions,cond=get_match_conditions('Member',dts['username'])
       qry="select name,member_name as ftv_name,email_id,phone_1 from tabMember where email_id not IN ( SELECT DISTINCT parent FROM tabUserRole WHERE role IN ('PCF Leader','Cell Leader', 'Senior Cell Leader','Church Pastor','Group Church Pastor','Regional Pastor','Zonal Pastor')) %s"%(cond)
    else:
    	match_conditions,cond=get_match_conditions('Member',dts['username'])
        qry="select name,member_name as ftv_name,email_id,phone_1 from tabMember where email_id in (select distinct parent from tabUserRole where role in ('PCF Leader','Cell Leader','Senior Cell Leader','Church Pastor','Group Church Pastor','Regional Pastor','Zonal Pastor')) %s"%(cond)
    print "qry----------------------"+qry
    res=frappe.db.sql(qry,as_dict=1)
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
    msg=''
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }   

    if 'sms' in dts:
    	from erpnext.setup.doctype.sms_settings.sms_settings import send_sms
    	rc_list=frappe.db.sql("select phone_1 from tabMember where phone_1 is not null and email_id in ('%s') limit 3" %(dts['recipents'].replace(",","','")),as_list=1)      
    	if rc_list:
    		send_sms([ x[0] for x in rc_list ], cstr(dts['message']))
    		msg+= "SMS "
    rc_list=dts['recipents'].split(',')
    if 'push' in dts:
        data={}
        data['Message']=dts['message']
        gcm = GCM('AIzaSyBIc4LYCnUU9wFV_pBoFHHzLoGm_xHl-5k')
        res=frappe.db.sql("select device_id from tabUser where name in ('%s')" % "','".join(map(str,rc_list)),as_list=1)
        if res:
                response = gcm.json_request(registration_ids=res[0], data=data,collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)
                if 'errors' in response:
                	return {
                		"status":"402",
                		"message": "The user is not registered for Push notification . Please login with user from mobile to generate Device ID"
                	 }
                msg+= "Push notification"
    if 'email' in dts:
        frappe.sendmail(recipients=dts['recipents'], sender='verve@lws.com', content=dts['message'], subject='Broadcast Message')
        msg+=" Email"
    return msg +" sent Successfully"


@frappe.whitelist(allow_guest=True)
def task_esclate():
	#frappe.errprint("in task_esclate")
	"""
	this will return recipents details
	"""
	#print "running task exclation"
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

@frappe.whitelist(allow_guest=True)
def get_gcm_key(data):
    """
    this will return gcm key details
    """
    dts=json.loads(data)
    qry="select user from __Auth where user='"+cstr(dts['username'])+"' and password=password('"+cstr(dts['userpass'])+"') "
    valid=frappe.db.sql(qry)
    msg=''
    if not valid:
        return {
                "status":"401",
                "message":"User name or Password is incorrect"
        }
    res=frappe.db.sql("select value as api_key from `tabSingles` where doctype='Notification Settings' and field = 'google_api_key'", as_dict=1)
    
    if res:
    	return res[0]
    else:
    	return {
                "status":"401",
                "message":"Please update gcm key in notification settings...!"
        }
        


