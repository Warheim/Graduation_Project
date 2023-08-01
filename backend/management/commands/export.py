import yaml
from django.core.management.base import BaseCommand
from backend.models import Provider, Category, Catalog


class Command(BaseCommand):
    """
        Class to arrange management command export_goods.
    """

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def handle(self, *args, **options):
        """
        Method to describe the actual logic of the command export
        """
        self.do_import('import.yml')
        result = {'categories': [],
                  'shop': [],
                  'goods': []}
        for category in Category.objects.all():
            result['categories'].append({'id': category.id, 'name': category.name})
        for provider in Provider.objects.all():
            result['shop'].append({'id': provider.id, 'name': provider.name})

        for catalog in Catalog.objects.all().\
                prefetch_related('product_characteristics', 'product_characteristics__characteristic').\
                select_related('product_id', 'product_id__category_id', 'provider_id'):
            parameters = {}
            for parameter in catalog.product_characteristics.all():
                parameters[parameter.characteristic.name] = parameter.value

            result['goods'].append({'id': catalog.article,
                                    'category': catalog.product_id.category_id.id,
                                    'name': catalog.product_id.name,
                                    'shop': catalog.provider_id.id,
                                    'price': float('{:.2f}'.format(catalog.purchase_price)),
                                    'price_rrc': float('{:.2f}'.format(catalog.retail_price)),
                                    'quantity': catalog.quantity,
                                    'parameters': parameters})
        with open('export.yml', 'w', encoding='utf8') as outfile:
            yaml.dump(result, outfile, allow_unicode=True, default_flow_style=False)