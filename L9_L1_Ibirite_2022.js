// 1. Área de interesse em UTM (EPSG:31983 – SIRGAS 2000 Zona 23S)
var aoi = ee.Geometry.Rectangle(
  [578524, 7774048, 609237, 7800187],
  ee.Projection('EPSG:31983'),
  false
);

// 2. Coleção Landsat-9 C02 Tier 1 (Level-1 radiância DN)
var collection = ee.ImageCollection('LANDSAT/LC09/C02/T1')
  .filterDate('2022-01-01', '2022-12-31')
  .filterBounds(aoi)
  .filter(ee.Filter.lt('CLOUD_COVER', 10));

// 3. Seleciona a cena com menor cobertura de nuvens
var image = collection.sort('CLOUD_COVER').first();

// 4. Bandas desejadas (B1-B7, B9 – omitindo B8 pancro e TIR)
var bandas = ['B1','B2','B3','B4','B5','B6','B7','B9'];
var imageBands = image.select(bandas);

// 5. Projeção alvo (SIRGAS 2000 / UTM 23 S)
var proj = 'EPSG:31983';

// 6. Recorte + reprojeção
var bandsClipped = imageBands.clip(aoi).reproject({crs: proj, scale: 30});

// 7. Data formatada
var formattedDate = ee.Date(image.get('system:time_start'))
                     .format('yyyyMMdd')
                     .getInfo();

// 8. Exporta cada banda individualmente
bandas.forEach(function(band){
  Export.image.toDrive({
    image: bandsClipped.select(band),
    description: 'L9_' + band + '_Ibirite_' + formattedDate,
    folder: 'GEE_Exports',
    fileNamePrefix: 'L9_' + band + '_Ibirite_' + formattedDate,
    region: aoi,
    scale: 30,
    crs: proj,
    maxPixels: 1e13
  });
});
