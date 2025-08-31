import json
import pytest
from django.core.management import call_command
from pois.models import PoI

@pytest.mark.django_db
def test_import_json(tmp_path):
    data = [
        {
            "id": "J-1",
            "name": "JSON Place",
            "coordinates": [10.5, -20.25],
            "category": "Cafe",
            "ratings": [5, 4, 5],
            "description": "from json"
        },
        {
            "id": "J-2",
            "name": "JSON Park",
            "coordinates": [0.0, 0.0],
            "category": "Park",
            "ratings": 4.6
        }
    ]
    jf = tmp_path / "data.json"
    jf.write_text(json.dumps(data), encoding="utf-8")

    call_command("import_pois", str(jf))

    p1 = PoI.objects.get(external_id="J-1")
    assert p1.name == "JSON Place"
    # promedio de [5,4,5] = 4.6666...
    assert abs(p1.avg_rating - (14/3)) < 1e-6
    assert p1.latitude == 10.5 and p1.longitude == -20.25
    assert p1.category == "Cafe"

    p2 = PoI.objects.get(external_id="J-2")
    assert p2.avg_rating == pytest.approx(4.6)

@pytest.mark.django_db
def test_import_xml(tmp_path):
    xml = """
    <pois>
      <poi>
        <pid>X-1</pid>
        <pname>XML Museum</pname>
        <platitude>48.86</platitude>
        <plongitude>2.35</plongitude>
        <pcategory>Museum</pcategory>
        <pratings>4.7</pratings>
      </poi>
      <poi>
        <pid>X-2</pid>
        <pname>XML Library</pname>
        <platitude></platitude>
        <plongitude>N/A</plongitude>
        <pcategory>Library</pcategory>
        <pratings></pratings>
      </poi>
    </pois>
    """.strip()
    xf = tmp_path / "data.xml"
    xf.write_text(xml, encoding="utf-8")

    call_command("import_pois", str(xf))

    m = PoI.objects.get(external_id="X-1")
    assert m.name == "XML Museum"
    assert m.category == "Museum"
    assert m.latitude == pytest.approx(48.86)
    assert m.longitude == pytest.approx(2.35)
    assert m.avg_rating == pytest.approx(4.7)

    l = PoI.objects.get(external_id="X-2")
    assert l.name == "XML Library"
    assert l.latitude is None and l.longitude is None
    assert l.avg_rating is None

@pytest.mark.django_db
def test_idempotency_and_update(tmp_path):
    # primer CSV crea el registro
    csv1 = (
        "poi_id,poi_name,poi_latitude,poi_longitude,poi_category,poi_ratings\n"
        "IDEMP-1,Original,1.0,2.0,Cafe,4.0\n"
    )
    c1 = tmp_path / "a.csv"
    c1.write_text(csv1, encoding="utf-8")
    call_command("import_pois", str(c1))
    assert PoI.objects.count() == 1
    p = PoI.objects.get(external_id="IDEMP-1")
    assert p.name == "Original"
    assert p.avg_rating == pytest.approx(4.0)

    # segundo JSON con el MISMO external_id debe ACTUALIZAR, no crear otro
    j = [{
        "id": "IDEMP-1",
        "name": "Updated",
        "coordinates": [5, 6],
        "category": "Cafe",
        "ratings": [5, 5, 4]
    }]
    jf = tmp_path / "b.json"
    jf.write_text(json.dumps(j), encoding="utf-8")
    call_command("import_pois", str(jf))

    assert PoI.objects.count() == 1  # no duplica
    p = PoI.objects.get(external_id="IDEMP-1")
    assert p.name == "Updated"
    assert p.latitude == 5 and p.longitude == 6
    assert p.avg_rating == pytest.approx(14/3)  # 4.666...