import pandas as pd
import pytest
from scripts.export_area_catalog import build_catalog


def test_catalog_uses_only_loaded_regions_and_preserves_source_geometry():
    cells = pd.DataFrame({'admin1_id': ['one', 'one'], 'admin1_name': ['Example', 'Example'], 'country': ['BD', 'BD'],
                          'lon_c': [88.5, 88.75], 'lat_c': [23.25, 23.25]})
    geometry = {'type': 'MultiPolygon', 'coordinates': [[[[88, 23], [89, 23], [89, 24], [88, 23]]]]}
    features = [{'properties': {'shapeID': 'one'}, 'geometry': geometry},
                {'properties': {'shapeID': 'unused'}, 'geometry': geometry}]
    result = build_catalog(cells, features)['areas']
    assert len(result) == 1
    assert result[0]['id'] == 'one' and result[0]['cellCount'] == 2
    assert result[0]['request']['geometry'] == geometry
    with pytest.raises(ValueError, match='Missing source boundary'):
        build_catalog(cells, [])
