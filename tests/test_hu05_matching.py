from dataclasses import replace
from inmobiliaria.modelos import Preferencia,PerfilInversor,Rentabilidad,DetalleVariable,Match
from inmobiliaria.matching import MotorMatching


def test_caso_control_86_8(propiedad,pref_vivir):
    propiedad.caracteristicas={'colegio':1,'espacios_verdes':.9,'conectividad':.6,'espacio_trabajo':1,'silencio':.8,'accesibilidad_salud':.5}
    match=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    assert match.porcentaje_compatibilidad==86.8
    assert match.variables_clave(3)==['colegio','espacio_trabajo','espacios_verdes']
    assert match.variables_debiles(2)==['conectividad','accesibilidad_salud']


def test_ejemplo_familia_80(propiedad,pref_vivir):
    pref_vivir.pesos={'espacios_verdes':1,'conectividad':.6,'colegio':.4}
    propiedad.caracteristicas={'espacios_verdes':1,'conectividad':1,'colegio':0}
    match=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    assert match.porcentaje_compatibilidad==80.
    assert {v:d.aporte for v,d in match.detalle.items()}=={'colegio':0,'espacios_verdes':50,'conectividad':30}


def test_ejemplo_inversor_89_5(propiedad):
    pref=Preferencia(None,None,'invertir','Venta',300000,'USD','Almagro',2,{'rentabilidad':.8,'precio_m2':.6,'conectividad':.2})
    propiedad.precio_m2=100
    propiedad.caracteristicas['conectividad']=1
    renta=Rentabilidad(1,10,3.4,5,'USD',True)
    match=MotorMatching().calcular_compatibilidad(pref,propiedad,PerfilInversor(None,None,4,5),renta,92)
    assert match.porcentaje_compatibilidad==89.5
    assert [match.detalle[v].aporte for v in ('rentabilidad','precio_m2','conectividad')]==[42.5,34.5,12.5]


def test_variable_sin_dato_se_excluye_y_renormaliza(propiedad):
    pref=Preferencia(None,None,'invertir','Venta',300000,'USD','Almagro',2,{'rentabilidad':.8,'precio_m2':.6,'conectividad':.2})
    propiedad.precio_m2=100
    propiedad.caracteristicas['conectividad']=1
    match=MotorMatching().calcular_compatibilidad(pref,propiedad,PerfilInversor(None,None,4,5),Rentabilidad(None,None,None,0,'USD',False),92)
    assert match.porcentaje_compatibilidad==94.0 and match.variables_sin_dato==['rentabilidad']


def test_mayor_peso_influye_proporcionalmente(propiedad,pref_vivir):
    pref_vivir.pesos={'colegio':.2,'conectividad':1.}
    propiedad.caracteristicas={'colegio':1,'conectividad':0}
    motor=MotorMatching()
    antes=motor.calcular_compatibilidad(pref_vivir,propiedad).porcentaje_compatibilidad
    pref_vivir.pesos['colegio']=1.
    despues=motor.calcular_compatibilidad(pref_vivir,propiedad).porcentaje_compatibilidad
    assert despues>antes


def test_rankear_orden_y_desempate(propiedad,pref_vivir):
    a=replace(propiedad,id='a',id_propiedad='a',caracteristicas={'colegio':1})
    b=replace(propiedad,id='b',id_propiedad='b',caracteristicas={'colegio':1})
    assert [m.id_propiedad for m in MotorMatching().rankear(pref_vivir,[b,a])]==['a','b']


def test_variables_clave_y_debiles(propiedad,pref_vivir):
    match=MotorMatching().calcular_compatibilidad(pref_vivir,propiedad)
    assert match.variables_clave() and match.variables_debiles()
