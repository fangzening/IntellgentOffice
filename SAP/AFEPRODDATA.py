# Basic data for SAP production server
from cryptography.fernet import Fernet
uName = 'FIIWSYS'
server = 'PAPRD902'
PWD = 'foxcnn1'
wsdl = 'http://k2d.na.foxconn.com/ws/djangosapconn.asmx?wsdl'
companyCode = 'US11'
key = Fernet.generate_key()
f = Fernet(key)
encrypt_value = f.encrypt(bytes(PWD, 'utf-8'))
