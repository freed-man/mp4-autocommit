from django.http import HttpResponse
from .models import Order, OrderLineItem
from services.models import Service

import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks."""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle a generic/unknown/unexpected webhook event."""
        return HttpResponse(
            content=f'unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook from Stripe."""
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        username = intent.metadata.username

        billing_details = intent.charges.data[0].billing_details
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=billing_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=billing_details.phone,
                    order_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            return HttpResponse(
                content=(
                    f'webhook received: {event["type"]} | '
                    'SUCCESS: verified order already in database'
                ),
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=billing_details.name,
                    email=billing_details.email,
                    phone_number=billing_details.phone,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for bag_key, item_data in json.loads(bag).items():
                    service = Service.objects.get(
                        id=item_data['service_id']
                    )
                    order_line_item = OrderLineItem(
                        order=order,
                        service=service,
                        vehicle_reg=item_data.get('reg', ''),
                        quantity=item_data['quantity'],
                    )
                    order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=(
                        f'webhook received: {event["type"]} | '
                        f'ERROR: {e}'
                    ),
                    status=500)

        return HttpResponse(
            content=(
                f'webhook received: {event["type"]} | '
                'SUCCESS: created order in webhook'
            ),
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """Handle the payment_intent.payment_failed webhook."""
        return HttpResponse(
            content=f'webhook received: {event["type"]}',
            status=200)