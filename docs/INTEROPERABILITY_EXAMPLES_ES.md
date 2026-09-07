# Ejemplos de Interoperabilidad Semántica y Polimorfismo (v1.3.0)

Este documento ilustra cómo la arquitectura de 4 capas de AgoraOWL v1.3.0 permite que un único activo de datos sirva a múltiples aplicaciones de distintos dominios.

---

## Escenario: El Dataset "Polímata" Urban-Agri

Tenemos un fichero CSV físico (`malaga_smart_city_2026.csv`) que contiene datos de sensores instalados en una zona urbana cercana a huertos periurbanos.

**Columnas:** `[timestamp, station_id, air_temp, traffic_intensity, pollution_no2]`

Este ÚNICO activo sirve a dos tipos de aplicaciones totalmente distintas.

### 0. Especificaciones Semánticas Reutilizables

Antes de modelar el activo, definimos las variables atómicas compartidas en el espacio de datos.

```turtle
@prefix ex: <https://example.org/> .
@prefix agoraowl: <https://w3id.org/AgoraOWL/> .
@prefix agrovoc: <http://aims.fao.org/aos/agrovoc/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:SpecAirTemp a agoraowl:DataSpecification ;
    rdfs:label "Temperatura del Aire"@es ;
    agoraowl:hasObservableProperty agrovoc:c_7657 ;
    agoraowl:hasFeatureOfInterest agrovoc:c_331557 .

ex:SpecTrafficFlow a agoraowl:DataSpecification ;
    rdfs:label "Intensidad de Tráfico"@es ;
    agoraowl:hasObservableProperty <http://vocab.datex.org/terms#TrafficFlow> ;
    agoraowl:hasFeatureOfInterest <http://vocab.datex.org/terms#RoadSection> .

ex:SpecNO2Concentration a agoraowl:DataSpecification ;
    rdfs:label "Concentración de NO2"@es ;
    agoraowl:hasObservableProperty <http://purl.oclc.org/NET/ssnext/qu#NO2Concentration> ;
    agoraowl:hasFeatureOfInterest agrovoc:c_331557 .
```

### 1. El Activo y su Representación Física

```turtle
@prefix ex: <https://example.org/> .
@prefix agoraowl: <https://w3id.org/AgoraOWL/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix theme: <http://publications.europa.eu/resource/authority/data-theme/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix qudt: <http://qudt.org/vocab/unit/> .
@prefix dct: <http://purl.org/dc/terms/> .

ex:AssetUrbanAgri a agoraowl:DataAsset, dcat:Dataset ;
    dct:title "Monitoreo Urbano-Agrícola Málaga 2026" ;
    dcat:theme theme:ENVI, theme:TRAN, theme:AGRI ;
    dcat:distribution ex:DistribucionCSV .

ex:DistribucionCSV a agoraowl:DataRepresentation, dcat:Distribution ;
    dct:format <http://publications.europa.eu/resource/authority/file-type/CSV> ;

    # Perfil Genérico: Qué variables proporciona este archivo en su conjunto
    agoraowl:hasProfile [
        a agoraowl:DataProfile ;
        agoraowl:hasDataSpecification ex:SpecAirTemp, ex:SpecTrafficFlow, ex:SpecNO2Concentration
    ] ;

    # POLIMORFISMO SEMÁNTICO: Múltiples mapeos en el mismo archivo para cada columna
    agoraowl:hasFieldMapping [
        a agoraowl:FieldMapping ;
        agoraowl:mapsToSpecification ex:SpecAirTemp ;
        agoraowl:mapsField "air_temp" ;
        agoraowl:hasUnit qudt:DEG_C
    ] ,
    [
        a agoraowl:FieldMapping ;
        agoraowl:mapsToSpecification ex:SpecTrafficFlow ;
        agoraowl:mapsField "traffic_intensity" ;
        agoraowl:hasUnit qudt:VEHICLE-PER-HR
    ] ,
    [
        a agoraowl:FieldMapping ;
        agoraowl:mapsToSpecification ex:SpecNO2Concentration ;
        agoraowl:mapsField "pollution_no2" ;
        agoraowl:hasUnit qudt:MicroGM-PER-M3
    ] .
```

---

## 2. Los Consumidores (DataApps)

### Aplicación A: Optimización de Riego (SmartAgri)

A esta app solo le interesa la temperatura para calcular la evapotranspiración.

```turtle
@prefix ex: <https://example.org/> .
@prefix agoraowl: <https://w3id.org/AgoraOWL/> .
@prefix qudt: <http://qudt.org/vocab/unit/> .

ex:AppSmartIrrigation a agoraowl:DataApp ;
    agoraowl:hasInputProfile [
        a agoraowl:InputProfile ;
        agoraowl:hasDataSpecification ex:SpecAirTemp ;
        agoraowl:hasConstraint [
            a agoraowl:DataConstraint ;
            agoraowl:requiresUnit qudt:DEG_C
        ]
    ] .
```

**Resultado:** ¡MATCH! El motor encuentra que `ex:AssetUrbanAgri` tiene un mapeo a `ex:SpecAirTemp` en grados Celsius.

### Aplicación B: Gestión de Tráfico (SmartCity)

A esta app le interesa el flujo de vehículos.

```turtle
@prefix ex: <https://example.org/> .
@prefix agoraowl: <https://w3id.org/AgoraOWL/> .
@prefix qudt: <http://qudt.org/vocab/unit/> .

ex:AppTrafficControl a agoraowl:DataApp ;
    agoraowl:hasInputProfile [
        a agoraowl:InputProfile ;
        agoraowl:hasDataSpecification ex:SpecTrafficFlow ;
        agoraowl:hasConstraint [
            a agoraowl:DataConstraint ;
            agoraowl:requiresUnit qudt:VEHICLE-PER-HR
        ]
    ] .
```

**Resultado:** ¡MATCH! El MISMO activo sirve a esta aplicación mediante su segundo mapeo.

---

## 3. Beneficios de la Arquitectura v1.3.0

1.  **Sin Redundancia:** No hace falta crear perfiles específicos para cada combinación de columnas. El `FieldMapping` es granular (por columna).
2.  **Matchmaking Desacoplado:** Las aplicaciones no necesitan conocer el nombre de la columna (`air_temp` vs `temperature`). Solo buscan por la URI de la `DataSpecification`.
3.  **Seguridad en el Tipo de Dato:** Gracias a `hasUnit` y `requiresDataType` en el mapeo/constraints, la App sabe exactamente cómo parsear el valor antes de procesarlo.
4.  **Simetría**: Las Apps que producen datos declaran sus salidas con `:OutputProfile`, permitiendo el encadenamiento automático de Apps.

Este modelo permite crear un verdadero **Mercado de Datos Semántico** donde la oferta y la demanda se encuentran mediante definiciones abstractas de variables reales.
