from inmobiliaria.rentabilidad import EstimadorRentabilidad
from inmobiliaria.catalogo import Catalogo
from inmobiliaria.modelos import PerfilInversor


def test_rentabilidad_formula(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    prop=repo.consultar_propiedades(__import__('inmobiliaria.modelos',fromlist=['Preferencia']).Preferencia(None,None,'vivir','Venta',260000,'USD','Almagro',2,{'colegio':1}))[0]
    r=EstimadorRentabilidad(repo,min_avisos=5).estimar(prop)
    assert r.disponible and abs(r.rentabilidad_bruta_anual-(550/60*60*12/150000*100))<.0001


def test_rentabilidad_sin_suficientes_avisos_es_sin_dato(repo,csv_sintetico,propiedad):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    renta=EstimadorRentabilidad(repo,min_avisos=6).estimar(propiedad)
    assert renta.disponible is False and renta.avisos_usados==5


def test_rentabilidad_ignora_monedas_distintas_sin_tipo_cambio(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    assert EstimadorRentabilidad(repo,min_avisos=1).mediana_alquiler_m2('Almagro','Departamento','ARS')[1]==0


def test_rentabilidad_con_tipo_cambio(repo,csv_sintetico):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    mediana,cantidad=EstimadorRentabilidad(repo,min_avisos=5).mediana_alquiler_m2('Almagro','Departamento','ARS',1000)
    assert cantidad==5 and abs(mediana-(550*1000/60))<1e-8


def test_mediana_precio_m2(repo,csv_sintetico,monkeypatch):
    Catalogo(repo).cargar_csv(str(csv_sintetico))
    monkeypatch.setenv('MIN_AVISOS_ALQUILER','2')
    assert Catalogo(repo).mediana_precio_m2('Almagro','Departamento','USD') is not None
