### Examples

#### Example 1 

```yaml
subjects:
  literal: 
    - http://marineregions.org/mrgid/63523
    - http://marineregions.org/mrgid/2540
    - http://marineregions.org/mrgid/12548
prefixes:
  ex: <https://example.org/whatever/>
  mr: <http://marineregions.org/ns/ontology#>
assert-paths:
  - "mr:hasGeometry"
  - "mr:isPartOf / mr:hasGeometry"
  - "mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>"
  - "mr:isPartOf/ <https://schema.org/geo>/<https://schema.org/longitude>"
  - "mr:isPartOf/mr:hasGeometry    / <https://schema.org/latitude> /<https://schema.org/longitude>"
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
  - <https://schema.org/Dataset>
cache_lifetime: 5
```

In this example, the subjects are the results of the SPARQL query. The `assert-paths` are the property paths to follow in the results. The `cache_lifetime` is the lifetime of the cache in minutes.

### Explanation

Key | Value | Required
--- | ---
`subjects` | The subjects to dereference this can be a list of literal values or a SPARQL query | Yes
`prefixes` | The prefixes to use in the `assert-paths` | No
`assert-paths` | The property paths to test the results against. | Yes
`cache_lifetime` | The lifetime of the cache in minutes | No
