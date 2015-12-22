import frappe
import requests
import json
from frappe.utils import cstr
from frappe.utils.data import getdate

@frappe.whitelist()
def get_children(ctype,node=None):
	args = frappe.local.form_dict
	ctype = args['ctype']
	tblmapper={
	"Regions":"Zones",
	"Zones":"Group Churches",
	"Group Churches":"Churches",
	"Churches":"PCFs",
	"PCFs":"Senior Cells",
	"Senior Cells":"Cells",
	"Cells":"name"
	}
	columnmapper={
	"Zones":"region",
	"Group Churches":"zone",
	"Churches":"church_group",
	"PCFs":"church",
	"Senior Cells":"pcf",
	"Cells":"senior_cell"
	}
	tab,name='',''
	if ('parent' in args) and (args['parent']!='Member Tree') :
		tab,name=args['parent'].split(':-')[0],args['parent'].split('-')[1]
	if ('Member Tree'  in args.values()) or ('parent' not in args):
		acc	= frappe.db.sql(""" select CONCAT ('Regions:-',name) as value, 1 as expandable from `tabRegions` """, as_dict=1)
	elif tab=='Senior Cells':
		acc	= frappe.db.sql(""" select CONCAT ('Cells:-',name) as value, 0 as expandable from `tabCells` where senior_cell='%s' """%(name), as_dict=1)
	else:
	    acc	= frappe.db.sql(""" select CONCAT ('%s:-',name) as value, 1 as expandable from `tab%s` where %s='%s' """%(tblmapper[tab],tblmapper[tab],columnmapper[tblmapper[tab]],name), as_dict=1)	
	return acc


