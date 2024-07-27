from django.http import JsonResponse 
from paypal.standard.forms import PayPalPaymentsForm   
from django.shortcuts import redirect, render
from shop.form import CustomUserForm
from shop.models import Cart, Order, OrderItem, Profile
from . models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json
import random

def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})

def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"shop/fav.html",{"fav":fav})
  else:
    return redirect("/")
    
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")


def cart_page(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"shop/cart.html",{"cart":cart})
  else:
    return redirect("/")

def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")

def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)

def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quentity>=product_qty:
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added in Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)

def logout_page(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request,"Logged out Successfully")
  return redirect("/")

def login_page(request):
  if request.user.is_authenticated:
    return redirect("/")
  else:
    if request.method=='POST':
      name=request.POST.get('username')
      pwd=request.POST.get('password')
      user=authenticate(request,username=name,password=pwd)
      if user is not None:
        login(request,user)
        messages.success(request,"Logged in Successfully")
        return redirect("/")
      else:
        messages.error(request,"Invaild User Name or Password")
        return redirect("/login")
    return render(request,"shop/login.html")

def register(request):
  form=CustomUserForm()
  if request.method=='POST':
    form=CustomUserForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request,"Registration Success You can Login Now..!")
      return redirect('/login')
  return render(request,"shop/register.html",{'form':form})

def collections(request):
    catagory=Catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{"catagory":catagory})

def collectionsview(request,name):
 if(Catagory.objects.filter(name=name,status=0)):
     products=Product.objects.filter(catagory__name=name)
     return render(request,"shop/products/index.html",{"products":products,"catagory_name":name})
 else:
     messages.warning(request,"No Such Catagory Found")
     return redirect('collections')
 

def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
     if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first() 
        return render(request,"shop/products/product_details.html",{"products":products})
     else:
        messages.error(request,"No Such Product Found")
        return redirect('collections')
    else:
        messages.error(request,"No Such Catagory Found")   
        return redirect("collections")

def checkout(request):
      rawcart = Cart.objects.filter(user=request.user)
      for item in rawcart:
            if item.product_qty > item.product.quentity :
                  Cart.objects.delete(id=item.id)
        
      cartitems = Cart.objects.filter(user=request.user)
      total_price = 0
      for item in cartitems:
          total_price = total_price + item.product.selling_price * item.product_qty
          
      userprofile = Profile.objects.filter(user=request.user).first()
      
      context = {'cartitems':cartitems, 'total_price':total_price, 'userprofile':userprofile}
      return render(request, "shop/checkout.html", context)
    
def placeorder(request):
  if request.method == "POST":
        
        currentuser = User.objects.filter(id=request.user.id).first()
        
        if not currentuser.first_name:
            currentuser.first_name = request.POST.get('fname')
            currentuser.last_name = request.POST.get('lname')
            currentuser.save()
            
        if not Profile.objects.filter(user=request.user):
              userprofile = Profile()
              userprofile.user = request.user
              userprofile.phone = request.POST.get('phone')
              userprofile.address = request.POST.get('address')
              userprofile.city = request.POST.get('city')
              userprofile.state = request.POST.get('state')
              userprofile.country = request.POST.get('country')
              userprofile.pincode = request.POST.get('pincode')
              userprofile.save()
        
        neworder = Order()
        neworder.user = request.user
        neworder.fname = request.POST.get('fname')
        neworder.lname = request.POST.get('lname')
        neworder.email = request.POST.get('email')
        neworder.phone = request.POST.get('phone')
        neworder.address = request.POST.get('address')
        neworder.city = request.POST.get('city')
        neworder.state = request.POST.get('state')
        neworder.country = request.POST.get('country')
        neworder.pincode = request.POST.get('pincode')
        
        neworder.payment_mode = request.POST.get('payment_mode')
        
        cart = Cart.objects.filter(user=request.user)
        cart_total_price = 0
        for item in cart:
            cart_total_price = cart_total_price + item.product.selling_price * item.product_qty
              
        neworder.total_price = cart_total_price
        trackno = 'sathya'+str(random.randint(1111111,9999999))
        while Order.objects.filter(tracking_no=trackno) is None:
              trackno = 'sathya'+str(random.randint(1111111,9999999))
              
        neworder.tracking_no = trackno
        neworder.save()
        
        neworderitems = Cart.objects.filter(user=request.user)
        for item in neworderitems:
              OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quentity=item.product_qty
              )
              
              # To decrease the product quentity from available stock
              orderproduct = Product.objects.filter(id=item.product_id).first()
              orderproduct.quentity = orderproduct.quentity = item.product_qty
              orderproduct.save()
              
          # To clear user's Cart
        Cart.objects.filter(user=request.user).delete()
            
        messages.success(request, "Your order has been placed successfully")
        return redirect('/')
      
   