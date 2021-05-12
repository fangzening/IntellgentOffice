# This file contains functions that pull and push to SAP, Always connect to PRD902 use basic data from AFEPRODDATA.py
# File)
import datetime
import sys
import traceback

from SAP import SAPWebService
from SAP import AFETESTDATA
from SAP import AFEPRODDATA

from office_app.models import SAPResponse

wsdl = 'http://k2d.na.foxconn.com/ws/djangosapconn.asmx?wsdl'


# get vendor Code and write to a file
# result file is in string format and utf-8 encoding
def getVendorCode():
    PrdData = {
        'strServer': AFEPRODDATA.server,
        'strName': AFEPRODDATA.uName,
        'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
        'strVendorName': '*',
        'strVendorCode': '*',
        'strCompanyCode': 'US11',
    }
    vendorCode = SAPWebService.vendorCode(wsdl, PrdData)
    f = open('../../../../Users/jacob.lattergrass/Downloads/result.txt', 'w', encoding='utf-8')
    f.writelines(str(vendorCode))
    f.close()


# trigger SAP to upload AP info and print the response
# SAP returns: DocNo, Posting Date, and SAP message
def createAP(formID, formType):
    PrdData = {
        'strServer': AFEPRODDATA.server,
        'strName': AFEPRODDATA.uName,
        'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
        'strID': formID,
        'strFormType': formType
    }
    response = SAPWebService.createAP(wsdl, PrdData)

    SAPResponse(transactionID=response['SAPDocNo'],
                sapMessage=response['SAPMessage'],
                date=response['SAPPostDate'],
                form=formType + "-" + str(formID),
                ).save()

    print("response after saving: " + str(response))
    return response


# this is used to check if the current invoice no exists in the SAP system to prevent from user uploading duplicate invoice
def check_invoice_SAP(invoice_id,companycode):
    # conn = Connection(user='DONGJUNY', passwd='SSY3.1415926', ashost='10.18.222.152', sysnr='00', client='802')
    # print(conn)
    Data = {
        'strServer': AFEPRODDATA.server,
        'strName': AFEPRODDATA.uName,
        'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
        'strCompanyCode': companycode,
        'strInvoiceID': invoice_id,
        'strCreateDate':datetime.datetime.now()
    }
    print(datetime.datetime.now())
    try:
        response = SAPWebService.checkinvoice(wsdl, Data)
    except:
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        response = None
    return True if response=="No duplicate was found" else False# True= being unique; False= beding duplicate



# Download PO items from SAP, SAP returns lots of stuff :) will update later
def downloadPO(poNumber, plantCode):
    PrdData = {
        'strServer': AFEPRODDATA.server,
        'strName': AFEPRODDATA.uName,
        'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
        'strPlant': plantCode,
        'strPO': poNumber,
    }
    response = SAPWebService.downloadPO(wsdl, PrdData)

    try:
        response = SAPWebService.downloadPO(wsdl, PrdData)
        print("No error getting response from SAP")
    except:
        print("Error getting response from SAP!")
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
        response = None
    return response


# trigger SAP to create a PO
# SAP returns:
def createPO(companyCode, vendorCode, plantCode, formID, PONumber):
    PrdData = {
        'strServer': AFEPRODDATA.server,
        'strName': AFEPRODDATA.uName,
        'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
        'strPlant': plantCode,
        'strCompany': companyCode,
        'strVendor': vendorCode,
        'strformID': formID,
        'strPOAssign': PONumber
    }
    response = SAPWebService.createPO(wsdl, PrdData)
    print(response)


# trigger SAP to create GR
# SAP returns:
def createGR(HeadText, DocDate, RefNo, formID):
    PrdData = {
        'strServer': AFEPRODDATA.server,
        'strName': AFEPRODDATA.uName,
        'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
        'strHeadText': HeadText,
        'strDocDate': DocDate,
        'strRefNo': RefNo,
        'strformID': formID
    }
    response = SAPWebService.createGR(wsdl, PrdData)
    print(response)


# #download open GR item
# #SAP returns:
def downloadGR(InvoiceNo, PONumber):
    PrdData = {
        'strServer': AFEPRODDATA.server,
        'strName': AFEPRODDATA.uName,
        'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
        'strInvoice': InvoiceNo,
        'polist': PONumber
    }
    response = SAPWebService.downloadGR(wsdl, PrdData)
    print(response)
