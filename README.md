#Mod06-Mini-Project
 
Use postman UI to interact with python app

- Start by adding user password from mysql into password.py file.
- Ensure flask, flask_sqlalchmey, marshmallow, flask_marshmallow are installed within virtual environment in python
- Run python file
- Go to postman UI
- Begin by adding customer(s) by switching the method to 'POST', adding the URL:'http://127.0.0.1:5000/customers', going to the 'Body' tab in Postman, switching to the 'raw' tab within- 
-the 'Body', and add in info per the format within the app.py file for customers example format 
-> (from app.py for Customers):

#Example format in Postman (add/update)

#{

#-     "name":"XXXXXX",
#-     "email":"YYYYYYY",
#-     "phone":"#######"

#}

- Follow this procedure to add customer accounts, products, and orders. Ensure user swaps URL to fit the desired method / function (example, switch URL to be 'http://127.0.0.1:5000/products' for products. See app.py endpoints for URL's and additional information.)
- View all created items (customers, customer accounts, products, orders) by creating a new method in postman (GET)
- Update any created item (customers, customer accounts, products, orders) by creating a new method in postman (PUT). Ensure the URL is consistent with the desired information. 
- Delete any created item (customers, customer accounts, products, orders) by creating a new method in postman (DELETE). Ensure the URL is consistent with the desired information. 

- NOTE: Deleting data from related tables can remove data from related tables. Example: deleting a product from the products endpoint will remove the product from any Orders without traceability. Removing a customer with a customer account will remove the customer id form that customer account. 

