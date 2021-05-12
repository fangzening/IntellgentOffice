# This file contains functions that pull and push to SAP, Always connect to NQA902 first for testing (use basic data
# from AFETESTDATA.py File)
import sys
import traceback
import datetime
from SAP import SAPWebService
from SAP import AFETESTDATA
from SAP import AFEPRODDATA
from office_app.models import SAPResponse
# from pyrfc import Connection


wsdl = AFETESTDATA.wsdl
testData = {
    'strServer': AFETESTDATA.server,
    'strName': AFETESTDATA.uName,
    'strPWD': AFETESTDATA.f.decrypt(AFETESTDATA.encrypt_value),
    'strID': 1,
    'strFormType': 'TA',
}

prdData = {
    'strServer': AFEPRODDATA.server,
    'strName': AFEPRODDATA.uName,
    'strPWD': AFEPRODDATA.f.decrypt(AFEPRODDATA.encrypt_value),
    'strVendorName': '*',
    'strVendorCode': '*',
    'strCompanyCode': 'US11',
}

# get vendor Code and write to a file
# result file is in string format and utf-8 encoding
def getVendorCode():
    vendorCode = SAPWebService.vendorCode(wsdl, prdData)
    f = open('result.txt', 'w', encoding='utf8')
    f.writelines(str(vendorCode))
    f.close()

# trigger SAP to upload AP info and print the response
# SAP returns DocNo, Posting Date, and SAP message
def createAP(fromId, formType):
    testData = {
        'strServer': AFETESTDATA.server,
        'strName': AFETESTDATA.uName,
        'strPWD': AFETESTDATA.f.decrypt(AFETESTDATA.encrypt_value),
        'strID': fromId,
        'strFormType': formType,
    }
    print(f"Test data: {testData}")
    response = SAPWebService.createAP(wsdl, testData)
    print("response before saving: " + str(response))

    SAPResponse(transactionID=response['SAPDocNo'],
                   sapMessage=response['SAPMessage'],
                   date=response['SAPPostDate'],
                   form=formType + "-" + str(fromId),
                ).save()

    print("response after saving: " + str(response))
    return response

# SAP2.uploadImage(AFEBasicData.wsdl, data2)


# print(vendorCode)

# this is used to check if the current invoice no exists in the SAP system to prevent from user uploading duplicate invoice
def check_invoice_SAP(invoice_id,companycode):
    # conn = Connection(user='DONGJUNY', passwd='SSY3.1415926', ashost='10.18.222.152', sysnr='00', client='802')
    # print(conn)
    Data = {
        'strServer': AFETESTDATA.server,
        'strName': AFETESTDATA.uName,
        'strPWD': AFETESTDATA.f.decrypt(AFETESTDATA.encrypt_value),
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
    testData = {
        'strServer': AFETESTDATA.server,
        'strName': AFETESTDATA.uName,
        'strPWD': AFETESTDATA.f.decrypt(AFETESTDATA.encrypt_value),
        'strPlant': plantCode,
        'strPO': poNumber
    }
    # try:
    response = SAPWebService.downloadPO(wsdl, testData)
    print("No error getting response from SAP")
    # except:
    # print("Error getting response from SAP!")
    # print('\n'.join(traceback.format_exception(*sys.exc_info())))
    # response = None
    return response

# trigger SAP to create a PO
# SAP returns:
def createPO(companyCode, vendorCode, plantCode, formID, PONumber):
    testData = {
        'strServer': AFETESTDATA.server,
        'strName': AFETESTDATA.uName,
        'strPWD': AFETESTDATA.f.decrypt(AFETESTDATA.encrypt_value),
        'strPlantCode': plantCode,
        'strCompanyCode': companyCode,
        'strVendorCode': vendorCode,
        'strFormID': formID,
        'strPOAssign': PONumber
    }
    print(f"test data: {testData}")
    response = SAPWebService.createPO(wsdl, testData)
    print(response)
    return response


# trigger SAP to create GR
# SAP returns:
def createGR(HeadText, DocDate, RefNo, formID):
    # HeadText - Empty String
    # DocDate - YYYYMMDD
    # RefNo - Packing Slip ID (can be formatted in any way, wont mess up sap)
    # formID - GR Form ID
    testData = {
        'strServer': AFETESTDATA.server,
        'strName': AFETESTDATA.uName,
        'strPWD': AFETESTDATA.f.decrypt(AFETESTDATA.encrypt_value),
        'strHeadText': HeadText,
        'strDocDate': DocDate,
        'strRefNo': RefNo,
        'strFormID': formID
    }
    print(f"Test Data: {testData}")
    response = SAPWebService.createGR(wsdl, testData)
    print(response)
    return response

# #download open GR item
# #SAP returns:
def downloadGR(InvoiceNo, PONumber):
    testData = {
        'strServer': AFETESTDATA.server,
        'strName': AFETESTDATA.uName,
        'strPWD': AFETESTDATA.f.decrypt(AFETESTDATA.encrypt_value),
        'strInvoice': InvoiceNo,
        'polist': PONumber
    }
    response = SAPWebService.downloadGR(wsdl, testData)
    print(response)
    return response
