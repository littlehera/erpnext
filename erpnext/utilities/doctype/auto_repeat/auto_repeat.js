// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Auto Repeat", {
	start_date: function(frm) {

		var frequency = frm.doc.frequency;
		var startDate = frm.doc.start_date;

		if(frequency && startDate) {

			if(frequency === "Daily") {
				frm.set_value("end_date", frappe.datetime.add_days(startDate, 1));
			} else if(frequency === "Weekly") {
				frm.set_value("end_date", frappe.datetime.add_days(startDate, 7));
			} else if(frequency === "Monthly") {
				frm.set_value("end_date", frappe.datetime.add_days(startDate, 30));
			}

		}

	},
	reference_doctype: function(frm) {

		frappe.call({
			method: "erpnext.utilities.doctype.auto_repeat.auto_repeat.parent_reference_document_query",
			args: {
				"doctype": frm.doc.reference_doctype
			},
			callback: function(r) {

				var exclude = r.message.map((val) => {
					return val.reference_document;
				});

				frm.set_query("reference_document", function() {
					return {
						filters: {
							"name": ["not in", exclude]
						}
					}
				});

			}
		});

	}
});

frappe.ui.form.on("Auto Repeat Item", "auto_repeat_item_add", function(frm, cdt, cdn) {
	var item = frappe.get_doc(cdt, cdn);
		item.reference_doctype = frm.doc.reference_doctype;
});