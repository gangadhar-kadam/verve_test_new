app_name = "church_ministry"
app_title = "Church Ministry"
app_publisher = "New Indictrans Technologies Pvt. Ltd."
app_description = "This app id for manage church ministry"
app_icon = "icon-book"
app_color = "#589494"
app_email = "gangadhar.k@indictranstech.com"
app_url = "info@indictranstech.com"
app_version = "0.0.1"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/church_ministry/css/church_ministry.css"
#app_include_js = "/assets/js/chart.js"

# include js, css files in header of web template
# web_include_css = "/assets/church_ministry/css/church_ministry.css"
# web_include_js = "/assets/church_ministry/js/church_ministry.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "church_ministry.install.before_install"
# after_install = "church_ministry.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "church_ministry.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events


fixtures = ["Custom Field"]

doc_events = {
	"Regions": {
		"validate": "church_ministry.church_ministry.doctype.regions.regions.validate_duplicate"		
	},
	"Zones": {
		"validate": "church_ministry.church_ministry.doctype.zones.zones.validate_duplicate"		
	},
	"Group Churches": {
		"validate": "church_ministry.church_ministry.doctype.group_churches.group_churches.validate_duplicate"		
	},
	"Churches": {
		"validate": "church_ministry.church_ministry.doctype.churches.churches.validate_duplicate"		
	},
	"PCFs": {
		"validate": "church_ministry.church_ministry.doctype.pcfs.pcfs.validate_duplicate"		
	},
	"Senior Cells": {
		"validate": "church_ministry.church_ministry.doctype.senior_cells.senior_cells.validate_duplicate"		
	},
	"Cells": {
		"validate": "church_ministry.church_ministry.doctype.cells.cells.validate_duplicate"		
	},
	"Foundation School Exams": {
		"validate": "church_ministry.church_ministry.doctype.foundation_school_exams.foundation_school_exams.validate_duplicate"		
	},
	"Foundation School Grades": {
		"validate": "church_ministry.church_ministry.doctype.foundation_school_grades.foundation_school_grades.validate_duplicate"		
	},
	"Member": {
		"validate": "church_ministry.church_ministry.doctype.member.member.validate_birth"		
	},
	"First Timer": {
		"validate": "church_ministry.church_ministry.doctype.first_timer.first_timer.validate_birth"		
	},
	"Foundation School Exam": {
		"validate": "church_ministry.church_ministry.doctype.foundation_school_exam.foundation_school_exam.validate_duplicate",
		"on_submit": "church_ministry.church_ministry.doctype.foundation_school_exam.foundation_school_exam.update_attendance",		
	},
	"Attendance Record": {
		"validate": "church_ministry.church_ministry.doctype.attendance_record.attendance_record.validate_duplicate"		
	},
	"Foundation School Attendance": {
		"validate": "church_ministry.church_ministry.doctype.foundation_school_attendance.foundation_school_attendance.validate_duplicate",
		"on_submit": "church_ministry.church_ministry.doctype.foundation_school_attendance.foundation_school_attendance.update_attendance",		
	},
}


#Scheduled Tasks
#---------------

scheduler_events = {
	"all": [
		"church_ministry.church_ministry.doctype.member.member.task_esclate",
		"church_ministry.church_ministry.doctype.member.member.send_notification_member_absent",
		"church_ministry.church_ministry.doctype.member.member.send_notification_cell_meeting_not_hold"
	]
	# "daily": [
	# 	"church_ministry.church_ministry.doctype.member.member.task_esclate",
	# 	"church_ministry.church_ministry.doctype.member.member.send_notification_member_absent",
	# 	"church_ministry.church_ministry.doctype.member.member.send_notification_cell_meeting_not_hold",

	#  ]#,
	# "hourly": [
	# 	"church_ministry.tasks.hourly"
	# ],
	# "weekly": [
	# 	"church_ministry.tasks.weekly"
	# ]
	# "monthly": [
	# 	"church_ministry.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "church_ministry.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "church_ministry.event.get_events"
# }

