import paypalrestsdk
from django.conf import settings
from django.urls import reverse
from .models import Pedido

# Configuración de PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # 'sandbox' o 'live' dependiendo del entorno
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def crear_pago(pedido):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": f"{settings.SITE_URL}{reverse('productos:confirmar_pago', args=[pedido.id])}",
            "cancel_url": f"{settings.SITE_URL}{reverse('productos:cancelar_pago')}"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": f"Pedido {pedido.id}",
                    "sku": f"pedido_{pedido.id}",
                    "price": str(pedido.total_final),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(pedido.total_final),
                "currency": "USD"
            },
            "description": f"Pago por el pedido {pedido.id}"
        }]
    })

    if payment.create():
        return payment  # Devolver el objeto de pago completo
    else:
        print(payment.error)  # Verifica si hay algún error en la creación del pago
        return None



def ejecutar_pago(payer_id, payment_id):
    # Buscar el pago por su ID
    payment = paypalrestsdk.Payment.find(payment_id)
    
    # Ejecutar el pago con el Payer ID obtenido
    if payment.execute({"payer_id": payer_id}):
        return payment  # Retorna la instancia de pago si es exitoso
    else:
        print(payment.error)  # Imprime el error en consola para depuración
        return None