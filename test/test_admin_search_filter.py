import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from pois.models import PoI

@pytest.fixture
def admin_client(db, client):
    User = get_user_model()
    u = User.objects.create_user(
        username="admin", password="admin123",
        is_staff=True, is_superuser=True
    )
    assert client.login(username="admin", password="admin123")
    return client

@pytest.fixture
def sample_pois(db):
    a = PoI.objects.create(external_id="EXT-1", name="Alpha", category="Cafe", latitude=1, longitude=1, avg_rating=4.2)
    b = PoI.objects.create(external_id="EXT-2", name="Beta",  category="Park", latitude=2, longitude=2, avg_rating=4.6)
    c = PoI.objects.create(external_id="EXT-3", name="Gamma", category="Cafe", latitude=3, longitude=3, avg_rating=4.0)
    return a, b, c

def _changelist(admin_client, params=None):
    url = reverse("admin:pois_poi_changelist")
    return admin_client.get(url, params or {})

@pytest.mark.django_db
def test_admin_search_by_external_id(admin_client, sample_pois):
    a, b, c = sample_pois
    resp = _changelist(admin_client, {"q": "EXT-1"})
    qs = resp.context["cl"].queryset
    assert list(qs.values_list("external_id", flat=True)) == ["EXT-1"]

@pytest.mark.django_db
def test_admin_search_by_internal_id(admin_client, sample_pois):
    a, b, c = sample_pois
    # buscar por ID interno del registro 'b'
    resp = _changelist(admin_client, {"q": str(b.id)})
    qs = resp.context["cl"].queryset
    # debe devolver exactamente ese registro
    assert qs.count() == 1 and qs.first().id == b.id

@pytest.mark.django_db
def test_admin_filter_by_category(admin_client, sample_pois):
    a, b, c = sample_pois
    # El list_filter por 'category' usa el parámetro 'category__exact'
    resp = _changelist(admin_client, {"category__exact": "Cafe"})
    qs = resp.context["cl"].queryset
    # Solo Alpha y Gamma son "Cafe"
    assert set(qs.values_list("external_id", flat=True)) == {"EXT-1", "EXT-3"}
