### Example

```yaml
SPARQL: >
  PREFIX dc: <http://purl.org/dc/terms/> 
  SELECT ?o
  WHERE {
    ?s dc:isVersionOf ?o .
      FILTER regex(str(?o), "marineregions.org")
  }
property_paths:
  - http://marineregions.org/ns/ontology#hasGeometry
  - http://marineregions.org/ns/ontology#isPartOf:
    - http://marineregions.org/ns/ontology#hasGeometry
    - https://schema.org/geo:
      - https://schema.org/latitude
      - https://schema.org/longitude
cache_lifetime: 3600
```

### Explanation

Key | Value
--- | ---
`query` | The SPARQL query to execute
`property_paths` | The property paths to follow in the results
`cache_lifetime` | The lifetime of the cache in minutes
