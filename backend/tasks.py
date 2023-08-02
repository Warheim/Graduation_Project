import requests
import yaml
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.validators import URLValidator
from django.db.utils import IntegrityError

from backend.models import Provider, Category, Catalog, Product, ProductCharacteristic, Characteristic


@shared_task()
def send_email(title, message, address):
    """
    Sends email with indicated title and message to indicated user
    """
    send_mail(title, message, settings.EMAIL_HOST_USER, [address], fail_silently=False)


@shared_task()
def do_import(url, user_id=None):
    """
    Performs import of catalogs from file with determinated structure
    """

    url_validator = URLValidator()
    try:
        url_validator(url)
    except ValidationError:
        return {'status': 'fail', "detail": 'Enter a valid URL.'}

    import_file = requests.get(url).content
    data = yaml.load(import_file, Loader=yaml.FullLoader)

    try:
        if user_id:
            provider, created = Provider.objects.get_or_create(
                user__id=user_id, name=data["shop"]
            )
            provider = Provider.objects.get(name=data["shop"])
        else:
            if not Provider.objects.filter(name=data["shop"]).exists():
                return {'status': 'fail', "detail": "Indicted provider does not exist"}
    except IntegrityError:
        return {'status': 'fail', "detail": "Request user already refers to another provider instance"}

    for category in data["categories"]:
        try:
            category_instance, created = Category.objects.get_or_create(
                id=category["id"], name=category["name"]
            )
            category_instance.provider_id.add(provider.id)
            category_instance.save()
        except IntegrityError:
            return {'status': 'fail', "detail": "Category with id from your file already exists with another name"}

    for db_catalog in Catalog.objects.filter(provider_id=provider.id):
        db_catalog.quantity = 0
        db_catalog.save()

    for import_catalog in data["goods"]:
        try:
            product, created = Product.objects.get_or_create(
                name=import_catalog["name"],
                category_id=Category.objects.get(id=import_catalog["category"]),
                description=import_catalog["model"]
            )

        except MultipleObjectsReturned:
            product = Product.objects.filter(
                name=import_catalog["name"], category__id=import_catalog["category"]
            ).first()
        if Catalog.objects.filter(
            article=import_catalog["id"], product_id=product.id, provider_id=provider.id
        ).exists():
            catalog = Catalog.objects.get(
                article=import_catalog["id"], product_id=product.id, provider_id=provider.id
            )
            catalog.purchase_price = import_catalog["price"]
            catalog.retail_price = import_catalog["price_rrc"]
            catalog.quantity = import_catalog["quantity"]
            catalog.save()
            ProductCharacteristic.objects.filter(catalog_id=catalog.id).delete()
        else:
            catalog = Catalog.objects.create(
                article=import_catalog["id"],
                product_id=product,
                provider_id=provider,
                purchase_price=import_catalog["price"],
                retail_price=import_catalog["price_rrc"],
                quantity=import_catalog["quantity"],
            )
        for name, value in import_catalog["parameters"].items():
            characteristic, created = Characteristic.objects.get_or_create(
                name=name
            )
            ProductCharacteristic.objects.create(
                characteristic_id=characteristic, catalog_id=catalog, value=value
            )

    return {'status': "success", 'detail': "Import or update performed successfully"}