from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    """
    Configuration for the 'checkout' application.

    This class is used to configure the checkout application and
    ensures that the signals module is imported when the app is ready.
    """
    name = 'checkout'

    def ready(self):
        import checkout.signals
