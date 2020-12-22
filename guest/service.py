from guest.models import Order


# Create your service here.
def find_order(order_id, token):
    return Order.objects.filter(order_id=order_id, token=token).first()
