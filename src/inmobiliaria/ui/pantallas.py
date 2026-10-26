"""Pantallas de HU-01, HU-02, HU-08 y detalle de explicaciones."""
from __future__ import annotations
import logging
import os
from inmobiliaria.arquetipos import PESOS_POR_DEFECTO,DESCRIPCIONES
from inmobiliaria.modelos import ARQUETIPOS,ETIQUETAS,VARIABLES,Preferencia,PerfilInversor,Usuario
from inmobiliaria.ui.logica import (slider_a_peso,pesos_desde_sliders,validar_formulario,ordenar_items,formatear_precio,formatear_porcentaje,icono_para)
from inmobiliaria.catalogo import Catalogo
from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.matching import MotorMatching
from inmobiliaria.rentabilidad import EstimadorRentabilidad
from inmobiliaria.explicacion.servicio import ServicioExplicacionIA
from inmobiliaria.explicacion.plantilla import PlantillaRespaldo
from inmobiliaria.explicacion.cliente_llm import ClienteGemini
from inmobiliaria.ui.demo import ClienteDemo,cargar_demo_si_vacio
from inmobiliaria.backend import Backend
from inmobiliaria.config import db_path,top_n

logger = logging.getLogger(__name__)


def mostrar() -> None:
    import streamlit as st
    st.set_page_config(page_title='LifeMatch · Asistente inmobiliario',page_icon='🏠',layout='centered')
    st.title('🏠 LifeMatch')
    st.caption('Asistente inmobiliario inteligente según tu perfil de vida e inversión')
    for nombre,valor in {'paso':'perfil','arquetipo':'Familia con hijos','operacion':'Venta','presupuesto':250000.,'moneda':'USD','zona':'Almagro','ambientes':2,'rentabilidad_objetivo':4.,'horizonte_anios':5,'tipo_cambio':0.,'items':None}.items():
        if nombre not in st.session_state: st.session_state[nombre] = valor
    paso = st.session_state.paso
    with st.chat_message('assistant'):
        if paso=='perfil': st.write('¡Hola! ¿Para qué buscás una propiedad? Elegí el perfil que más se parece a tu situación.')
        elif paso=='datos': st.write('Contame tus condiciones indispensables. Después vamos a elegir tus prioridades.')
        elif paso=='prioridades': st.write('¿Qué valorás más? Podés ajustar cada importancia de 0 a 5.')
        elif paso=='resumen': st.write('Revisá tu perfil antes de buscar. Podés volver y editar cualquier criterio.')
        else: st.write('Estos resultados usan tus condiciones obligatorias y tus prioridades.')
    if paso=='perfil':
        for a in ARQUETIPOS:
            with st.container(border=True):
                st.markdown(f'**{a}** — {DESCRIPCIONES[a]}')
        opcion = st.radio('Elegí un perfil',ARQUETIPOS,index=ARQUETIPOS.index(st.session_state.arquetipo))
        if st.button('Continuar',type='primary'):
            st.session_state.arquetipo=opcion
            st.session_state.peso_sliders={v:round(p*5) for v,p in PESOS_POR_DEFECTO[opcion].items()}
            st.session_state.paso='datos'
            st.rerun()
    elif paso=='datos':
        inversor = st.session_state.arquetipo=='Inversor'
        with st.form('form_datos'):
            if inversor:
                st.info('Ruta inversión: compra para alquilar. La operación es siempre Venta.')
            else:
                st.selectbox('Operación',['Venta','Alquiler'],index=['Venta','Alquiler'].index(st.session_state.operacion),key='form_operacion')
            st.number_input('Capital máximo de compra (USD)' if inversor else 'Presupuesto máximo',min_value=0.,value=float(st.session_state.presupuesto),key='form_presupuesto')
            st.selectbox('Moneda',['USD','ARS'],index=['USD','ARS'].index(st.session_state.moneda),key='form_moneda')
            st.text_input('Zona (barrio o localidad)',value=st.session_state.zona,key='form_zona')
            st.number_input('Ambientes mínimos',min_value=1,max_value=15,value=int(st.session_state.ambientes),key='form_ambientes')
            if inversor:
                st.number_input('Rentabilidad bruta anual objetivo (%)',min_value=0.,value=float(st.session_state.rentabilidad_objetivo),key='form_rentabilidad')
                st.number_input('Horizonte de inversión (años)',min_value=1,value=int(st.session_state.horizonte_anios),key='form_horizonte')
                st.number_input('Tipo de cambio opcional (ARS por USD, 0 = no convertir)',min_value=0.,value=float(st.session_state.tipo_cambio),key='form_cambio')
            siguiente = st.form_submit_button('Continuar a las prioridades',type='primary')
        if siguiente:
            st.session_state.operacion='Venta' if inversor else st.session_state.form_operacion
            for origen,destino in [('form_presupuesto','presupuesto'),('form_moneda','moneda'),('form_zona','zona'),('form_ambientes','ambientes')]:
                st.session_state[destino]=st.session_state[origen]
            if inversor:
                st.session_state.rentabilidad_objetivo=st.session_state.form_rentabilidad
                st.session_state.horizonte_anios=st.session_state.form_horizonte
                st.session_state.tipo_cambio=st.session_state.form_cambio
            if st.session_state.presupuesto<=0:
                st.error('Falta indicar presupuesto para continuar.')
            elif not st.session_state.zona.strip():
                st.error('Falta indicar zona para continuar.')
            elif inversor and st.session_state.rentabilidad_objetivo<=0:
                st.error('Falta indicar rentabilidad objetivo para continuar.')
            else:
                st.session_state.paso='prioridades'
                st.rerun()
        if st.button('Volver al perfil'):
            st.session_state.paso='perfil';st.rerun()
    elif paso=='prioridades':
        variables = ['rentabilidad','precio_m2','conectividad'] if st.session_state.arquetipo=='Inversor' else ['colegio','espacios_verdes','conectividad','espacio_trabajo','silencio','accesibilidad_salud']
        with st.form('form_pesos'):
            valores = {v:st.slider(ETIQUETAS[v],0,5,int(st.session_state.peso_sliders.get(v,0))) for v in variables}
            st.caption('El peso de cada variable = su valor ÷ la suma de todos los valores.')
            sig = st.form_submit_button('Revisar búsqueda',type='primary')
        if sig:
            if not any(valores.values()): st.error('Falta indicar al menos una prioridad mayor a cero.')
            else:
                st.session_state.peso_sliders=valores
                st.session_state.paso='resumen';st.rerun()
        if st.button('Volver a las condiciones'):
            st.session_state.paso='datos';st.rerun()
    elif paso=='resumen':
        usuario,pref,perfil = _construir_busqueda(st)
        st.write(f'**Perfil:** {usuario.arquetipo}')
        st.write(f'**Objetivo:** {pref.objetivo} · **Operación:** {pref.operacion} · **Presupuesto:** {formatear_precio(pref.presupuesto,pref.moneda)}')
        st.write(f'**Zona:** {pref.zona} · **Ambientes mínimos:** {pref.ambientes}')
        if perfil: st.write(f'**Rentabilidad objetivo:** {perfil.rentabilidad_objetivo:g}% · **Horizonte:** {perfil.horizonte_anios} años')
        for v,p in pref.pesos.items(): st.write(f'- {ETIQUETAS[v]}: {p:g}')
        errores = validar_formulario(pref,perfil)
        if errores: st.warning('Corregí: '+', '.join(errores))
        if st.button('Buscar propiedades',type='primary',disabled=bool(errores)):
            repo: RepositorioSQLite | None = None
            try:
                ruta = 'data/demo.db' if os.getenv('DEMO')=='1' else db_path()
                repo = RepositorioSQLite(ruta)
                if os.getenv('DEMO')=='1': cargar_demo_si_vacio(repo)
                repo.guardar_usuario(usuario)
                pref.id_usuario = usuario.id_usuario
                repo.guardar_preferencia(pref,perfil)
                cat = Catalogo(repo)
                motor = MotorMatching(EstimadorRentabilidad(repo),cat)
                cliente = ClienteDemo(os.getenv('DEMO_LLM','ok').lower()=='falla') if os.getenv('DEMO')=='1' else ClienteGemini()
                servicio = ServicioExplicacionIA(cliente,PlantillaRespaldo())
                res = Backend(cat,motor,servicio,repo,top_n()).buscar(pref,perfil)
                st.session_state.items=res.items
                st.session_state.mensaje=res.mensaje
                st.session_state.paso='resultados'
                st.rerun()
            except Exception:
                logger.exception('Falló la búsqueda')
                st.error('No pudimos completar la búsqueda. Revisá tus datos y volvé a intentar.')
            finally:
                if repo:repo.cerrar()
        col1,col2=st.columns(2)
        with col1:
            if st.button('Editar condiciones'):st.session_state.paso='datos';st.rerun()
        with col2:
            if st.button('Editar prioridades'):st.session_state.paso='prioridades';st.rerun()
    else:
        items=st.session_state.items or []
        if not items:
            st.warning(st.session_state.get('mensaje') or 'No hay resultados.')
            if st.button('Editar criterios'):st.session_state.paso='datos';st.rerun()
        else:
            st.success(f'Encontré {len(items)} propiedades que cumplen tus condiciones.')
            orden=st.selectbox('Orden',['mayor compatibilidad','menor compatibilidad'])
            for item in ordenar_items(items,orden):
                p,m,e=item.propiedad,item.match,item.explicacion
                with st.container(border=True):
                    st.subheader(f'{icono_para(p.property_type)} {p.title}')
                    st.write(f'{p.property_type or "Propiedad"} · {p.ubicacion}')
                    st.write(f'**{formatear_precio(p.precio,p.moneda)}** · {p.ambientes} ambientes · {p.surface_covered or p.surface_total or "Sin dato"} m²')
                    st.metric('LifeMatch · índice de compatibilidad',formatear_porcentaje(m.porcentaje_compatibilidad))
                    if m.rentabilidad is not None:
                        st.markdown('**Rentabilidad bruta anual estimada (dato separado del LifeMatch)**')
                        r=m.rentabilidad
                        st.write(formatear_porcentaje(r.rentabilidad_bruta_anual) if r.disponible else 'Sin datos suficientes')
                    st.write(e.texto)
                    with st.expander('Detalle y variables del cálculo'):
                        if e.origen=='llm': st.caption('Explicación generada con inteligencia artificial')
                        for v,d in m.detalle.items():
                            st.write(f'{ETIQUETAS[v]} · aporte {formatear_porcentaje(d.aporte)}')
                            st.progress(min(1.,max(0.,d.cumplimiento)))
                            if d.cumplimiento==0:st.caption('El aviso no lo menciona; no se verificó la cercanía real.')
                        if m.variables_sin_dato: st.write('Variables sin datos suficientes: '+', '.join(ETIQUETAS[v] for v in m.variables_sin_dato))
                        if m.rentabilidad and m.rentabilidad.disponible:
                            r=m.rentabilidad
                            st.write(f'Alquiler mensual estimado: {formatear_precio(r.alquiler_mensual_est,r.moneda)}; mediana alquiler/m²: {r.mediana_alquiler_m2:.2f}; avisos comparables: {r.avisos_usados}.')
                        if m.rentabilidad: st.caption('La rentabilidad es una estimación basada en avisos de alquiler del dataset, no una garantía.')
        if st.button('Hacer otra búsqueda'): st.session_state.paso='perfil';st.rerun()
    st.divider()
    st.caption('Datos de Properati (uso académico, avisos de 2019-2020 en la muestra). La rentabilidad es una estimación.')
    with st.expander('Acerca de los datos'):
        st.write('La muestra histórica contiene precios publicados, no precios de cierre ni precios actuales. El catálogo no incluye fotos ni distancias a colegios, parques o transporte. Las menciones se extraen del título y descripción del anuncio; ausencia de mención no prueba ausencia real. Puede haber campos vacíos o inconsistentes. Las rentabilidades se estiman con alquileres comparables disponibles y no constituyen asesoramiento financiero.')


def _construir_busqueda(st: object) -> tuple[Usuario,Preferencia,PerfilInversor | None]:
    s=st.session_state
    usuario=Usuario(None,'Visitante',s.arquetipo)
    inv = s.arquetipo=='Inversor'
    pref=usuario.completar_preferencias(s.operacion,float(s.presupuesto),s.moneda,s.zona,int(s.ambientes),pesos_desde_sliders(s.peso_sliders))
    perfil=PerfilInversor(None,None,float(s.rentabilidad_objetivo),int(s.horizonte_anios),float(s.tipo_cambio) if s.tipo_cambio else None) if inv else None
    return usuario,pref,perfil
