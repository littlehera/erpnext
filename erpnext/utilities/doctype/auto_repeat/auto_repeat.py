# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, getdate

import datetime

class AutoRepeat(Document):
	def validate(self):
		self.validate_dates()
		self.validate_frequency_and_end_date()

		if not self.next_repeat_date:
			self.next_repeat_date = get_next_date(self.frequency, self.start_date)

	def validate_dates(self):
		if getdate(self.end_date) <= getdate(self.start_date):
			frappe.throw(_("End Date must not be before/same as the Start Date"))

	def validate_frequency_and_end_date(self):
		next_date = get_next_date(self.frequency, self.start_date)
		if getdate(self.end_date) < next_date:
			frappe.throw(_("Please match end date with the next frequency date"))

def make_auto_repeat_entry(date=None):
	date = date or today()
	for entry in get_auto_repeat_entries(date):
		if getdate(date) == getdate(entry.next_repeat_date):
			duplicate_entry(entry)
			next_date = get_next_date(entry.frequency, entry.next_repeat_date)
			update_repeat_date(entry.name, next_date)
			if getdate(date) == getdate(entry.end_date):
				set_status_completed(entry.name)

def get_auto_repeat_entries(date):
	return frappe.db.sql("""select * from `tabAuto Repeat` where status='Active' and next_repeat_date=%s""", date, as_dict=1)

def get_max_idx_from_parent(parent):
	return frappe.db.sql("""select max(idx) as last_idx from `tabAuto Repeat Item` where parent=%s""", parent, as_dict=1)

def get_next_date(frequency, date):
	if frequency == "Daily":
		return getdate(date) + datetime.timedelta(days=1)
	elif frequency == "Weekly":
		return getdate(date) + datetime.timedelta(days=7)
	elif frequency == "Monthly":
		return getdate(date) + datetime.timedelta(days=30)

def duplicate_entry(args):
	doc = frappe.get_doc(args.reference_doctype, args.reference_document)
	new_doc = frappe.copy_doc(doc)
	new_doc.insert(ignore_permissions=True)

	last_entry = get_max_idx_from_parent(args.name)[0]
	idx = (last_entry.last_idx or 0)

	item = frappe.get_doc({
		"idx": idx + 1,
		"doctype": "Auto Repeat Item",
		"parent": args.name,
		"parenttype": "Auto Repeat",
		"parentfield": "auto_repeat_item",
		"reference_doctype": args.reference_doctype,
		"reference_document": new_doc.name
	})

	item.insert()

def update_repeat_date(doc_name, next_date):
	frappe.db.set_value("Auto Repeat", doc_name, "next_repeat_date", next_date)

def set_status_completed(doc_name):
	frappe.db.set_value("Auto Repeat", doc_name, "status", "Completed")

@frappe.whitelist()
def parent_reference_document_query(doctype):
	return frappe.db.sql("""select reference_document from `tabAuto Repeat Item` where reference_doctype=%s""", (doctype), as_dict=1)