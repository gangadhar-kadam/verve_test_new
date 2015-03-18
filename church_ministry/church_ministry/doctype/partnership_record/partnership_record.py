# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PartnershipRecord(Document):
	# pass

	def on_submit(self):
		if self.is_member==1:
			email=frappe.db.sql("select email_id,member_name from `tabMember` where name='%s'"%(self.member))
		else:
			email=frappe.db.sql("select email_id,ftv_name from `tabFirst Timer` where name='%s'"%(self.ftv))
		msg="""Hello %s,<br> Thank you so much for your donation of amount '%s'. <br>Regards,<br>Varve"""%(email[0][1],self.amount)
		frappe.sendmail(recipients=email[0][0], sender='gangadhar.k@indictranstech.com', content=msg, subject='Partnership Record')
