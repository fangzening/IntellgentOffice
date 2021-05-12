import datetime
import os
from Smart_Office.settings import BASE_DIR
from office_app.models import Vendors, Notification


def parse_vendor_data(filename):
    file_path = BASE_DIR + filename + '.txt'
    python_file_path = BASE_DIR + filename + '.py'

    with open(file_path, "r") as file:
        model_list = []
        appendedString = 'data = '

        with open(python_file_path, 'w') as file2:
            file2.write(appendedString + file.read())

        try:
            from it_app.static.uploads.processing import result

            temp = Vendors()
            for data in result.data:
                for key in data:
                    temp.parse_vendor_data(key, data[key])
                model_list.append(temp)
                temp = Vendors()
        except:
            print('There was an error importing the file.')
    try:
        if open(file_path):
            os.remove(file_path)
        if open(python_file_path):
            os.remove(python_file_path)
    except:
        print('One of these files does not exist.')

    Vendors.objects.bulk_update(model_list)


def change_user_password(user, is_approved, raw_password):
    notification = Notification(employee=user, is_unread=True, created_on=datetime.today(),
                                module='Pass-request')
    if is_approved:
        user.set_password(raw_password)

        notification.title = "Password Change"
        notification.body = "Your password has been successfully changed!"
        notification.link = ""
        notification.save()
    else:
        notification.title = "Password Change Denied"
        notification.body = "You are not approved for a password change. Please try contacting an administrator if you have questions."
        notification.link = ""
        notification.save()
