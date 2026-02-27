from modules.Domain.Plugins.AbstractPayPalPlugin import PayPalPlugin
from modules.Entities.Payment import Payment, PaymentStatus, PaymentMethod
from modules.Entities.Payer import Payer


class PayPalService:

    paypal_plugin: PayPalPlugin

    def __init__(self, paypal_plugin: PayPalPlugin):
        self.paypal_plugin = paypal_plugin

    async def pay(self, payment: Payment, payer: Payer):
        payment.check([PaymentMethod.PAYPAL])
        await self.paypal_plugin.get_access_token()
        await self.paypal_plugin.create_order(payment, payer).update_payment()

    async def status(self, payment: Payment):
        await self.paypal_plugin.get_access_token()
        await self.paypal_plugin.show_order_details(payment).update_payment()

    async def capture(self, payment: Payment):
        await self.status(payment)
        if payment.status == PaymentStatus.PENDING:
            self.paypal_plugin.capture_payment_for_order(payment).update_payment()
