# Generated by Django 3.2.22 on 2024-09-20 02:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0003_rename_correo_usuario_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('productos', '0006_auto_20240918_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApadrinamientoArbol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_apadrinamiento', models.DateTimeField(auto_now_add=True)),
                ('latitud', models.FloatField(blank=True, null=True)),
                ('longitud', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CausaAmbiental',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Donacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('porcentaje', models.DecimalField(decimal_places=2, max_digits=5)),
                ('causa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.causaambiental')),
            ],
        ),
        migrations.CreateModel(
            name='MetodoEntrega',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('tiempo_estimado', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TipoArbol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_pedido', models.DateTimeField(auto_now_add=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('porcentaje_donacion', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('estado', models.CharField(default='Pendiente', max_length=50)),
                ('apadrinamiento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='productos.apadrinamientoarbol')),
                ('carrito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.carrito')),
                ('comuna_entrega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuentas.comuna')),
                ('direccion_entrega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuentas.direccion')),
                ('metodo_entrega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.metodoentrega')),
                ('monto_donacion', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='productos.donacion')),
                ('region_entrega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuentas.region')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Envio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('costo_envio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_envio', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(default='Pendiente', max_length=50)),
                ('metodo_entrega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.metodoentrega')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.pedido')),
            ],
        ),
        migrations.AddField(
            model_name='donacion',
            name='pedido_donacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.pedido'),
        ),
        migrations.AddField(
            model_name='apadrinamientoarbol',
            name='tipo_arbol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.tipoarbol'),
        ),
        migrations.AddField(
            model_name='apadrinamientoarbol',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
