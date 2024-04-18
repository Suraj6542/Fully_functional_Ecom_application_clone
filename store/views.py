from django.shortcuts import render, redirect,  HttpResponseRedirect
from django.views import View
from django.contrib.auth.hashers import make_password, check_password
from .models import *
from store.middlewares.auth import auth_middleware

class Index(View):
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else: 
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1  
            else:
                cart[product] = 1 
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart

        return redirect('homepage')

    def get(self, request):
        
        products = None
        categories = Category.get_all_categories()
        categoryID = request.GET.get('category')
        if categoryID:
            products = Product.get_all_products_by_categoryid(categoryID)
        else:
            products = Product.get_all_products();

        data = {}
        data['products'] = products
        data['categories'] = categories
        return render(request, 'index.html', data)
    

    


class Signup(View):
    def get(self, request):
        return render(request, 'signup.html')
    def post(self, request):
        postData = request.POST
        first_name = postData.get('firstname')
        last_name = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        #validation
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }

        error_message = None
        customer = Customer(first_name=first_name,
                                last_name=last_name,
                                phone=phone,
                                email=email,
                                password=password)

        if(not first_name):
            error_message = "First Name required !!"
        elif len(first_name) < 4:
            error_message = "First Name must be more than 4 characters !!"
        elif not last_name:
            error_message = "Last_name required !!"
        elif not phone:
            error_message = "phone number required !!"
        elif len(password) < 3:
            error_message = "password must be more than 3 char !!"
        elif len(email) < 4:
            error_message = "Email must be 4 char long !!"
        
        elif customer.isExists():
            error_message = 'Email already registered'
        #saving
        if not error_message :
            customer.password = make_password(customer.password)
            customer.register()

            return redirect('login')
        else:
            data = {
                'error' : error_message,
                'values' : value
                    }
    
            return render(request, 'signup.html', data)
        

class Login(View):
    return_url = None
    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
           flag =  check_password(password, customer.password)
           if flag:
              request.session['customer'] = customer.id
              
              if Login.return_url:
                return HttpResponseRedirect(Login.return_url)
              else:
                Login.return_url = None
                return redirect('homepage')
           else:
               error_message = 'email or password invalid!!' 
        else:
           error_message = 'email or password invalid!!'
           return render(request, 'login.html', {'error': error_message})
        
def logout(request): 
    request.session.clear()
    return redirect('login')

class Cart(View):
    def get(self , request):
        cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {}
            cart = {}
        ids = list(request.session.get('cart').keys())
        products = Product.get_products_by_id(ids)
        print(products)
        return render(request , 'cart.html' , {'products' : products} )



class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))
        print(address, phone, customer, cart, products)

        for product in products:
            print(cart.get(str(product.id)))
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart'] = {}

        return redirect('cart')
    
class OrderView(View):
    def get(self , request ):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request , 'orders.html'  , {'orders' : orders})

    


