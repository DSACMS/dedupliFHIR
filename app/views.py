import json
import os

import dedupe
from flask import Blueprint, redirect, request, render_template
from werkzeug.utils import secure_filename

from . import base_dir
from .utils import get_slugs, prepare_patient_data, slugify, use_deduper

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
    return render_template("detail.html", slug=slug)


# Also include input/hidden textarea with full labeled pair data
# <input type="submit" name="button_1" value="Click me">
@views.route("/imports/<slug>/train", methods=["GET", "POST"])
def training(slug):
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
        return render_template("preview.html", record_groups=record_groups, slug=slug)


@views.route("/imports/<slug>/download", methods=["GET"])
def import_download(slug):
    # TODO: Run dedupe, replace patient IDs
    if not os.path.exists(base_dir, ".data", slug, "dedupe.settings"):
        return
    # deduper = dedupe.StaticDeduper
