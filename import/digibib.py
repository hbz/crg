import csv
import json
import sys
import uuid
import os

def eprint(string):
    sys.stderr.write(string + "\n")

uuids = {}
def organizationFromSigel(sigel):
    if not sigel in uuids:
        uuids[sigel] = "urn:uuid" + str(uuid.uuid1())
    else:
        eprint("Found organization for " + sigel + ": " + uuids[sigel])
    return uuids[sigel]

sigel = {}
def sigelFromFachbereich(fachbereich):
    if not fachbereich in sigel:
        eprint("Fachbereich " + fachbereich + " not found")
    else:
        return sigel[fachbereich]

contactPoints = {}
def contactPointForSigel(sigel):
    if not sigel in contactPoints:
        contactPoints[sigel] = "urn:uuid" + str(uuid.uuid1())
    else:
        eprint("Found contactPoint for " + sigel + ": " + contactPoints[sigel])
    return contactPoints[sigel]

def convert(input_path):

    digiBib = {
        "@type": "Product",
        "@id": "urn:uuid:6937062a-81ab-11e7-8a88-9faa99a64490",
        "name": "DigiBib",
        "logo": "https://www.hbz-nrw.de/service/mediathek/logos/digibib/digibib-gross"
    }

    resources = [digiBib]

    # Organizations
    with open(os.path.join(input_path, "erwerbungsdb.Teilnehmer.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        for row in servicereader:
            organization = {
                "@type": "Organization",
                "@id": organizationFromSigel(row[0]),
                "identifier": row[0],
                "name": row[2],
                "location": {
                    "@type": "Place",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": row[3],
                        "postalCode": row[4],
                        "addressLocality": row[5],
                        "addressCountry": "DE"
                    }
                },
                "url": row[8],
                "comment": row[9]
            }
            if row[6].strip() != "":
                organization["address"] = {
                    "@type": "PostalAddress",
                    "postOfficeBoxNumber": row[6],
                    "postalCode": row[7],
                    "addressLocality": row[5],
                    "addressCountry": "DE"
                }
            resources.append(organization)

    # Contact points
    with open(os.path.join(input_path, "digibib.Ansprechpartner.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        for row in servicereader:
            if row[2].strip() == "":
                eprint("Skipping due to missing Sigel")
                continue
            contactPoint = {
                "@type": "ContactPoint",
                "@id": contactPointForSigel(row[2]),
                "affiliation": [
                    {
                        "@id": organizationFromSigel(row[2])
                    }
                ],
                "familyName": row[3],
                "givenName": row[4],
                "telephone": row[5],
                "faxNumer": row[6],
                "email": row[7],
                "comment": row[8],
                "gender": row[9]
            }
            resources.append(contactPoint)

    # Map Fachbereich-ID to Sigel
    with open(os.path.join(input_path, "erwerbungsdb.Fachbereich.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        for row in servicereader:
            sigel[row[0]] = row[1]

    with open(os.path.join(input_path, "digibib.TeilnehmerProdukt.csv")) as csvfile:
        servicereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # skip the header line
        next(servicereader)
        for row in servicereader:
            customerRelationship = {
                "@type": "CustomerRelationship",
                "product": {
                    "@id": digiBib["@id"]
                },
                "contactPoint": [
                    {
                        "@id": contactPointForSigel(sigelFromFachbereich(row[1]))
                    }
                ],
                "customer": [
                    {
                        "@id": organizationFromSigel(sigelFromFachbereich(row[1]))
                    }
                ],
                "startDate": row[4],
                "endDate": row[5]
            }
            resources.append(customerRelationship)

    print json.dumps(resources, indent=2)

if __name__ == "__main__":
    convert(sys.argv[1])
