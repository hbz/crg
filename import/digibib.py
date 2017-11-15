import csv
import json
import sys
import uuid
import os

def eprint(string):
    sys.stderr.write(string + "\n")

uuids = {}
def organizationFromSigel(sigel, create):
    if not sigel in uuids and create:
        uuids[sigel] = "urn:uuid" + str(uuid.uuid1())
    #else:
        #eprint("Found organization for " + sigel + ": " + uuids[sigel])
    return uuids[sigel] if sigel in uuids else None

sigel = {}
def sigelFromFachbereich(fachbereich):
    if not fachbereich in sigel:
        eprint("Fachbereich " + fachbereich + " not found")
    else:
        return sigel[fachbereich]

contactPoints = {}
def contactPointForSigel(sigel):
    uri = "urn:uuid" + str(uuid.uuid1())
    if not sigel in contactPoints:
        contactPoints[sigel] = [uri]
    else:
        contactPoints[sigel].append(uri)
    #else:
        #eprint("Found contactPoint for " + sigel + ": " + contactPoints[sigel])
    return uri if sigel in contactPoints else None

def contactPointsForSigel(sigel):
    return contactPoints[sigel] if sigel in contactPoints else []

def convert(input_path):

    # Products
    products_out = []
    digiBib = {
        "@type": "Product",
        "@id": "urn:uuid:6937062a-81ab-11e7-8a88-9faa99a64490",
        "name": "DigiBib",
        "logo": "https://www.hbz-nrw.de/service/mediathek/logos/digibib/digibib-gross"
    }
    products_out.append(digiBib)
    with open("products.json", "w") as out_file:
        json.dump(products_out, out_file, indent=2)

    # Organizations
    organizations_out = []
    with open(os.path.join(input_path, "erwerbungsdb.Teilnehmer.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        for row in servicereader:
            organization = {
                "@type": "Organization",
                "@id": organizationFromSigel(row[0].strip(), True),
                "isil": row[0].strip(),
                "name": row[2].strip(),
                "location": {
                    "@type": "Place",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": row[3].strip(),
                        "postalCode": row[4].strip(),
                        "addressLocality": row[5].strip(),
                        "addressCountry": "DE"
                    }
                },
                "url": row[8].strip(),
                "comment": row[9].strip()
            }
            if row[6].strip() != "":
                organization["address"] = {
                    "@type": "PostalAddress",
                    "postOfficeBoxNumber": row[6].strip(),
                    "postalCode": row[7].strip(),
                    "addressLocality": row[5].strip(),
                    "addressCountry": "DE"
                }
            organizations_out.append(organization)
    with open("organizations.json", "w") as out_file:
        json.dump(organizations_out, out_file, indent=2)

    # Contact points
    contactPoints_out = []
    with open(os.path.join(input_path, "digibib.Ansprechpartner.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        for row in servicereader:
            if not row[2].strip():
                eprint("Skipping contactPoint due to missing Sigel: " + str(servicereader.line_num))
                continue
            if not organizationFromSigel(row[2].strip(), False):
                eprint("Skipping contactPoint due to non-mapping Sigel: " + str(servicereader.line_num))
                continue

            contactPoint = {
                "@type": "ContactPoint",
                "@id": contactPointForSigel(row[2].strip()),
                "affiliation": [
                    {
                        "@id": organizationFromSigel(row[2].strip(), False)
                    }
                ],
                "familyName": row[3].strip(),
                "givenName": row[4].strip(),
                "telephone": row[5].strip(),
                "faxNumber": row[6].strip(),
                "email": row[7].strip(),
                "comment": row[8].strip(),
                "gender": row[9].strip()
            }
            if contactPoint["givenName"] and contactPoint["familyName"]:
                contactPoint["name"] = contactPoint["givenName"] + " " + contactPoint["familyName"]
            elif contactPoint["familyName"]:
                contactPoint["name"] = contactPoint["familyName"]
            else:
                contactPoint["name"] = contactPoint["email"]
            contactPoints_out.append(contactPoint)
    with open("contactPoints.json", "w") as out_file:
        json.dump(contactPoints_out, out_file, indent=2)

    # Map Fachbereich-ID to Sigel
    with open(os.path.join(input_path, "erwerbungsdb.Fachbereich.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        for row in servicereader:
            sigel[row[0].strip()] = row[1].strip()

    # Customer relationships
    customerRelationships_out = []
    with open(os.path.join(input_path, "digibib.TeilnehmerProdukt.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        # Ensure to process each Fachbereich_id only once
        Fachbereich_id_processed = []
        for row in servicereader:
            if row[1].strip() in Fachbereich_id_processed:
                eprint(row[1].strip() + " already processed, skipping")
                continue
            if not contactPointsForSigel(sigelFromFachbereich(row[1].strip())):
                eprint("Skipping customerRelationship due to missing contactPointForSigel: " + str(servicereader.line_num))
                continue
            if not organizationFromSigel(sigelFromFachbereich(row[1].strip()), False):
                eprint("Skipping customerRelationship due to missing organizationFromSigel: " + str(servicereader.line_num))
                continue
            customerRelationship = {
                "@type": "CustomerRelationship",
                "product": {
                    "@id": digiBib["@id"]
                },
                "customer": [
                    {
                        "@id": organizationFromSigel(sigelFromFachbereich(row[1].strip()), False)
                    }
                ]
            }
            customerRelationship["contactPoint"] = []
            for uri in contactPointsForSigel(sigelFromFachbereich(row[1].strip())):
                customerRelationship["contactPoint"].append( { "@id": uri } )
            customerRelationships_out.append(customerRelationship)
            Fachbereich_id_processed.append(row[1].strip())
    with open("customerRelationships.json", "w") as out_file:
        json.dump(customerRelationships_out, out_file, indent=2)

if __name__ == "__main__":
    convert(sys.argv[1])
