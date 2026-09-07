# Guía de Perfilado Semántico: Dataset Real y Matchmaking (v1.3.0)

AgoraOWL organiza el perfilado simétrico en una **separación en 4 capas**, consolidada desde la v1.2.0 y sin cambios estructurales en v1.3.0:

1.  **Capa 1: Semántica (¿Qué es?):** `DataSpecification`. Define el fenómeno físico (ej. Humedad) y el sujeto (ej. Suelo). Es pura y reutilizable.
2.  **Capa 2: Puente (¿Cómo viene?):** `FieldMapping`. Une la especificación semántica con una columna física, definiendo la **Unidad**, el **Tipo de Dato** y la **Métrica de Observación**.
3.  **Capa 3: Técnica (¿Dónde está?):** `Distribution`. Contiene los metadatos del archivo (formato, resoluciones, CRS).
4.  **Capa 4: Requisitos/Ofertas (¿Cómo se pide/entrega?):** `InputProfile` y `OutputProfile`. Define los puertos de entrada y salida de las Apps.

---

## 1. El Dataset Real (Archivo CSV)

Imagina un fichero CSV llamado `monitoreo-sensores.csv` con estas columnas:

| fecha      | sensor_id | temp_c | humedad_suelo_p |
| ---------- | --------- | ------ | --------------- |
| 2026-05-10 | S-01      | 22.5   | 45.2            |
| 2026-05-10 | S-02      | 23.0   | 44.8            |

Este CSV ofrece datos sobre 2 variables semánticas:

1. **Temperatura del Aire** (`agrovoc:c_7657` + `agrovoc:c_331557`): Medido en grados Celsius.
2. **Humedad del Suelo** (`agrovoc:c_7208`): Medido en porcentaje.

---

## 2. Modelando con AgoraOWL v1.3.0 (Turtle)

### 2.1 Especificaciones Semánticas (Librería Reutilizable)

Estas definiciones se crean una vez y se reutilizan en todo el espacio de datos.

```turtle
@prefix : <https://w3id.org/AgoraOWL/> .
@prefix agrovoc: <http://aims.fao.org/aos/agrovoc/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Especificación de Humedad del Suelo
<spec/soil-moisture> a :DataSpecification ;
    rdfs:label "Especificación de Humedad del Suelo"@es ;
    :hasObservableProperty agrovoc:c_7208 ;
    :hasFeatureOfInterest agrovoc:c_7176 .  # Soil

# Especificación de Temperatura
<spec/air-temperature> a :DataSpecification ;
    rdfs:label "Especificación de Temperatura del Aire"@es ;
    :hasObservableProperty agrovoc:c_7657 ;
    :hasFeatureOfInterest agrovoc:c_331557 . # Air
```

### 2.2 El Activo y su Distribución (Supply)

Aquí es donde vinculamos la semántica con la realidad física del archivo.

```turtle
@prefix : <https://w3id.org/AgoraOWL/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix qudt: <http://qudt.org/vocab/unit/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<dataset/sensor-data-2026> a :DataAsset, dcat:Dataset ;
    dct:title "Datos de Sensores de Campo 2026"@es ;
    dcat:distribution <distribution/field-sensors-csv> .

<distribution/field-sensors-csv> a :DataRepresentation, dcat:Distribution ;
    dct:format <http://publications.europa.eu/resource/authority/file-type/CSV> ;

    # Metadatos Técnicos (Capa 3)
    dcat:temporalResolution "PT1H"^^xsd:duration ;
    :hasCRS <http://www.opengis.net/def/crs/EPSG/0/4326> ;

    # Perfil Genérico (Capa Semántica, opcional pero recomendado)
    :hasProfile [
        a :DataProfile ;
        :hasDataSpecification <spec/air-temperature> , <spec/soil-moisture>
    ] ;

    # Vinculación Específica por Campo (Capa 2): Aquí definimos unidades y mapeos
    :hasFieldMapping [
        a :FieldMapping ;
        :mapsToSpecification <spec/air-temperature> ;
        :mapsField "temp_c" ;
        :hasUnit qudt:DEG_C ;           # La unidad va en el mapeo, no en la spec
        :hasDataType xsd:float ;
        :hasObservationMetric :Instantaneous
    ] ,
    [
        a :FieldMapping ;
        :mapsToSpecification <spec/soil-moisture> ;
        :mapsField "humedad_suelo_p" ;
        :hasUnit qudt:PERCENT ;
        :hasDataType xsd:float ;
        :hasObservationMetric :DailyAverage
    ] .
```

---

## 3. Matchmaking: ¿Cómo una App pide lo que necesita?

Las aplicaciones no solo piden "Humedad", sino que pueden exigir requisitos técnicos específicos (como el `xsd:float`) mediante **Constraints**.

### 3.1 La DataApp y su perfil de entrada (Demand)

```turtle
@prefix : <https://w3id.org/AgoraOWL/> .
@prefix ids: <https://w3id.org/idsa/core/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix qudt: <http://qudt.org/vocab/unit/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<app/smart-irrigator> a :DataApp, ids:DataApp ;
    dct:title "Irrigador Inteligente v1.0"@es ;

    # Requisitos de entrada
    :hasInputProfile [
        a :InputProfile ;
        :hasDataSpecification <spec/soil-moisture> ;

        # Constraint: Mi algoritmo SOLO entiende float y medias diarias
        :hasConstraint [
            a :DataConstraint ;
            :requiresUnit qudt:PERCENT ;
            :requiresDataType xsd:float ;
            :requiresMetric :DailyAverage ;
            # v1.3.0: si además exijo un umbral de calidad, declaro qué hacer
            # cuando el candidato no publique esa evidencia (ver §3.3 más abajo).
            :constraintMetricType :Accuracy ;
            :constraintOperator :GreaterOrEqual ;
            :constraintValue "0.90"^^xsd:decimal ;
            :constraintEnforcement :Mandatory
        ]
    ] ;

    # Perfil de Salida (Symmetric Profiling)
    :hasOutputProfile [
        a :OutputProfile ;
        :hasDataSpecification <spec/irrigation-volume>
    ] .
```

### 3.2 ¿Por qué es mejor este modelo?

1.  **Flexibilidad:** Si otro Dataset tiene la humedad en una escala de 0 a 1 (unit:UNITLESS), el `FieldMapping` de ese dataset lo declarará así. La App, al ver que no coincide con su `requiresUnit: PERCENT`, sabrá que necesita una conversión previa.
2.  **Precisión:** Una App de climatología podría pedir "Temperatura" pero con la constraint `requiresMetric: DailyMax` para detectar olas de calor, descartando datasets que solo den la media.
3.  **Simplicidad en la Búsqueda:** El motor de búsqueda solo tiene que comparar URIs de `DataSpecification`. Si coinciden, luego verifica las `DataConstraint`.

---

## 3.3 Restricciones que no se pueden evaluar (v1.3.0)

El ejemplo de arriba pide `Accuracy >= 0.90`. ¿Qué pasa si el `FieldMapping`
candidato no publica ninguna `:Metric` de tipo `:Accuracy`? Hasta v1.2.1 esto no
estaba definido — de hecho, el ejemplo de referencia de la propia ontología
(`eo-instances.ttl`) caía exactamente en este caso, y dos implementaciones de
matchmaking conformes podían devolver respuestas opuestas para el mismo par.

`:constraintEnforcement` lo cierra:

- **`:Mandatory`**: si el candidato no publica evidencia para la restricción, el
  emparejamiento se **rechaza**. Úsalo cuando el umbral es un requisito real, no
  una preferencia.
- **`:Preferred`** (valor por defecto si se omite `:constraintEnforcement`): si no
  hay evidencia, el emparejamiento se **acepta**, pero el candidato debe quedar
  peor clasificado que cualquiera que sí satisfaga la restricción explícitamente.

```turtle
:hasConstraint [
    a :DataConstraint ;
    :constraintMetricType :Accuracy ;
    :constraintOperator :GreaterOrEqual ;
    :constraintValue "0.90"^^xsd:decimal ;
    :constraintEnforcement :Mandatory   # ausente = :Preferred
]
```

Y la escala importa: `:metricValue` de `:Accuracy`, `:Completeness`,
`:Uniqueness`, `:Consistency` y `:Duplication` **debe** ser un decimal en `[0,1]`.
Un conector que calcule estas cifras como porcentaje (`93` en vez de `0.93`) hace
que `93 >= 0.90` se cumpla siempre de forma silenciosa — es una fuente real de
falsos emparejamientos, y `shapes/edc-connector-shapes.ttl` lo rechaza.

---

## 4. Calidad del Dato (DQV)

Las métricas de calidad (precisión, completitud) se asocian ahora al `FieldMapping`, permitiendo saber la calidad de cada columna individualmente.

```turtle
@prefix : <https://w3id.org/AgoraOWL/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Dentro del FieldMapping de temperatura
<distribution/field-sensors-csv> :hasFieldMapping [
    a :FieldMapping ;
    :mapsToSpecification <spec/air-temperature> ;
    :mapsField "temp_c" ;
    :hasMetric [
        a :Metric ;
        :metricName "Accuracy" ;
        :metricType :Accuracy ;
        :metricValue "0.98"^^xsd:decimal ;
        prov:generatedAtTime "2026-05-11T10:00:00Z"^^xsd:dateTime
    ]
] .
```

---

## Resumen: Regla de Oro v1.3.0

- **DataSpecification:** Es el "Fenómeno Puro" (ej. Precipitación). No cambia nunca.
- **FieldMapping:** Es el "Cómo se entrega" (ej. en la columna 'rain_mm' como float en Milímetros).
- **DataConstraint:** Es el "Cómo se necesita" (ej. Necesito mm con error < 5% y tipo float).
- **Profiles:** Son los puertos de la App (Entrada/Salida).

Este desacoplamiento permite que los espacios de datos escalen sin crear diccionarios infinitos de propiedades hardcodeadas con unidades.
