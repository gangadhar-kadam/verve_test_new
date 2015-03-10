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
	"Region Master": {
		"validate": "church_ministry.church_ministry.doctype.region_master.region_master.validate_duplicate"		
	},
	"Zone Master": {
		"validate": "church_ministry.church_ministry.doctype.zone_master.zone_master.validate_duplicate"		
	},
	"Church Group Master": {
		"validate": "church_ministry.church_ministry.doctype.church_group_master.church_group_master.validate_duplicate"		
	},
	"Church Master": {
		"validate": "church_ministry.church_ministry.doctype.church_master.church_master.validate_duplicate"		
	},
	"PCF Master": {
		"validate": "church_ministry.church_ministry.doctype.pcf_master.pcf_master.validate_duplicate"		
	},
	"Senior Cell Master": {
		"validate": "church_ministry.church_ministry.doctype.senior_cell_master.senior_cell_master.validate_duplicate"		
	},
	"Cell Master": {
		"validate": "church_ministry.church_ministry.doctype.cell_master.cell_master.validate_duplicate"		
	},
	"Foundation School Exam Master": {
		"validate": "church_ministry.church_ministry.doctype.foundation_school_exam_master.foundation_school_exam_master.validate_duplicate"		
	},
	"Grade Master": {
		"validate": "church_ministry.church_ministry.doctype.grade_master.grade_master.validate_duplicate"		
	},
	"Member": {
		"validate": "church_ministry.church_ministry.doctype.member.member.validate_birth"		
	},
	"First Time Visitor": {
		"validate": "church_ministry.church_ministry.doctype.first_time_visitor.first_time_visitor.validate_birth"		
	},
	"Foundation School Exam": {
		"validate": "church_ministry.church_ministry.doctype.foundation_school_exam.foundation_school_exam.validate_duplicate",
		"on_submit": "church_ministry.church_ministry.doctype.foundation_school_exam.foundation_school_exam.update_attendance",		
	},
	"Cell Meeting Invitation": {
		"validate": "church_ministry.church_ministry.doctype.cell_meeting_invitation.cell_meeting_invitation.validate_duplicate"		
	},
	"First Time Visitor": {
		"validate": "church_ministry.church_ministry.doctype.first_time_visitor.first_time_visitor.validate_duplicate"		
	}
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"church_ministry.tasks.all"
# 	],
# 	"daily": [
# 		"church_ministry.tasks.daily"
# 	],
# 	"hourly": [
# 		"church_ministry.tasks.hourly"
# 	],
# 	"weekly": [
# 		"church_ministry.tasks.weekly"
# 	]
# 	"monthly": [
# 		"church_ministry.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "church_ministry.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "church_ministry.event.get_events"
# }

