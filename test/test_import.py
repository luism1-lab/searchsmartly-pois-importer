import os
import pytest
from django.core.management import call_command
from pois.models import PoI

@pytest.mark.django_db
def test_import_csv(tmp_path):
    # Crear un CSV temporal
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "poi_id,poi_name,poi_latitude,poi_longitude,poi_category,poi_ratings\n"
        "T-1,Test Place,10.0,20.0,Cafe,4.5\n",
        encoding="utf-8"
    )

    # Llamar al comando
    call_command("import_pois", str(csv_file))

    # Verificar que se creó en DB
    poi = PoI.objects.get(external_id="T-1")
    assert poi.name == "Test Place"
    assert poi.category == "Cafe"
    assert abs(poi.avg_rating - 4.5) < 0.01