import os
import sys
import traceback
from datetime import datetime

from django.http import HttpResponse

from office_app.approval_functions import get_approvers_for_form_at_current_stage_or_lower
from office_app.models import *
#from purchase.models import PurchaseRequestForm
import pdfrw

'''
removes any unneccesary keys from error messages. removes all items without keys that will be used in js
'''


def remove_unneccesary_keys_from_error_message_dict(dict):
    remove_these_keys = []
    for key in dict.keys():
        if key != 'other_errors' and key != 'fatal_errors' and key != 'new_pk' and key != 'slip' and 'attachment' not in key and key != 'file_link' and key != 'dir_to_dash':
            remove_these_keys.append(key)
    for key in remove_these_keys:
        dict.pop(key)
    return dict


# United States of America Python Dictionary to translate States,
# Districts & Territories to Two-Letter codes and vice versa.
#
# https://gist.github.com/rogerallen/1583593
#
# Dedicated to the public domain.  To the extent possible under law,
# Roger Allen has waived all copyright and related or neighboring
# rights to this code.

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands': 'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def is_user_buyer(request):
    allowed_view = False
    for bu in BusinessUnit.objects.filter(buBuyer__isnull=False):
        if bu.buBuyer.associateID == request.session['user_id']:
            allowed_view = True

    return allowed_view


