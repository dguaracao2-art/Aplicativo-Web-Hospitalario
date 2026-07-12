from django.db import migrations


# (nombre del módulo padre, nombre del submódulo) -> url_name correcto
FIXES = {
    ('Seguridad', 'Usuarios'): 'security:user_list',
    ('Seguridad', 'Roles'): 'security:group_list',
    ('Catálogo', 'Categorías'): 'catalog:categoria_list',
    ('Catálogo', 'Productos'): 'catalog:producto_list',
    ('Clientes', 'Listado de Clientes'): 'customers:cliente_list',
    ('Ventas', 'Facturas'): 'invoicing:invoice_list',
    ('Ventas', 'Reportes'): 'invoicing:reports_index',
}


def fix_menu_urls(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    for (padre, hijo), url_name in FIXES.items():
        MenuItem.objects.filter(
            name=hijo, parent__name=padre, parent__isnull=False
        ).update(url_name=url_name)


def reverse_fix(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    for (padre, hijo), _ in FIXES.items():
        MenuItem.objects.filter(
            name=hijo, parent__name=padre, parent__isnull=False
        ).update(url_name='')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_seed_pacientes_menu'),
    ]

    operations = [
        migrations.RunPython(fix_menu_urls, reverse_fix),
    ]