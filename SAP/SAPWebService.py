# Do Not modify this file unless necessary
from zeep import *
from requests import *
from zeep.plugins import *

# session infor for SAP, Do not change
session = Session()
session.verify = False
transport = Transport(session=session)
history = HistoryPlugin()


# Get Vendor Code
def vendorCode(wsdl, data):
    client = Client(wsdl=wsdl, transport=transport)
    response = client.service.SAPVENDORCODE(**data)
    return response


# create AP
def createAP(wsdl, data):
    client = Client(wsdl=wsdl, transport=transport)
    response = client.service.SAPAPCREATE(**data)
    return response


# downlaod PO
def downloadPO(wsdl, data):
    client = Client(wsdl=wsdl, transport=transport)
    response = client.service.SAPOPENPO(**data)
    print(f'inner response: {response}')
    return response

# create New PO entry
def createPO(wsdl, data):
    client = Client(wsdl=wsdl, transport=transport)
    response = client.service.SAPMROPOCREATE(**data)
    return response

# create New GR entry
def createGR(wsdl, data):
    client = Client(wsdl=wsdl, transport=transport)
    response = client.service.SAPMROGRCREATE(**data)
    return response

# download open GR item
def downloadGR(wsdl, data):
    client = Client(wsdl=wsdl, transport=transport)
    response = client.service.SAPOPENGR(**data)
    return response

#check if invoice is unique in SAP system
def checkinvoice(wsdl,data):
    client = Client(wsdl=wsdl,transport=transport)
    response = client.service.SAPINVOICECHECK(**data)
    return response
