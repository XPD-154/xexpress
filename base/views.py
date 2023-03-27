from django.shortcuts import render
from .models import *                   #import all models into view
from django.http import JsonResponse
import requests
import json

#Create your views here.

'''check and update cart item total based on items added'''

def cartItems(request, number):
    request.session['cartItems'] = number
    return request.session['cartItems']

def cartItemsCheck(request):
    if 'cartItems' in request.session:
        cartData = request.session['cartItems']
    else:
        cartData = cartItems(request, 0)

    return cartData

'''end of check and update cart item total based on items added'''

def index(request):
    products = Product.objects.all().order_by('id')[:3]

    #get cart item total
    cartData = cartItemsCheck(request)

    context = {'products':products, 'cartItems':cartData}
    return render(request, 'base/index.html', context)

def about(request):
    context = {}
    return render(request, 'base/about.html', context)

def product(request):
    products = Product.objects.all()

    #check if user is authenticated
    if request.user.is_authenticated:
        #get customer
        customer = request.user.customer
        #check for customer's order create one or check for existing
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        #get all orderitems that have order on top as parents
        items = order.orderitem_set.all()

        #get cart item total
        cartItemsNumber = order.get_cart_items
        cartData = cartItems(request, cartItemsNumber)

    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}

        #get cart item total
        cartItemsNumber = order['get_cart_items']
        cartData = cartItems(request, cartItemsNumber)

    context = {'products':products, 'cartItems':cartData}
    return render(request, 'base/product.html', context)

def contact(request):
    context = {}
    return render(request, 'base/contact.html', context)

def cart(request):
    #check if user is authenticated
    if request.user.is_authenticated:
        #get customer
        customer = request.user.customer
        #check for customer's order create one or check for existing
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        #get all orderitems that have order on top as parents
        items = order.orderitem_set.all()

        #get cart item total
        cartItemsNumber = order.get_cart_items
        cartData = cartItems(request, cartItemsNumber)

    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}

        #get cart item total
        cartItemsNumber = order['get_cart_items']
        cartData = cartItems(request, cartItemsNumber)

    context = {'items':items, 'order':order, 'cartItems':cartData}
    return render(request, 'base/cart.html', context)

def checkout(request):
    #check if user is authenticated
    if request.user.is_authenticated:
        #get customer
        customer = request.user.customer
        #check for customer's order create one or check for existing
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        #get all orderitems that have order on top as parents
        items = order.orderitem_set.all()
    else:
        #create empty cart for non-logged users
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}

    #get cart item total
    cartData = cartItemsCheck(request)

    context = {'items':items, 'order':order, 'cartItems':cartData}
    return render(request, 'base/checkout.html', context)

def updateItem(request):

    #load items from javascript API and make items available
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    #get signed in customer, the product, order and order item
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    #add or remove from orderitem quantity
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    #save after changes
    orderItem.save()

    #if orderitem quantity is zero, delete
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('item was added', safe=False)

