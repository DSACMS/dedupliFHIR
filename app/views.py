import json
import os

import dedupe
from flask import Blueprint, redirect, request, render_template, Response
from werkzeug.utils import secure_filename

from . import base_dir
from .utils import (
    get_fhir_filename,
    get_slugs,
    prepare_patient_data,
    slugify,
    use_deduper,
)

views = Blueprint("views", __name__, url_prefix="")


@views.route("/", methods=["GET"])
def index():
    return render_template("index.html", slugs=get_slugs())


@views.route("/imports", methods=["GET", "POST"])
def imports():
    if request.method == "GET":
        # TODO: Load all existing imports
        return render_template("list.html", slugs=get_slugs())

    if request.method == "POST":
        if "upload" not in request.files:
            # TODO: Flash
            return redirect(request.url)
        upload_file = request.files["upload"]
        if not upload_file.filename.lower().endswith(".json"):
            # TODO: flash
            return redirect(request.url)
        base_filename = os.path.splitext(upload_file.filename)[0]
        slug = slugify(base_filename)
        slug_dir = os.path.join(base_dir, ".data", slug)
        os.makedirs(os.path.join(slug_dir, "fhir"))

        upload_file.save(
            os.path.join(slug_dir, "fhir", secure_filename(upload_file.filename))
        )
        upload_file.seek(0)
        patient_data = prepare_patient_data(json.load(upload_file))
        with open(os.path.join(slug_dir, "data.json"), "w") as f:
            json.dump(patient_data, f)

        return redirect(f"/imports/{slug}")


@views.route("/imports/<slug>", methods=["GET"])
def import_detail(slug):
    data_dir = os.path.join(base_dir, ".data", slug)
    data_path = os.path.join(data_dir, "data.json")
    training_path = os.path.join(data_dir, "training.json")
    with open(data_path, "r") as f:
        count_records = len(json.load(f).keys())
    if os.path.exists(training_path):
        with open(training_path, "r") as f:
            training_data = json.load(f)
            count_training = len(training_data["distinct"]) + len(
                training_data["match"]
            )
    else:
        count_training = 0
    return render_template(
        "detail.html",
        slug=slug,
        count_records=count_records,
        count_training=count_training,
    )


# Also include input/hidden textarea with full labeled pair data
# <input type="submit" name="button_1" value="Click me">
@views.route("/imports/<slug>/train", methods=["GET", "POST"])
def training(slug):
    # TODO: Why is this pulling repeats?
    with use_deduper(slug) as deduper:
        if request.method == "GET":
            # Load most recent training
            unlabeled = deduper.uncertain_pairs()
            record_pair = unlabeled.pop()
            return render_template(
                "train.html",
                pair=record_pair,
                pair_json=json.dumps(record_pair),
                slug=slug,
            )

        if request.method == "POST":
            pair_data = tuple(json.loads(request.form["data"]))
            is_match = "same" in request.form

            labeled_pairs = {"match": [], "distinct": []}
            label_key = "match" if is_match else "distinct"
            labeled_pairs[label_key].append(pair_data)
            deduper.mark_pairs(labeled_pairs)

            return redirect(f"/imports/{slug}/train")


@views.route("/imports/<slug>/preview", methods=["GET", "POST"])
def import_preview(slug):
    # TODO: Show all records that will be consolidated in HTML
    if request.method == "POST":
        with use_deduper(slug) as deduper:
            deduper.train()
            # deduper.train(recall=0.90)
            with open(
                os.path.join(base_dir, ".data", slug, "dedupe.settings"), "wb"
            ) as f:
                deduper.write_settings(f)
            return redirect(f"/imports/{slug}/preview")

    if request.method == "GET":
        with open(os.path.join(base_dir, ".data", slug, "dedupe.settings"), "rb") as f:
            deduper = dedupe.StaticDedupe(f, num_cores=4)

        with open(os.path.join(base_dir, ".data", slug, "data.json"), "r") as f:
            data = json.load(f)

        clustered_dupes = deduper.partition(data, threshold=0.5)
        record_groups = []
        for cluster, _ in clustered_dupes:
            if len(cluster) > 1:
                record_groups.append([data[i] for i in cluster])
        count_groups = len(record_groups)
        count_matches = sum([len(g) for g in record_groups])
        return render_template(
            "preview.html",
            record_groups=record_groups,
            slug=slug,
            count_groups=count_groups,
            count_matches=count_matches,
        )


@views.route("/imports/<slug>/download", methods=["GET"])
def import_download(slug):
    # TODO: abstract into separate utility function
    if not os.path.exists(os.path.join(base_dir, ".data", slug, "dedupe.settings")):
        # TODO: 404
        return

    with open(os.path.join(base_dir, ".data", slug, "dedupe.settings"), "rb") as f:
        deduper = dedupe.StaticDedupe(f, num_cores=4)

    with open(os.path.join(base_dir, ".data", slug, "data.json"), "r") as f:
        data_map = json.load(f)

    clustered_dupes = deduper.partition(data_map, threshold=0.5)
    record_groups = []
    for cluster, _ in clustered_dupes:
        if len(cluster) > 1:
            record_groups.append([data_map[i] for i in cluster])

    patient_id_map = {}
    for group in record_groups:
        to_id = group[0]["id"]
        for from_id in group[1:]:
            patient_id_map[from_id["id"]] = to_id

    with open(get_fhir_filename(slug), "r") as f:
        fhir_obj = json.load(f)

    fhir_obj["entry"] = [
        entry
        for entry in fhir_obj["entry"]
        if (
            entry["resource"]["resourceType"] != "Patient"
            or entry["resource"]["id"] not in patient_id_map
        )
    ]

    fhir_str = json.dumps(fhir_obj)
    for from_id, to_id in patient_id_map.items():
        fhir_str = fhir_str.replace(f'"Patient/{from_id}"', f'"Patient/{to_id}"')

    return Response(
        fhir_str,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={slug}-dedupe.json"},
    )
