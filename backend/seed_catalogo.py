"""
Reemplaza el catálogo heredado del proyecto de ventas por uno clínico.

Uso:  python manage.py shell < seed_catalogo.py

Los productos viejos no se borran: quedan inactivos, así que las facturas
ya emitidas siguen mostrando correctamente lo que se vendió.
"""
from catalog.models import Categoria, Producto

# (categoría, descripción, IVA %, [(código, nombre, precio, stock, stock mínimo)])
CATALOGO = [
    ('Consultas Médicas', 'Atención ambulatoria por especialidad', '0.00', [
        ('CONS-001', 'Consulta de medicina general', '25.00', 9999, 0),
        ('CONS-002', 'Consulta de pediatría',        '30.00', 9999, 0),
        ('CONS-003', 'Consulta de ginecología',      '35.00', 9999, 0),
        ('CONS-004', 'Consulta de cardiología',      '45.00', 9999, 0),
        ('CONS-005', 'Consulta de dermatología',     '35.00', 9999, 0),
        ('CONS-006', 'Consulta de traumatología',    '40.00', 9999, 0),
    ]),
    ('Exámenes de Laboratorio', 'Pruebas clínicas procesadas en laboratorio', '0.00', [
        ('LAB-001', 'Biometría hemática completa', '12.00', 9999, 0),
        ('LAB-002', 'Química sanguínea',           '18.00', 9999, 0),
        ('LAB-003', 'Examen elemental de orina',    '8.00', 9999, 0),
        ('LAB-004', 'Perfil lipídico',             '22.00', 9999, 0),
    ]),
    ('Procedimientos', 'Procedimientos menores en consulta externa', '0.00', [
        ('PROC-001', 'Curación simple',            '15.00', 9999, 0),
        ('PROC-002', 'Sutura de herida',           '35.00', 9999, 0),
        ('PROC-003', 'Nebulización',               '10.00', 9999, 0),
        ('PROC-004', 'Inyección intramuscular',     '5.00', 9999, 0),
    ]),
    ('Insumos Médicos', 'Material de uso clínico con control de inventario', '15.00', [
        ('INS-001', 'Jeringa descartable 5 ml',        '0.35', 500, 100),
        ('INS-002', 'Gasa estéril 10x10',              '1.20', 300,  60),
        ('INS-003', 'Alcohol antiséptico 250 ml',      '2.50',  80,  20),
        ('INS-004', 'Guantes de examen (caja de 100)', '8.50',  45,  15),
    ]),
]


def limpiar_catalogo_heredado():
    """Desactiva productos y categorías del proyecto de ventas original."""
    nuevos = {cod for _, _, _, ps in CATALOGO for cod, *_ in ps}

    productos = [p for p in Producto.objects.all() if p.codigo not in nuevos]
    for producto in productos:
        producto.soft_delete()

    nombres_nuevos = {nombre for nombre, _, _, _ in CATALOGO}
    categorias = [c for c in Categoria.objects.all() if c.nombre not in nombres_nuevos]
    for categoria in categorias:
        categoria.soft_delete()

    return len(productos), len(categorias)


def cargar_catalogo_clinico():
    """Crea o actualiza el catálogo del hospital."""
    creados = actualizados = 0

    for nombre, descripcion, iva, productos in CATALOGO:
        categoria, _ = Categoria.all_objects.update_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion, 'is_active': True, 'deleted_at': None},
        )

        for codigo, nom, precio, stock, minimo in productos:
            _, nuevo = Producto.all_objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nom,
                    'precio': precio,
                    'iva_porcentaje': iva,
                    'stock': stock,
                    'stock_minimo': minimo,
                    'categoria': categoria,
                    'is_active': True,
                    'deleted_at': None,
                },
            )
            creados += 1 if nuevo else 0
            actualizados += 0 if nuevo else 1

    return creados, actualizados


prod_off, cat_off = limpiar_catalogo_heredado()
print(f'Desactivados: {prod_off} productos, {cat_off} categorías del catálogo anterior.')

creados, actualizados = cargar_catalogo_clinico()
print(f'Catálogo clínico: {creados} productos creados, {actualizados} actualizados.')
print('Listo. Revisa Catálogo → Productos.')