### Examples

#### Example 1 

```yaml
subjects:
  literal: 
    - http://marineregions.org/mrgid/63523
    - http://marineregions.org/mrgid/2540
    - http://marineregions.org/mrgid/12548
assert-paths:
  - http://marineregions.org/ns/ontology#hasGeometry
  - http://marineregions.org/ns/ontology#isPartOf:
    - http://marineregions.org/ns/ontology#hasGeometry
    - https://schema.org/geo:
      - https://schema.org/latitude
      - https://schema.org/longitude
cache_lifetime: 18000
```

In this example, the subjects are the literal values of the URIs. The `assert-paths` are the property paths to follow in the results. The `cache_lifetime` is the lifetime of the cache in minutes.

#### Example 2

```yaml
subjects:
  SPARQL: >
    select DISTINCT ?s where { 
      ?s ?p ?o .
        FILTER regex(str(?s), "^http://marineregions.org/mrgid/[0-9]{1,5}$")
    }
assert-paths:
  - http://marineregions.org/ns/ontology#isPartOf
cache_lifetime: 5
```

In this example, the subjects are the results of the SPARQL query. The `assert-paths` are the property paths to follow in the results. The `cache_lifetime` is the lifetime of the cache in minutes.

### Explanation

Key | Value
--- | ---
`subjects` | The subjects to dereference this can be a list of literal values or a SPARQL query
`assert-paths` | The property paths to test the results against.
`cache_lifetime` | The lifetime of the cache in minutes
