from django import forms
from .models import *
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from .Custom_Layout import *

class ExpenseForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ExpenseForm, self).clean()
        date = cleaned_data.get('payment_Date')
        #print("we are cleaning dare:"+date.strftime("%m/%d/%Y"))
        if date < datetime.date.today():
            raise forms.ValidationError("The date cannot be in the past!")
        return cleaned_data

    class Meta:
        model = Expense
        fields=('requester','payment_Date','BU','document_Header','invoice_ID','tax_Rate',
                'shipping_Cost',)
        widgets = {
            'payment_Date':  forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'datepicker', 'placeholder':'Select a date', 'type':'date'}),

        }

class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model=ExpenseItem
        exclude=['cost_Center_Name','active_Status','expense']

class AttachmentForm(forms.ModelForm):
    class Meta:
        model=Attachment
        fields=('attachments','description')

# class UseTaxForm(forms.ModelForm):
#     class Meta:
#         model=UseTax
#         exclude=['GL_Name','activation_status','cost_Center_Name','expense']



# class ExpenseFormSet(forms.ModelForm):
#
#     def clean(self):
#         cleaned_data = super(ExpenseFormSet, self).clean()
#         date = cleaned_data.get('payment_Date')
#         #print("we are cleaning dare:"+date.strftime("%m/%d/%Y"))
#         if date < datetime.date.today():
#             raise forms.ValidationError("The date cannot be in the past!")
#         return cleaned_data
#
#     class Meta:
#         model = Expense
#         fields=('requester','payment_Date','company','BU','BG','document_Header','invoice_ID','vendor_Name','tax_Rate',
#                 'shipping_Cost',)
#         widgets = {
#             'payment_Date':  forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'datepicker', 'placeholder':'Select a date', 'type':'date'}),
#
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(ExpenseFormSet, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_tag = True
#         self.helper.form_class = 'form-horizontal'
#         self.helper.label_class = 'col-md-3 create-label'
#         self.helper.field_class = 'col-md-9'
#         self.helper.layout = Layout(
#             Div(
#                 Field('requester'),
#                 Fieldset('Add attachments',
#                          Formset('attachments')),
#                 Fieldset('Add items',
#                          Formset('expense_items')),
#                 Fieldset('Add assets',
#                          Formset('use_tax')),
#                 Field('payment_Date'),
#                 Field('BG'),
#                 Field('BU'),
#                 Field('company'),
#                 Field('document_Header'),
#                 Field('invoice_ID'),
#                 Field('vendor_Name'),
#                 Field('tax_Rate'),
#                 Field('shipping_Cost'),
#                 HTML("<br>"),
#                 ButtonHolder(Submit('submit', 'save')),
#             )
#         )
#
# ExpenseAttachmentFormSet = inlineformset_factory(
#     Expense, Attachment, form=AttachmentForm, extra=1, can_delete=True)
#
# ExpenseItemFormSet = inlineformset_factory(
#     Expense, ExpenseItem, form=ExpenseItemForm, extra=1, can_delete=True)

# ExpenseUseTaxFormSet= inlineformset_factory(
#     Expense,UseTax, form= UseTaxForm,extra=1, can_delete=True
# )
