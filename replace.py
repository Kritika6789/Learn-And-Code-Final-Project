import re
import os

file_path = "client/screens/admin.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

replacements = [
    ("Manage Employees", "Manage Resources"),
    ("manage_employees", "manage_resources"),
    ("MANAGE EMPLOYEES", "MANAGE RESOURCES"),
    ("View All Employees", "View All Resources"),
    ("Update Employee", "Update Resource"),
    ("Deactivate Employee", "Deactivate Resource"),
    ("Manage Employee Skills", "Manage Resource Skills"),
    ("view_all_employees", "view_all_resources"),
    ("update_employee", "update_resource"),
    ("deactivate_employee", "deactivate_resource"),
    ("assign_manager", "assign_role"),
    ("Assign Manager", "Assign Role"),
    ("ASSIGN MANAGER", "ASSIGN ROLE"),
    ("Employee User ID", "User ID"),
    ("Manager User ID", "Role ID"),
    ("api.assign_manager(emp_id, manager_id)", "api.assign_role(emp_id, manager_id)"),
    ("api.get_employees()", "api.get_resources()"),
    ("api.create_employee", "api.create_resource"),
    ("add_employee", "add_resource"),
    ("ADD EMPLOYEE", "ADD RESOURCE"),
    ("Employee '", "Resource '"),
    ("No employees found.", "No resources found."),
    ("Total: {len(employees)}", "Total: {len(resources)}"),
    ("employees =", "resources ="),
    ("employees)", "resources)"),
    ("filtered = [e for e in employees", "filtered = [e for e in resources"),
    ("Enter Employee ID", "Enter Resource ID"),
    ("/admin/employees/", "/admin/resources/"),
]

for old, new in replacements:
    text = text.replace(old, new)

# Special regex for variable names
text = re.sub(r'\bemp\b', 'res', text)
text = re.sub(r'\bemp_id\b', 'res_id', text)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Replaced successfully")
