# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import HttpResponseRedirect
import razorpay
from django.views.decorators.csrf import csrf_exempt



def payments(request):
    print('ujjwal_2')
    order_id = request.POST.get('order_id')
    print(f"{order_id = }")
    order = Order.objects.get(id=order_id)
    print(order)

    if not order:
        messages.error(request, f"Order Not Genrated!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    if request.method=="POST":
        order = Order.objects.filter(user=request.user, is_ordered=False,id=order.id).last()
        if order:
            get_total_amount = order.order_total   
            print(f"{get_total_amount = }")
            print(f"{type(get_total_amount) = }")
            get_name = order.user.first_name + '' + order.user.last_name
            get_email = order.user.email

            client = razorpay.Client(auth=("rzp_test_SjQuoGgh17Ps5G" , "BmNrvpc0S7W7aqGkFn8oknrw"))

            #Payment capture = 1 for automatic , 0 for manual
            payment = client.order.create({'amount':int(get_total_amount*100) , 'currency':'INR' , 'payment_capture':'1'})
            print(payment)
            payment_db = Payment.objects.create(user = request.user,
                                        payment_id = payment['id'],
                                        # payment_method = body['payment_method'],
                                        amount_paid = int(order.order_total),
                                        # status = body['status'],
                                        )
            print(f"{payment = }")
            return render(request, "orders/payments.html", {'payment': payment})
        return render(request, "orders/payments.html", {'payment': payment})
    # body = json.loads(request.body)
    # order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # # Store transaction details inside Payment model
    # payment = Payment(
    #     user = request.user,
    #     payment_id = body['transID'],
    #     payment_method = body['payment_method'],
    #     amount_paid = order.order_total,
    #     status = body['status'],
    # )
    # payment.save()

    # order.payment = payment
    # order.is_ordered = True
    # order.save()

    # # Move the cart items to Order Product table
    # cart_items = CartItem.objects.filter(user=request.user)

    # for item in cart_items:
    #     orderproduct = OrderProduct()
    #     orderproduct.order_id = order.id
    #     orderproduct.payment = payment
    #     orderproduct.user_id = request.user.id
    #     orderproduct.product_id = item.product_id
    #     orderproduct.quantity = item.quantity
    #     orderproduct.product_price = item.product.price
    #     orderproduct.ordered = True
    #     orderproduct.save()

    #     cart_item = CartItem.objects.get(id=item.id)
    #     product_variation = cart_item.variations.all()
    #     orderproduct = OrderProduct.objects.get(id=orderproduct.id)
    #     orderproduct.variations.set(product_variation)
    #     orderproduct.save()


    #     # Reduce the quantity of the sold products
    #     product = Product.objects.get(id=item.product_id)
    #     product.stock -= item.quantity
    #     product.save()

    # # Clear cart
    # CartItem.objects.filter(user=request.user).delete()

    # # Send order recieved email to customer
    # mail_subject = 'Thank you for your order!'
    # message = render_to_string('orders/order_recieved_email.html', {
    #     'user': request.user,
    #     'order': order,
    # })
    # to_email = request.user.email
    # send_email = EmailMessage(mail_subject, message, to=[to_email])
    # send_email.send()

    # # Send order number and transaction id back to sendData method via JsonResponse
    # data = {
    #     'order_number': order.order_number,
    #     'transID': payment.payment_id,
    # }
    # return JsonResponse(data)
    
@csrf_exempt
def success(request):
    if request.method == "POST":
        a =  (request.POST)    #jo bhi razor pay ne bheja hoga post karke vo a ke andar store kar lenge
    #     # print(a)
    #     order_id = ""

    #     data = {}
    #     for key , value in a.items():
    #         if key=="razorpay_order_id":
    #             data['razorpay_order_id'] = value

    #             order_id = value

    #         elif key=="razorpay_payment_id":
    #             data['razorpay_payment_id'] = value

    #         elif key=="razorpay_signature":
    #             data['razorpay_signature'] = value

    #     user = Coffee.objects.filter(order_id=order_id).last()
    #     user.paid=True
    #     user.save()

    #     #signature verification
    #     client = razorpay.Client(auth=("rzp_test_SjQuoGgh17Ps5G" , "BmNrvpc0S7W7aqGkFn8oknrw"))
    #     check = client.utility.verify_payment_signature(data)
    #     print(check)

    #     if check is True:
    #         msg_plain = render_to_string('razorpay/email.txt')
    #         msg_html = render_to_string('razorpay/email.html')

    #         send_mail("Your Order Was Confirm! Thanku" , msg_plain , settings.EMAIL_HOST_USER , 
    #                   [user.email] , html_message = msg_html)
    #     else:
    #         return render(request, "razorpay/error.html")
        
    # return render(request, "razorpay/success.html")



def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST or None,)
        if form.is_valid():
            try:
                # Store all the billing information inside Order table
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.order_note = form.cleaned_data['order_note']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                # Generate order number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr,mt,dt)
                current_date = d.strftime("%Y%m%d") #20210305
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

                order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'tax': tax,
                    'grand_total': grand_total,
                    'order_id' : order.id
                }
                return render(request, 'orders/payments.html', context)
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # pint(f"Form errors: {form.errors}")
            messages.error(request, "Form is not valid")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number','')
    transID = request.GET.get('payment_id','')

    try:
        if order_number and transID:
            order = Order.objects.filter(order_number=order_number, is_ordered=True).last()
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity

            payment = Payment.objects.get(payment_id=transID)

            context = {
                'order': order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,
                'transID': payment.payment_id,
                'payment': payment,
                'subtotal': subtotal,
            }
            return render(request, 'orders/order_complete.html', context)
        else:
            return render(request, 'orders/order_complete.html')
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')