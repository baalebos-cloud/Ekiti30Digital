import argparse
import json
import re
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import shape
from shapely.ops import unary_union


DATASET_BOUNDARY_ID = "NGA-ADM2-59680162"
DATASET_YEAR = "2022"
DATASET_SOURCE = "GRID3"
DATASET_BUILD_DATE = "2023-12-12"
DATASET_COMMIT = "9469f09"
DATASET_LICENSE = "CC BY 4.0"

GEOJSON_URL = (
    "https://github.com/wmgeolab/geoBoundaries/raw/"
    "9469f09/releaseData/gbOpen/NGA/ADM2/"
    "geoBoundaries-NGA-ADM2.geojson"
)


# Exact source names and IDs in the pinned geoBoundaries dataset.
EXPECTED_SOURCE_BOUNDARIES = {
    "adoekiti": "59680162B25214275797379",
    "efon": "59680162B55690925628014",
    "ekitieast": "59680162B97170897047692",
    "ekitisouthwest": "59680162B46774046834533",
    "ekitiwest": "59680162B72061925749770",
    "emure": "59680162B54887547034560",
    "gbonyin": "59680162B53652676960042",
    "idoosi": "59680162B17555212909244",
    "ijero": "59680162B51712615582520",
    "ikere": "59680162B84830000650933",
    "ikole": "59680162B9357675593038",
    "ilejemeje": "59680162B76636581595069",
    "irepodunifelodun": "59680162B16609728895319",
    "iseorun": "59680162B94034829608504",
    "moba": "59680162B58812788921078",
    "oye": "59680162B43824241108050",
}


LGA_CONFIG = {
    "ado-ekiti": {
        "source_name": "adoekiti",
        "title": "Ado-Ekiti",
        "folder": "ado-ekiti",
    },
    "aiyekire": {
        # The pinned source dataset calls this boundary Gbonyin.
        "source_name": "gbonyin",
        "title": "Aiyekire",
        "folder": "aiyekire",
    },
    "efon": {
        "source_name": "efon",
        "title": "Efon",
        "folder": "efon",
    },
    "ekiti-east": {
        "source_name": "ekitieast",
        "title": "Ekiti East",
        "folder": "ekiti-east",
    },
    "ekiti-south-west": {
        "source_name": "ekitisouthwest",
        "title": "Ekiti South-West",
        "folder": "ekiti-south-west",
    },
    "ekiti-west": {
        "source_name": "ekitiwest",
        "title": "Ekiti West",
        "folder": "ekiti-west",
    },
    "emure": {
        "source_name": "emure",
        "title": "Emure",
        "folder": "emure",
    },
    "ido-osi": {
        "source_name": "idoosi",
        "title": "Ido/Osi",
        "folder": "ido-osi",
    },
    "ijero": {
        "source_name": "ijero",
        "title": "Ijero",
        "folder": "ijero",
    },
    "ikere": {
        "source_name": "ikere",
        "title": "Ikere",
        "folder": "ikere",
    },
    "ikole": {
        "source_name": "ikole",
        "title": "Ikole",
        "folder": "ikole",
    },
    "ilejemeje": {
        "source_name": "ilejemeje",
        "title": "Ilejemeje",
        "folder": "ilejemeje",
    },
    "irepodun-ifelodun": {
        "source_name": "irepodunifelodun",
        "title": "Irepodun/Ifelodun",
        "folder": "irepodun-ifelodun",
    },
    "ise-orun": {
        "source_name": "iseorun",
        "title": "Ise/Orun",
        "folder": "ise-orun",
    },
    "moba": {
        "source_name": "moba",
        "title": "Moba",
        "folder": "moba",
    },
    "oye": {
        "source_name": "oye",
        "title": "Oye",
        "folder": "oye",
    },
}


CANONICAL_LABELS = {
    "adoekiti": "Ado-Ekiti",
    "efon": "Efon",
    "ekitieast": "Ekiti East",
    "ekitisouthwest": "Ekiti South-West",
    "ekitiwest": "Ekiti West",
    "emure": "Emure",
    "gbonyin": "Aiyekire",
    "idoosi": "Ido/Osi",
    "ijero": "Ijero",
    "ikere": "Ikere",
    "ikole": "Ikole",
    "ilejemeje": "Ilejemeje",
    "irepodunifelodun": "Irepodun/Ifelodun",
    "iseorun": "Ise/Orun",
    "moba": "Moba",
    "oye": "Oye",
}


EKITI_SOURCE_NAMES = set(EXPECTED_SOURCE_BOUNDARIES)


def normalize(value):
    """Convert an LGA name to a simple comparison format."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def geometry_parts(geometry):
    """Return polygons contained in a Polygon or MultiPolygon."""
    if geometry.geom_type == "MultiPolygon":
        return list(geometry.geoms)

    return [geometry]


def get_feature_name(properties):
    """Read the LGA name from supported GeoJSON fields."""
    return (
        properties.get("shapeName")
        or properties.get("ADM2_NAME")
        or properties.get("admin2Name")
        or properties.get("name")
        or ""
    )


def validate_selected_boundaries(selected):
    """Verify the exact 16 expected Ekiti boundaries were selected."""
    source_names_found = {
        item["normalized_name"]
        for item in selected
    }

    missing_names = sorted(
        EKITI_SOURCE_NAMES - source_names_found
    )
    unexpected_names = sorted(
        source_names_found - EKITI_SOURCE_NAMES
    )

    if missing_names or unexpected_names:
        raise ValueError(
            "Ekiti boundary-name mismatch. "
            f"Missing: {missing_names}; "
            f"Unexpected: {unexpected_names}"
        )

    if len(selected) != 16:
        raise ValueError(
            "Expected exactly 16 Ekiti source features, "
            f"but found {len(selected)}."
        )

    shape_ids = [item["shape_id"] for item in selected]

    if None in shape_ids or "" in shape_ids:
        raise ValueError(
            "One or more selected boundaries have no shapeID."
        )

    if len(set(shape_ids)) != 16:
        raise ValueError(
            "Duplicate shapeID detected among Ekiti boundaries."
        )

    for item in selected:
        source_name = item["normalized_name"]
        actual_shape_id = item["shape_id"]
        expected_shape_id = EXPECTED_SOURCE_BOUNDARIES[
            source_name
        ]

        if actual_shape_id != expected_shape_id:
            raise ValueError(
                f"Boundary ID mismatch for {item['name']}. "
                f"Expected {expected_shape_id}, "
                f"found {actual_shape_id}."
            )


def main():
    parser = argparse.ArgumentParser(
        description="Generate an Ekiti State LGA highlight map."
    )
    parser.add_argument(
        "lga",
        choices=sorted(LGA_CONFIG),
        help="LGA folder slug",
    )
    args = parser.parse_args()
    config = LGA_CONFIG[args.lga]

    print("Using pinned geographic boundary dataset")
    print("Boundary ID:", DATASET_BOUNDARY_ID)
    print("Year represented:", DATASET_YEAR)
    print("Source:", DATASET_SOURCE)
    print("Build date:", DATASET_BUILD_DATE)
    print("Dataset commit:", DATASET_COMMIT)
    print("GeoJSON:", GEOJSON_URL)

    with urllib.request.urlopen(
        GEOJSON_URL,
        timeout=120,
    ) as response:
        data = json.load(response)

    selected = []

    for feature in data.get("features", []):
        properties = feature.get("properties", {})
        name = get_feature_name(properties)
        normalized_name = normalize(name)

        if normalized_name in EKITI_SOURCE_NAMES:
            selected.append(
                {
                    "name": name,
                    "normalized_name": normalized_name,
                    "shape_id": properties.get("shapeID"),
                    "geometry": shape(feature["geometry"]),
                }
            )

    validate_selected_boundaries(selected)

    highlighted_features = [
        item
        for item in selected
        if item["normalized_name"] == config["source_name"]
    ]

    if len(highlighted_features) != 1:
        raise ValueError(
            f"Expected exactly one boundary for "
            f"{config['title']}, but found "
            f"{len(highlighted_features)}."
        )

    highlighted_feature = highlighted_features[0]

    print("Selected source name:", highlighted_feature["name"])
    print("Selected shapeID:", highlighted_feature["shape_id"])
    print("Canonical label:", config["title"])

    state_geometry = unary_union(
        [item["geometry"] for item in selected]
    )

    fig, ax = plt.subplots(figsize=(10, 10))

    for item in selected:
        normalized_name = item["normalized_name"]
        geometry = item["geometry"]
        highlighted = normalized_name == config["source_name"]
        colour = "#15803d" if highlighted else "#d9ead3"

        for polygon in geometry_parts(geometry):
            x, y = polygon.exterior.xy
            ax.fill(
                x,
                y,
                facecolor=colour,
                edgecolor="#ffffff",
                linewidth=1.2,
                zorder=2,
            )

        point = geometry.representative_point()
        ax.text(
            point.x,
            point.y,
            CANONICAL_LABELS.get(
                normalized_name,
                item["name"],
            ),
            fontsize=7,
            ha="center",
            va="center",
            color="#111827",
            zorder=3,
        )

    for polygon in geometry_parts(state_geometry):
        x, y = polygon.exterior.xy
        ax.plot(
            x,
            y,
            color="#14532d",
            linewidth=2.2,
            zorder=4,
        )

    title = config["title"]
    ax.set_title(
        "Ekiti State Local Government Areas\n"
        f"{title} LGA Highlighted",
        fontsize=16,
        fontweight="bold",
        pad=18,
    )

    ax.legend(
        handles=[
            Patch(
                facecolor="#15803d",
                edgecolor="#14532d",
                label=f"{title} LGA",
            ),
            Patch(
                facecolor="#d9ead3",
                edgecolor="#14532d",
                label="Other Ekiti LGAs",
            ),
        ],
        loc="lower left",
        frameon=True,
    )

    ax.text(
        0.5,
        -0.04,
        "Boundary data: geoBoundaries NGA ADM2 "
        "(NGA-ADM2-59680162, 2022, GRID3, "
        "CC BY 4.0).",
        transform=ax.transAxes,
        ha="center",
        fontsize=7,
        color="#4b5563",
    )

    ax.set_aspect("equal")
    ax.axis("off")

    repository_root = Path(__file__).resolve().parents[2]
    output_directory = (
        repository_root
        / "02_LGAs"
        / "media"
        / config["folder"]
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    output_path = output_directory / (
        f"{args.lga}-lga-highlight-map-01.png"
    )

    absolute_output_path = output_path.resolve()
    temporary_output_path = absolute_output_path.with_name(
        f"{absolute_output_path.stem}.tmp.png"
    )

    fig.tight_layout()
    fig.savefig(
        str(temporary_output_path),
        format="png",
        dpi=180,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)

    try:
        temporary_output_path.replace(absolute_output_path)
    except OSError as error:
        raise OSError(
            "Could not replace the existing map image. "
            "Close the image in Photos or another program, "
            "then run the command again."
        ) from error

    print("Map generated successfully")
    print("LGA:", title)
    print("Output:", absolute_output_path)


if __name__ == "__main__":
    main()
