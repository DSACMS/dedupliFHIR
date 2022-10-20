import csv
import json
import sys


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        patient_id_map = {row["from"]: row["to"] for row in csv.DictReader(f)}

    with open(sys.argv[2], "r") as f:
        bundle_data = json.load(f)

    # First remove any patient in "entry[].resource.resourceType" = "Patient"
    # Then as string run find/replace on \"Patient/{ID}\"
    bundle_data["entry"] = [
        entry
        for entry in bundle_data["entry"]
        if (
            entry["resource"]["resourceType"] != "Patient"
            or entry["resource"]["id"] not in patient_id_map
        )
    ]

    bundle_str = json.dumps(bundle_data)
    for from_id, to_id in patient_id_map.items():
        bundle_str = bundle_str.replace(f'"Patient/{from_id}"', f'"Patient/{to_id}"')

    sys.stdout.write(bundle_str)
