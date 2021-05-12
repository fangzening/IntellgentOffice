# Basic data for SAP test server
#
from cryptography.fernet import Fernet
uName = 'FIIWSYS'
server = 'PANQA902'
PWD = 'foxcnn1'
wsdl = 'http://k2d.na.foxconn.com/ws/djangosapconn.asmx?wsdl'
companyCode = 'US11'
key = Fernet.generate_key()
f = Fernet(key)
encrypt_value = f.encrypt(bytes(PWD, 'utf-8'))
# conn = Connection(ashost='10.18.222.152', sysnr='00', client='802', user='DONGJUNY', passwd='ssy3.1415926')