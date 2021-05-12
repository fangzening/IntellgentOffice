import csv

from office_app.models import Vendors


'''
    update_vendor_changes
    This function checks to see if there have been any changes in SAP's vendor table.
    If yes, then the changes will be made in SO.
    :param temp_vendor: the temporary placeholder of the vendor from all_vendors
    :param current_vendor: the current vendor from the file being checked
    :returns status: a dict object that stores the status of what has happened
'''
def update_vendor_changes(temp_vendor, current_vendor, status_tracker=None):
    status = {'status': 'incomplete', 'action': 'unchanged'}
    # CHECK NAME
    if temp_vendor.vendorName != current_vendor.vendorName:
        temp_vendor.vendorName = current_vendor.vendorName
        status['action'] = 'changed'
    # CHECK COMPANY CODE
    if temp_vendor.companyCode != current_vendor.companyCode:
        temp_vendor.companyCode = current_vendor.companyCode
        status['action'] = 'changed'
    # CHECK CONTACT
    if temp_vendor.supplierContact != current_vendor.supplierContact:
        temp_vendor.supplierContact = current_vendor.supplierContact
        status['action'] = 'changed'
    # CHECK ADDRESS
    if temp_vendor.supplierAddress != current_vendor.supplierAddress:
        temp_vendor.supplierAddress = current_vendor.supplierAddress
        status['action'] = 'changed'
    # CHECK TELEPHONE
    if temp_vendor.supplierTelephone != current_vendor.supplierTelephone:
        temp_vendor.supplierTelephone = current_vendor.supplierTelephone
        status['action'] = 'changed'
    # CHECK COUNTRY
    if temp_vendor.vendorCountry != current_vendor.vendorCountry:
        temp_vendor.vendorCountry = current_vendor.vendorCountry
        status['action'] = 'changed'
    status['status'] = 'complete'
    status_tracker = status
    return status_tracker


'''
    update_vendor_list
    This function will update the current list of vendors in our database.
    :returns status: a dict object that stores the status of what has happened
'''
def update_vendor_list():
    status_tracker = {'status': 'starting'}
    vendor_count1 = 0
    vendor_count2 = 0

    all_vendors = Vendors.objects.all()
    vendor_codes = []

    for vendor in all_vendors:
        vendor_codes.append(vendor.vendorCode)

    # PREP FOR CSV FILE
    column_headers = ['vendor_code', 'vendor_name', 'comp_code', 'contact', 'address', 'telephone', 'country']
    temp = Vendors()
    current_vendor = Vendors()
    changes = 0

    status_tracker['status'] = 'opening_file'
    with open('Updated_Vendor_List.csv', 'r') as file:
        status_tracker['status'] = 'pending'
        rows = csv.DictReader(file, column_headers)
        for row in rows:
            vendor_code = row['vendor_code']
            if vendor_code in vendor_codes:
                vendor_count1 += 1

                current_vendor = Vendors()
                temp = Vendors.objects.filter(vendorCode=vendor_code).first()

                current_vendor.vendorCode = row['vendor_code']
                current_vendor.vendorName = row['vendor_name']
                current_vendor.companyCode = row['comp_code']
                current_vendor.supplierContact = row['contact']
                current_vendor.supplierAddress = row['address']
                current_vendor.supplierTelephone = row['telephone']
                current_vendor.vendorCountry = row['country']
                status_tracker = update_vendor_changes(temp, current_vendor, status_tracker)
                # SAVE CHANGES AFTER CHECKING TEMP AGAINST CURRENT VENDOR INFO
                if status_tracker['action'] == 'changed':
                    temp.save()
            else:
                current_vendor = Vendors()

                current_vendor.vendorCode = row['vendor_code']
                current_vendor.vendorName = row['vendor_name']
                current_vendor.companyCode = row['comp_code']
                current_vendor.supplierContact = row['contact']
                current_vendor.supplierAddress = row['address']
                current_vendor.supplierTelephone = row['telephone']
                current_vendor.vendorCountry = row['country']
                current_vendor.save()
                vendor_count2 += 1

    status_tracker['status'] = 'completed'
    print(f"We have {vendor_count1} of the vendors in our db.")
    print(f"We are missing about {vendor_count2} of the vendors from our db.")
    return status_tracker
