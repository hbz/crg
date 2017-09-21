#!/usr/bin/env bash

curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @digibib-product.json
curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @digitale-inhalte-product.json
curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @rwth-business-partner.json
curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @DE-82-customer.json
curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @cp01.json
curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @cp02.json
curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @customer-relationship-01.json
curl -i -H "Content-type: application/json" http://localhost:9000/resource/ -d @customer-relationship-02.json
