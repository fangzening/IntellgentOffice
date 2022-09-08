# Intellgent Office

# Objectives
To design, develop, test, and deploy an OA (office automation) software-

# Project Scope
1. Human Resource Module
2. Company Heriachary Structure
3. Review and Approval Process
4. Purchasing Module
5. Material Adjustment Module
6. Business Travel Module
7. Finacial Review Module
8. Public Relationship Module
9. Shipment Module
10. Asset Control Module
11. Cost Allocation Module
12. Inventory Module
13. Budget Control Module
14. Logistic Expense Tracking Module
15. Optical Data Reconginazation Module
16. SAP interface
# System Scope
1. Webservice
2. Database
3. User Interface
# Applications

The smart office project currently consists of two application.
1.  Smart HR - *To help in on-boarding hiring process*
2.  Travel Application & Travel Reimbursement - *To manage and log travel information*

# Prerequisites 

1. Python v3.9.1 or above - *required*
2. Django Framework v3.0.2 - *required* (will be installed when installing dependencies)
3. JetBeans PyCharm IDE - *recommended*

# Preparation

1. Create a new project in Pycharm by cloning git `http://10.20.67.86/ZeningFang/smart-office.git`
1. Install dependencies using terminal `pip install -r requirements.txt`
2. Create database tables `python manage.py migrate` (if not already created in the database)
3. Create admin account `python manage.py createsuperuser` (if not already created in the database)
4. Visit `http://localhost:8000` or `http://127.0.0.1:8000` in your browser
5. Visit the admin panel `http://localhost:8000/admin` to easily manipulate data

# Url to the application

1. Smart HR - `http://127.0.0.1:8000/smart_hr` 
2. Travel Reimbursement - `http://127.0.0.1:8000/travel` 





