import xlsxwriter

from Smart_Office import settings
# data = [['HCP S11 CNTRL,1 CPU,64GB,2x256GB SSD,6 P', '', 2, ''], ['Asm,Cont,RAID,4P CNC,12G,Ga-LX3,SBB', '', 1, ''],
#        ['Asm,JBOD,SAS,4P,6G,Xena', '', 1, ''], ['Asm,Cont,RAID,4P SAS,12G,Ga-LX3,SBB', '', 1, ''],
#        ['Asm,EBOD, SAS, 12Gb, 3Port', '', 1, ''], ['Asm,Cont,RAID,4P CNC,12G,Ga-NX3,SBB', '', 4, ''],
#        ['FRU,SAS,4P,1.3GHz,Gallium,HP', '', 1, ''], ['Asm,JBOD,SAS,6Gb,Gallium', '', 1, ''],
#        ['EBOD,COBRA 106,BULK', '', 1, '']]

# Each item in list is:
# [itemDesc, assetNum, qty, cost_center, profit_center]
# item is '' (empty string) if it is not found

# Create a file called asset.xlsx, used for creating the asset tags. Need to send the file along with the notification.

def createAssetFile(assetData, GRFormID, user):
    file_path = settings.MEDIA_ROOT + "\\goods_recieved\\asset_files\\gr_spreadsheet_" + str(GRFormID) + '.xlsx'
    file_name = 'gr_spreadsheet_' + str(GRFormID) + '.xlsx'
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    for row_num, columns in enumerate(assetData):
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num, col_num, cell_data)

    workbook.close()
    try:
        from office_app.services import EmailHandler
        EmailHandler.send_excel_attachment_email(user, file_path, file_name)
    except ImportError:
        raise ImportError('There was an issue importing the EmailHandler.')

# How to call the file:
# createAssetFile(data, 105)
