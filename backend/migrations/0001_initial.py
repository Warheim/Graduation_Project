# Generated by Django 4.2.3 on 2023-08-02 08:54

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=150)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('company', models.CharField(max_length=50)),
                ('position', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('admin', 'администратор'), ('buyer', 'покупатель'), ('seller', 'продавец')], default='customer', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Список пользователей',
                'ordering': ('id',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.CharField(blank=True, max_length=50, null=True)),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=16, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('retail_price', models.DecimalField(decimal_places=2, max_digits=16, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('quantity', models.PositiveIntegerField()),
                ('delivery_cost', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Каталог продуктов',
                'verbose_name_plural': 'Список продуктов каталога',
                'ordering': ('product_id', 'purchase_price'),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Список категорий',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Characteristic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Список характеристик',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Покупатель',
                'verbose_name_plural': 'Список покупателей',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CustomerInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('street', models.CharField(blank=True, max_length=50, null=True)),
                ('house', models.CharField(blank=True, max_length=50, null=True)),
                ('structure', models.CharField(blank=True, max_length=50, null=True)),
                ('building', models.CharField(blank=True, max_length=50, null=True)),
                ('apartment', models.CharField(blank=True, max_length=50, null=True)),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_positions', to='backend.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.CharField(choices=[('accepted', 'подтверждён'), ('canceled', 'отменён')], default='saved', max_length=15)),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='backend.customer')),
                ('delivery_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='backend.customerinfo')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Список заказов',
                'ordering': ('-order_date', 'customer_id'),
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Список магазинов',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('url', models.CharField(blank=True, max_length=200, null=True)),
                ('order_is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Поставщик',
                'verbose_name_plural': 'Список поставщиков',
                'ordering': ('-order_is_active', 'name'),
            },
        ),
        migrations.CreateModel(
            name='ProductCharacteristic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=30)),
                ('catalog_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_characteristics', to='backend.catalog')),
                ('characteristic_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_characteristics', to='backend.characteristic')),
            ],
            options={
                'verbose_name': 'Характеристика продукта в каталоге',
                'verbose_name_plural': 'Список характеристик продукта в каталоге',
                'ordering': ('catalog_id', 'value'),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='backend.category')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Список продуктов',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('token', models.UUIDField(default=uuid.uuid4)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Токен сброса пароля',
                'verbose_name_plural': 'Токены сброса пароля',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('catalog_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='backend.catalog')),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='backend.order')),
            ],
            options={
                'verbose_name': 'Позиция заказа',
                'verbose_name_plural': 'Список позиций заказов',
                'ordering': ('order_id', 'quantity'),
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='shop',
            field=models.ManyToManyField(related_name='customers', to='backend.provider'),
        ),
        migrations.AddField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='category',
            name='provider_id',
            field=models.ManyToManyField(blank=True, related_name='categories', to='backend.provider'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalogs', to='backend.product'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='provider_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalogs', to='backend.provider'),
        ),
        migrations.AddConstraint(
            model_name='productcharacteristic',
            constraint=models.UniqueConstraint(fields=('catalog_id', 'characteristic_id'), name='unique_product_characteristic'),
        ),
        migrations.AddConstraint(
            model_name='orderitem',
            constraint=models.UniqueConstraint(fields=('order_id', 'catalog_id'), name='unique_order_catalog'),
        ),
        migrations.AddConstraint(
            model_name='catalog',
            constraint=models.UniqueConstraint(fields=('article', 'product_id', 'provider_id'), name='unique_catalog'),
        ),
    ]
