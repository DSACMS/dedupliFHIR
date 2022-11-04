import csv
import json
import sys

# Example https://github.com/projecttacoma/fqm-execution/blob/4738f84b72290c2d715c902163043674213fe837/test/fixtures/EXM111-9.1.000/Armando772_Almanza534_08fc9439-b7ff-4309-b409-4d143388594c.json # noqa

if __name__ == "__main__":
    patient_fhir = json.load(sys.stdin)

    patients = []

    for entry in patient_fhir["entry"]:
        # Handle errors more gracefully here, report out?
        if entry["resource"]["resourceType"] != "Patient":
            continue
        resource = entry["resource"]
        patient = {
            "id": resource["id"],
            "family_name": resource["name"][0]["family"],
            "given_name": " ".join(resource["name"][0]["given"]),
            "gender": resource["gender"],
            "birth_date": resource["birthDate"],
            "phone": "",
            "street_address": "",
            "city": "",
            "state": "",
            "postal_code": "",
        }
        # TODO: Handle multiple phones?
        if len(resource["telecom"]) > 0:
            patient["phone"] = resource["telecom"][0]["value"]

        # TODO: multiple addresses
        if len(resource["address"]) > 0:
            patient["street_address"] = " ".join(resource["address"][0]["line"])
            patient["city"] = resource["address"][0]["city"]
            patient["state"] = resource["address"][0]["state"]
            patient["postal_code"] = resource["address"][0].get("postalCode")

        patients.append(patient)

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "id",
            "family_name",
            "given_name",
            "gender",
            "birth_date",
            "phone",
            "street_address",
            "city",
            "state",
            "postal_code",
        ],
    )

    writer.writeheader()
    writer.writerows(patients)
