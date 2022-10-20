import csv
import sys
from collections import defaultdict


if __name__ == "__main__":
    reader = csv.DictReader(sys.stdin)

    cluster_groups = defaultdict(list)

    for row in reader:
        cluster_groups[row["Cluster ID"]].append(row["id"])

    rows = []
    for id_list in cluster_groups.values():
        if len(id_list) == 1:
            continue
        to_id = id_list[0]
        for from_id in id_list[1:]:
            rows.append({"from": from_id, "to": to_id})

    writer = csv.DictWriter(sys.stdout, fieldnames=["from", "to"])
    writer.writeheader()
    writer.writerows(rows)
