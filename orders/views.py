import requests
import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from shop import settings
from .cart import Cart
from home.models import Product
from .forms import CartAddForm, CouponApplyForm
from .models import Order, OrderItem, Coupon


class CartView(View):
    def get(self, request):
        cart = Cart(request)
        return render(request, 'orders/cart.html', {'cart': cart})


class CartAddView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])
        return redirect('orders:cart')


class CartRemoveView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart')


class OrderDetailView(LoginRequiredMixin, View):
    form_class =CouponApplyForm
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/order.html', {'order': order, 'form':self.form_class})


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()
        return redirect('orders:order_detail', order_id=order.id)



class OrderPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        request.session['order_pay'] = {
            'order_id': order.id,
        }
        callback_url = request.build_absolute_uri('/orders/verify/')
        amount = order.get_total_price()

        data = {
            "merchant" : settings.merchant_id,
            "amount" : order.get_total_price(),
            "callbackUrl" : callback_url,
            "description" : "Test Payment"
        }

        response = requests.post('https://gateway.zibal.ir/v1/request', json=data)
        result = response.json()

        if result["result"] == 100:
            return redirect(f'https://gateway.zibal.ir/start/{result["trackId"]}')
        else:
            return HttpResponse(f"Error: {result['message']}")



class OrderVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        track_id = request.GET.get('trackId')
        order = get_object_or_404(Order, id=request.session['order_pay']['order_id'])

        data = {
            "merchant" : settings.merchant_id,
            "trackId" : track_id
        }

        response = requests.post('https://gateway.zibal.ir/v1/verify', json=data)
        result = response.json()

        if result["result"] == 100:
            order.paid = True
            order.save()
            return HttpResponse(f"Payment Successful! Ref ID: {result['refNumber']}")
        else:
            return HttpResponse(f"Payment Failed! Error Code: {result['result']}")


class CouponApplyView(LoginRequiredMixin, View):
    form_class =CouponApplyForm
    def post(self, request, order_id):
        now = datetime.datetime.now()
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code__exact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            except Coupon.DoesNotExist:
                messages.error(request, 'this coupon does not exist', 'danger')
                return redirect('orders:order_detail', order_id=order_id)
            order = Order.objects.get(id=order_id)
            order.discount = coupon.discount
            order.save()
        return redirect('orders:order_detail', order_id=order_id)