import csv
from inmobiliaria.catalogo import Catalogo,COLUMNAS
from inmobiliaria.modelos import Preferencia


def test_carga_deja_esquema_consistente(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico),lote=2)
    assert repo.con.execute('SELECT COUNT(*) FROM propiedad').fetchone()[0]==8
    assert repo.con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='caracteristica'").fetchone()[0]==1


def test_descarta_registros_invalidos_sin_cortar_la_carga(repo,csv_sintetico):
    resumen=Catalogo(repo).cargar_csv(str(csv_sintetico))
    assert (resumen.leidos,resumen.validos,resumen.descartados)==(9,8,1)


def test_completa_precio_m2_con_surface_total(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    assert repo.con.execute("SELECT precio_m2 FROM propiedad WHERE id='v2'").fetchone()[0]==180000/70


def test_corrige_lat_lon_invertidas(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    lat,lon=repo.con.execute("SELECT lat,lon FROM propiedad WHERE id='v1'").fetchone()
    assert (lat,lon)==(-34.6,-58.4)


def test_repara_texto_danado(repo):
    base=dict.fromkeys(COLUMNAS,'')
    base.update(id='a',price='100000',currency='USD',operation_type='Venta',l3='Almagro',rooms='2',title='BalcÃ³n')
    assert Catalogo(repo).normalizar_datos(base).title=='Balcón'


def test_lee_formato_fila_entre_comillas(repo,tmp_path):
    ruta=tmp_path/'envuelto.csv'
    valores=dict.fromkeys(COLUMNAS,'')
    valores.update(id='envuelto',price='100000',currency='USD',operation_type='Venta',l3='Almagro',rooms='2',title='Lindo depto')
    import io
    buffer=io.StringIO(newline='')
    writer=csv.writer(buffer)
    writer.writerow(COLUMNAS)
    writer.writerow([valores[k] for k in COLUMNAS])
    normal=buffer.getvalue().splitlines()
    # Línea CSV completa codificada como único campo (comillas duplicadas):
    con_envuelto = normal[0] + '\n' + '"' + normal[1].replace('"','""') + '"\n'
    ruta.write_text(con_envuelto,encoding='utf-8-sig')
    assert Catalogo(repo).cargar_csv(str(ruta)).validos==1


def test_carga_venta_y_alquiler(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    assert set(r[0] for r in repo.con.execute('SELECT DISTINCT operation_type FROM propiedad'))=={'Venta','Alquiler'}


def test_carga_idempotente(repo,csv_sintetico):
    cat=Catalogo(repo)
    cat.cargar_csv(str(csv_sintetico));cat.cargar_csv(str(csv_sintetico))
    assert repo.con.execute('SELECT COUNT(*) FROM propiedad').fetchone()[0]==8


def test_resumen_de_carga(repo,csv_sintetico):
    resumen=Catalogo(repo).cargar_csv(str(csv_sintetico))
    assert resumen.completados >= 1


def test_caracteristicas_por_palabras_clave(repo):
    base=dict.fromkeys(COLUMNAS,'')
    base.update(id='a',price='100000',currency='USD',operation_type='Venta',l3='Almagro',rooms='2',title='Frente al parque Centenario',description='Con subte')
    p=Catalogo(repo).normalizar_datos(base)
    assert p.caracteristicas['espacios_verdes']==1. and p.caracteristicas['conectividad']==1.
    assert p.caracteristicas['colegio']==0.


def test_lee_formato_envuelto_con_descripcion_multilinea(repo,tmp_path):
    import io
    ruta = tmp_path/'multilinea.csv'
    datos = dict.fromkeys(COLUMNAS,'')
    datos.update(id='m1',price='90000',currency='USD',operation_type='Venta',l3='Almagro',rooms='2',description='Patio, colegio\nY también subte cerca')
    b = io.StringIO(newline='')
    writer=csv.writer(b)
    writer.writerow(COLUMNAS)
    writer.writerow([datos[c] for c in COLUMNAS])
    cabecera, linea = b.getvalue().split('\n',1)
    ruta.write_text(cabecera+'\n'+ '"'+linea.rstrip('\r\n').replace('"','""')+'"\n',encoding='utf-8')
    resumen = Catalogo(repo).cargar_csv(str(ruta))
    assert resumen.validos==1 and repo.con.execute("SELECT description FROM propiedad WHERE id='m1'").fetchone()[0].count('\n')==1
