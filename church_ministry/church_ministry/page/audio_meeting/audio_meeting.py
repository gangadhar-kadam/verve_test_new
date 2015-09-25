from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.utils import cstr,now,add_days,nowdate


@frappe.whitelist()
def process(data):
	dts=[x for x in data[1:-1].split(',')]
	for item in dts:
		itm=item.replace('"','').strip()
		qry="select first_name,ifnull(last_name,'') from tabUser where name='"+itm+"'"
		result=frappe.db.sql(qry)
		import requests
		import xmltodict ,json
		req1 = requests.get('http://88.198.52.49:5080/openmeetings/services/UserService/getSession')
		#frappe.errprint(req1.text)
		frappe.errprint(req1.text.split('ax23:session_id>')[1][:-2])
		req2="http://88.198.52.49:5080/openmeetings/services/UserService/loginUser?SID="+req1.text.split('ax23:session_id>')[1][:-2]+"&username="+result[0][0].replace(' ','')+"&userpass="+result[0][0].replace(' ','')
		#req2="http://88.198.52.49:5080/openmeetings/services/UserService/loginUser?SID="+req1.text.split('ax23:session_id>')[1][:-2]+"&username=pcfleader1&userpass=pcfleader1"
		#frappe.errprint(req2)
		res2=requests.get(req2)
		frappe.errprint(res2.text)
		req3="http://88.198.52.49:5080/openmeetings/services/UserService/setUserObjectAndGenerateRoomHashByURLAndRecFlag?SID="+req1.text.split('ax23:session_id>')[1][:-2]+"&username="+result[0][0]+"&firstname="+result[0][0]+"&lastname="+result[0][1]+"&profilePictureUrl=http://www.fnordware.com/superpng/pnggrad16rgb.png&email=email.kadam@gmail.com&externalUserId=1&externalUserType=kadamgn&room_id=1&becomeModeratorAsInt=1&showAudioVideoTestAsInt=1&allowRecording=1"
		frappe.errprint(req3)
		res3=requests.get(req3)
		frappe.errprint(res3.text)
		hashid=res3.text.split('ns:return>')[1][:-2]
		url="http://88.198.52.49:5080/openmeetings/?secureHash="+hashid
		frappe.get_doc({
		"doctype": "ToDo",
		"description": url,
		"owner":itm
		}).insert(ignore_permissions=True)
		frappe.sendmail(recipients=itm+',gangadhar.k@indictranstech.com', content=url, subject='Audio meeting url')
	return "done"

@frappe.whitelist()
def get_users():
	res=frappe.db.sql("select a.name,CONCAT(ifnull(a.first_name,''),' ',ifnull(a.last_name,'')) as full_name from tabUser  a,tabUserRole r where a.name=r.parent and r.role in ('Regional Pastor','Zonal Pastor','Group Church Pastor','Church Pastor','Cell Leader','Senior Cell Leader','PCF Leader','Bible Study Class Teacher','System Manager') order by a.name" ,as_dict=1)	
	return res


@frappe.whitelist()
def invite_meeting(data):
	from church_ministry.church_ministry.page.open_office.open_office import process
	process(user_list)
	frappe.msgprint("invited members for meeting")
	return data
