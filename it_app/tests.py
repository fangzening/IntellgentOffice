from django.test import TestCase

# Create your tests here.
'''
Corrina Created this class for debugging so it saves load time
'''
from SAP.SAPFunctions import *
from purchase.models import *

class ZhuLi():
    @staticmethod
    def do_the_thing():
        the_thing = PurchaseRequestForm.objects.get(formID=200).generate_pr_num()
        return the_thing