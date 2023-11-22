import brazilcep
from geopy.geocoders import Nominatim

# R. Dragão do Mar, 81 - Praia de Iracema, Fortaleza - CE, 60060-390

def request_latlong(cep):
    endereco = brazilcep.get_address_from_cep(cep)
    geolocator = Nominatim(user_agent="test_app")
    location = geolocator.geocode(endereco['logradouro'] + ", " + endereco['cidade'] + " - " + endereco['bairro'])

    return location.latitude, location.longitude