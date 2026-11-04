"""Export selectable ADM1 boundaries only for regions with processed grid cells."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_catalog(cells, features):
    """Input: cells with admin1_id/name/country and GeoJSON features. Output: named area records."""
    from shapely import intersects_xy
    from shapely.geometry import shape
    by_id = {str(f['properties']['shapeID']): f for f in features}
    areas = []
    for (region_id, name, country), group in cells.dropna(subset=['admin1_id']).groupby(['admin1_id', 'admin1_name', 'country']):
        feature = by_id.get(str(region_id))
        if feature is None:
            raise ValueError(f'Missing source boundary for {name} ({region_id})')
        geometry = feature['geometry']
        if geometry['type'] not in {'Polygon', 'MultiPolygon'}:
            raise ValueError(f'Unsupported boundary geometry for {name}')
        if country not in {'BD', 'PB'}:
            raise ValueError(f'Unexpected coverage code: {country}')
        # Match Store.select: original boundary intersects grid centres. Some
        # assigned edge cells lie just outside that original administrative outline.
        count = int(intersects_xy(shape(geometry), cells['lon_c'].to_numpy(), cells['lat_c'].to_numpy()).sum())
        areas.append({'id': str(region_id), 'name': str(name), 'country': 'BD' if country == 'BD' else 'IN',
                      'cellCount': count, 'request': {'geometry': geometry}})
    return {'source': 'geoBoundaries ADM1; regions with cells in the processed FireSense grid', 'areas': areas}


def main():
    import pandas as pd
    cells = pd.read_parquet(ROOT / 'data/processed/cells.parquet')
    features = []
    for path in sorted((ROOT / 'data/raw/boundaries').glob('*.geojson')):
        features.extend(json.loads(path.read_text(encoding='utf-8'))['features'])
    catalog = build_catalog(cells, features)
    target = ROOT / 'ws5_frontend/public/demo/areas.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'Exported {len(catalog["areas"])} named boundaries: {target} ({target.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
