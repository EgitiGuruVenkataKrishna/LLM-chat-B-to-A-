from fastapi import FastAPI
from models import Product
app=FastAPI()

##Similar to CRUD Operations in DBMS 
  #here we have  
  #GET:For reading the data 
  #PUT:For Updating the data 
  #POST:For Creating the data
  #Delete:For deleting.. the data



@app.get("/")             
def greet():
     return "Welcome to Fast API"



p1=Product(id=1,name="sprite",description="No.1 Beverage",quantity=4,price=20)
p2=Product(id=2,name="coke",description="Beverage",quantity=10,price=20)
p3=Product(id=3,name="Thumps-UP",description="Beverages",quantity=5,price=20)

product_list=[p1,p2,p3]

@app.get("/products")
def products():
     return product_list

@app.get("/product/{id}")
def get_product_Id(id:int):
     for i in product_list:
          if i.id==id:
               return i
          
               return  (f"Product with ID:{id} not found ...")
        

@app.post('/products')
def add_products(p:Product):
     product_list.append(p)
     return p
             
@app.put("/products")
def update_product(id:int,p:Product):
     for i in range(len(product_list)):
          if product_list[i].id==id:
               product_list[i]=p
               return f"product Updated:{product_list[i]}"
     return "No product found"
     
@app.delete("/products")
def delete_product(id:int):
     for i in range(len(product_list)):
          if product_list[i].id==id:
               del product_list[i]
               return product_list
          