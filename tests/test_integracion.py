from inmobiliaria.repositorio import RepositorioSQLite
from inmobiliaria.catalogo import Catalogo
from inmobiliaria.rentabilidad import EstimadorRentabilidad
from inmobiliaria.matching import MotorMatching
from inmobiliaria.backend import Backend
from inmobiliaria.explicacion.servicio import ServicioExplicacionIA
from inmobiliaria.explicacion.plantilla import PlantillaRespaldo
from inmobiliaria.ui.demo import ClienteDemo
from inmobiliaria.modelos import Usuario,PerfilInversor


def buscar(repo,arquetipo,pesos,objetivo_inversor=False):
    u=Usuario(None,'Visitante',arquetipo)
    repo.guardar_usuario(u)
    pref=u.completar_preferencias('Venta',260000,'USD','Almagro',2,pesos)
    perfil=PerfilInversor(None,None,4,5) if objetivo_inversor else None
    repo.guardar_preferencia(pref,perfil)
    cat=Catalogo(repo)
    backend=Backend(cat,MotorMatching(EstimadorRentabilidad(repo,min_avisos=5),cat),ServicioExplicacionIA(ClienteDemo(),PlantillaRespaldo(),.1),repo,top_n=5)
    return backend.buscar(pref,perfil)


def test_busqueda_completa_vivir(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    res=buscar(repo,'Familia con hijos',{'colegio':1.,'espacios_verdes':1.,'conectividad':.5})
    assert res.items and res.mensaje is None
    assert all(i.match.porcentaje_compatibilidad>=0 for i in res.items)


def test_busqueda_completa_inversor(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    res=buscar(repo,'Inversor',{'rentabilidad':.8,'precio_m2':.6,'conectividad':.2},True)
    assert res.items and all(i.match.rentabilidad is not None for i in res.items)


def test_mismo_catalogo_ranking_distinto_por_perfil(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    # Con este fixture las propiedades v1/v2 empatan en colegio y conectividad, y v3 favorece silencio.
    a=buscar(repo,'Familia con hijos',{'conectividad':1.})
    b=buscar(repo,'Profesional remoto',{'silencio':1.})
    assert [i.propiedad.id for i in a.items] != [i.propiedad.id for i in b.items]


def test_persistencia_match_rentabilidad_explicacion(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    res=buscar(repo,'Inversor',{'rentabilidad':1.},True)
    assert len(res.items)==repo.con.execute('SELECT COUNT(*) FROM "match"').fetchone()[0]
    assert len(res.items)==repo.con.execute('SELECT COUNT(*) FROM rentabilidad').fetchone()[0]
    assert len(res.items)==repo.con.execute('SELECT COUNT(*) FROM explicacion').fetchone()[0]
