from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type":"doctype",
					"name": "First Time Visitor",
					"description": _("First Time Visitor Database")
				},			
				{
					"type":"doctype",
					"name": "Member",
					"description": _("Member Database")
				},				
				
				{
					"type":"doctype",
					"name": "Cell Meeting Invitation",
					"description": _("Cell Meeting Invitation Database")
				},
				{
					"type":"doctype",
					"name": "Cell Meeting Attendance",
					"description": _("Cell Meeting Attendance Database")
				},
				{
					"type":"doctype",
					"name": "Partnership Arm Record",
					"description": _("Partnership Arm Record Database")
				},								

				{
					"type":"doctype",
					"name": "Foundation School Exam",
					"description": _("Foundation School Exam Attendance/Results")
				},
				{
					"type":"doctype",
					"name": "Event",
					"description": _("Event")
				},
				{
					"type":"doctype",
					"name": "Event Attendance",
					"description": _("Event Attendance Database")
				},
			]
		},
		{
			"label": _("Page"),
			"icon": "icon-star",
			"items": [
				{
					"type": "page",
					"name": "assign-for-followup",
					"label": _("Assign For Followup"),
					"icon": "icon-bar-chart",
					"description": _("Assign For Followup")
				},
				{
					"type": "page",
					"name": "approve-ftv-to-membe",
					"label": _("Eligible FTV's to Member"),
					"icon": "icon-bar-chart",
					"description": _("Eligible FTV's to Member")
				},
				{
					"type": "page",
					"name": "convert-ftv-to-membe",
					"label": _("Convert FTV to Member"),
					"icon": "icon-bar-chart",
					"description": _("Convert FTV to Member")
				},
				{
					"type": "page",
					"name": "dashboard",
					"label": _("Dashboard"),
					"icon": "icon-bar-chart",
					"description": _("Dashboard")
				},			
			]
		},
		{
			"label": _("Setup"),
			"icon": "icon-star",
			"items": [
				{
					"type":"doctype",
					"name": "Region Master",
					"description": _("Region Master")
				},
				{
					"type":"doctype",
					"name": "Zone Master",
					"description": _("Zone Master")
				},
				{
					"type":"doctype",
					"name": "Church Group Master",
					"description": _("Church Group Master")
				},
				{
					"type":"doctype",
					"name": "Church Master",
					"description": _("Church Master")
				},				
				{
					"type":"doctype",
					"name": "PCF Master",
					"description": _("PCF Master")
				},
				{
					"type":"doctype",
					"name": "Senior Cell Master",
					"description": _("Senior Cell Master")
				},
				{
					"type":"doctype",
					"name": "Cell Master",
					"description": _("Cel Master")
				},				
				{
					"type":"doctype",
					"name": "Foundation School Exam Master",
					"description": _("Foundation School Exam Master")
				},							
				{
					"type":"doctype",
					"name": "Grade Master",
					"description": _("Foundation School Exam Grade Master")
				},				
			]
		},
	]

