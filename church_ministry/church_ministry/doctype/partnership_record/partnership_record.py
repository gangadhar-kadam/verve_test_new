# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class PartnershipRecord(Document):
	def validate(self):
		if self.giving_type=='Cheque':
			if (not self.instrument__no  or not self.instrument_date or  not self.bank_name) :
				frappe.throw(_(" 'Instrument No' , 'Instrument Date' and 'Bank Name' are mandatory for giving type 'Cheque' ..!"))


	def on_submit(self):
		if self.is_member==1:
			email=frappe.db.sql("select email_id,member_name from `tabMember` where name='%s'"%(self.member))
		else:
			email=frappe.db.sql("select email_id,ftv_name from `tabFirst Timer` where name='%s'"%(self.ftv))
		if email:
			msg="""Hello %s,<br> Thank you so much for your donation of amount '%s'. <br>Regards,<br>Verve"""%(email[0][1],self.amount)
			frappe.sendmail(recipients=email[0][0], sender='gangadhar.k@indictranstech.com', content=msg, subject='Partnership Record')
