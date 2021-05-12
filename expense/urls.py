from django.urls import path

from . import views

urlpatterns = [
    #path('multiple/',views.ExpenseFormView.as_view(),name='getExpense'),
    # path('create/',views.ExpenseCreate.as_view(),name="newExpense"),
    # path('expense_approve/<slug:pk>/',views.showExpenseForm,name='approveExpense'),
    path('expense_create/',views.add_expense_without_modelform,name="add_expense_without_modelform"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('History/',views.expense_history,name="history"),
    path('itemasset/<str:item_id>',views.get_asset_by_item,name="viewasset"),
    path('process/',views.process_expense,name="process"),
    path('checkapprover/',views.checkapprover,name="checkapprover"),
    path('checkBU/',views.get_BU_by_CCs,name="getBU"),
    path('checkCC/',views.get_CCs_by_company,name="getCCs"),
    path('checkInvoice/',views.check_invoice_no,name="checkInvoice"),
    path('checkAppCC/',views.check_designated_approvers,name="checkAppCC"),
    path('asset_create/',views.asset_create,name="create_asset"),
    path('usetax_create/',views.usetax_create,name="create_usetax"),
    path('usetax_delete/',views.delete_usetax,name="delete_use_tax"),
    path('glbycode/',views.getGlbycode,name="get_GLdescription"),
    path('to_asset_create/<str:item_id>',views.to_create_asset,name="to_asset_create"),
    path('asset_delete/',views.delete_asset,name="delet_asset"),
    # path('delete_asset/<str:asset_id>',views.delete_asset,name="delete asset"),
    path('get_item/<str:item_id>',views.get_item,name='get_item'),
    path('<str:expense_id>/<str:type>', views.showExpenseForm, name='details'),
    path('ExpenseToApprove/',views.expense_to_approve,name="to_approve"),
    path('getitemasset/',views.get_asset_by_item,name="getasset")
    # path('expense_detail',views.showExpenseForm,name="showdetails")
]