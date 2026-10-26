from datetime import date,datetime
from inmobiliaria.modelos import ItemResultado,Match,Explicacion
from inmobiliaria.ui.logica import ordenar_items,formatear_precio,formatear_porcentaje,icono_para


def test_resultados_tarjetas_incluyen_datos_y_porcentaje(propiedad):
    item=ItemResultado(propiedad,Match(None,None,propiedad.id,90,date.today()),Explicacion(None,None,'Explicación','plantilla',datetime.now()))
    assert item.propiedad.title and item.propiedad.precio
    assert formatear_precio(item.propiedad.precio,item.propiedad.moneda)=='USD 200.000'
    assert formatear_porcentaje(item.match.porcentaje_compatibilidad)=='90,0 %'
    assert icono_para('Departamento')=='🏢'


def test_ordenar_por_mayor_y_menor(propiedad):
    def item(p,id):return ItemResultado(propiedad,Match(None,None,id,p,date.today()),Explicacion(None,None,'hola','plantilla',datetime.now()))
    a,b=item(90,'a'),item(70,'b')
    assert ordenar_items([b,a],'mayor compatibilidad')==[a,b]
    assert ordenar_items([a,b],'menor compatibilidad')==[b,a]


def test_rentabilidad_bloque_separado(propiedad):
    from inmobiliaria.modelos import Rentabilidad
    m=Match(None,None,propiedad.id,85,date.today(),rentabilidad=Rentabilidad(10,500,3.2,6,'USD',True))
    item=ItemResultado(propiedad,m,Explicacion(None,None,'estimada','plantilla',datetime.now()))
    assert item.match.rentabilidad.rentabilidad_bruta_anual==3.2
    assert item.match.porcentaje_compatibilidad==85
