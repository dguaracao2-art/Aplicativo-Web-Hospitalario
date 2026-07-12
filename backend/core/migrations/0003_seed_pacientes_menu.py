from django.db import migrations


def seed_pacientes_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')

    # Módulo raíz "Pacientes" con sus 3 submódulos.
    # order=2 lo ubica justo después de "Dashboard" (order=1) en el sidebar.
    modulo = MenuItem.objects.create(
        name='Pacientes',
        icon='bi-heart-pulse',
        url_name='',
        order=2,
    )
    submodulos = [
        {'name': 'Pacientes', 'icon': 'bi-people', 'url_name': 'pacientes:listar'},
        {'name': 'Médicos', 'icon': 'bi-person-badge', 'url_name': 'pacientes:medicos_listar'},
        {'name': 'Citas', 'icon': 'bi-calendar-week', 'url_name': 'pacientes:citas_listar'},
    ]
    for idx, sub in enumerate(submodulos, start=1):
        MenuItem.objects.create(
            parent=modulo,
            name=sub['name'],
            icon=sub['icon'],
            url_name=sub['url_name'],
            order=idx,
        )


def reverse_seed(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    MenuItem.all_objects.filter(name='Pacientes', parent__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_seed_menu'),
    ]

    operations = [
        migrations.RunPython(seed_pacientes_menu, reverse_seed),
    ]