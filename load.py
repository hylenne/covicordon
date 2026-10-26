import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coovicordon.settings')
django.setup()

from members.models import Member

socios = csv.DictReader(open("socios.csv", encoding="latin-1"), delimiter=";")
socios_list = []

for row in socios:
    socios_list.append(row)

for s in socios_list:
    if s["Activo"] == "Si":
        socio = Member(
            first_name=s["Nombre"],
            last_name=s["Apellido"],
            member_number=s["Nro de Socio"],
            apartment_number=s["Apto"],
            bedrooms=s["Dorm."],
        )
        socio.save()
