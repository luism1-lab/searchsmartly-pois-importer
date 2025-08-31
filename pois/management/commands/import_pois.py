import csv, json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Dict, Any, List
from django.core.management.base import BaseCommand, CommandError
from pois.models import PoI

def to_float(v):
   if v is None: return None
   if isinstance(v, (int, float)): return float(v)
   s = str(v).strip()
   if not s: return None
   try: return float(s)
   except ValueError: return None

def avg_rating_from(v):
   if v is None: return None
   if isinstance(v, (list, tuple)):
       nums = [to_float(x) for x in v if to_float(x) is not None]
       return sum(nums)/len(nums) if nums else None
   return to_float(v)

def parse_csv(path: Path) -> Iterable[Dict[str, Any]]:
   with path.open(encoding='utf-8', newline='') as f:
       for row in csv.DictReader(f):
           yield {
               "external_id": row.get("poi_id"),
               "name": row.get("poi_name"),
               "category": row.get("poi_category"),
               "latitude": to_float(row.get("poi_latitude")),
               "longitude": to_float(row.get("poi_longitude")),
               "avg_rating": avg_rating_from(row.get("poi_ratings")),
               "description": "",
           }

def parse_json(path: Path) -> Iterable[Dict[str, Any]]:
   with path.open(encoding='utf-8') as f:
       data = json.load(f)
   items: List[dict] = data if isinstance(data, list) else [data]
   for obj in items:
       coords = obj.get("coordinates") or []
       lat = to_float(coords[0]) if len(coords) > 0 else None
       lon = to_float(coords[1]) if len(coords) > 1 else None
       yield {
           "external_id": obj.get("id"),
           "name": obj.get("name"),
           "category": obj.get("category"),
           "latitude": lat,
           "longitude": lon,
           "avg_rating": avg_rating_from(obj.get("ratings")),
           "description": obj.get("description") or "",
       }

def parse_xml(path: Path) -> Iterable[Dict[str, Any]]:
   root = ET.parse(path).getroot()
   nodes = root.findall(".//poi") or [root]  # soporta <pois><poi/>...</pois> o un único <poi/>
   for el in nodes:
       def text(tag):
           n = el.find(tag)
           return n.text if n is not None else None
       yield {
           "external_id": text("pid"),
           "name": text("pname"),
           "category": text("pcategory"),
           "latitude": to_float(text("platitude")),
           "longitude": to_float(text("plongitude")),
           "avg_rating": avg_rating_from(text("pratings")),
           "description": "",
       }

PARSERS = {".csv": parse_csv, ".json": parse_json, ".xml": parse_xml}

class Command(BaseCommand):
   help = "Importa PoIs desde uno o más archivos (CSV, JSON, XML)."

   def add_arguments(self, parser):
       parser.add_argument("paths", nargs="+", help="Rutas a archivos")

   def handle(self, *args, **opts):
       paths = [Path(p) for p in opts["paths"]]
       if not paths:
           raise CommandError("Proporciona al menos un archivo.")
       created = updated = skipped = 0

       for path in paths:
           ext = path.suffix.lower()
           parser = PARSERS.get(ext)
           if parser is None:
               self.stderr.write(self.style.WARNING(f"Saltando {path} (extensión no soportada: {ext})"))
               continue
           if not path.exists():
               self.stderr.write(self.style.WARNING(f"Saltando {path} (no existe)"))
               continue

           self.stdout.write(self.style.NOTICE(f"Procesando {path} ..."))
           for item in parser(path):
               ext_id = (item.get("external_id") or "").strip()
               name = (item.get("name") or "").strip()
               category = (item.get("category") or "").strip()
               if not ext_id or not name or not category:
                   skipped += 1
                   continue
               obj, is_created = PoI.objects.update_or_create(
                   external_id=ext_id,
                   defaults=item
               )
               if is_created: created += 1
               else: updated += 1

       self.stdout.write(self.style.SUCCESS(
           f"Importación completa. Creados: {created}, Actualizados: {updated}, Omitidos: {skipped}."
       ))
