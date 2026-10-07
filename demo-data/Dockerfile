FROM mongo:4.4.6

# copy demo data (one file per collection of the "distinct" database)
COPY browsers handlers proxies reports sequence statements /demo-data/

# import demo data into the database at DISTINCT_DB (existing documents are replaced)
CMD for collection in /demo-data/*; do \
      mongoimport --uri "$DISTINCT_DB" --db distinct --collection "$(basename "$collection")" --file "$collection" --mode upsert || exit 1; \
    done
