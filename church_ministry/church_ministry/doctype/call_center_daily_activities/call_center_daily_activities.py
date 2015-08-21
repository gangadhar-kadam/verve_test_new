# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_add, cint, today
from frappe import throw, _, msgprint

class CallCenterDailyActivities(Document):
	def validate(self):
		for d in self.get('daily_activities'):
			if d.date and d.date >today():
				frappe.throw(_('Date should not be future date. {0} is future date').format(d.date))
				
