from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402


@dataclass
class EngRunArtifacts:
    overlay_image_uri: str
    metrics_csv_uri: str
    metrics_json_uri: str
    manifest_uri: str
    dip_columns: List[int]


def process_bscan(
    run_id: str,
    input_image_path: str,
    output_dir: str,
    model_name: str,
    model_version: Optional[str],
    confidence_threshold: float,
) -> EngRunArtifacts:
    """
    Deterministic AO-OCT B-scan processing pipeline.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(input_image_path).convert("L")
    arr = np.asarray(image, dtype=np.float32) / 255.0
    height, width = arr.shape

    seg_map = np.zeros((height, width), dtype=np.uint8)
    seg_map[arr > 0.2] = 1
    seg_map[arr > 0.7] = 2

    num_classes = 3
    probs = np.full((height, width, num_classes), 0.05, dtype=np.float32)
    for c in range(num_classes):
        probs[seg_map == c, c] = 0.9

    confidence = np.zeros(width, dtype=np.float32)
    uncertainty = np.ones(width, dtype=np.float32)
    for x in range(width):
        mask = seg_map[:, x] > 0
        if not np.any(mask):
            confidence[x] = 0.0
            uncertainty[x] = 1.0
            continue
        col_probs = probs[:, x, 1][mask]
        pmax = float(col_probs.max())
        confidence[x] = pmax
        uncertainty[x] = 1.0 - pmax

    dip_indices = [int(i) for i in np.where(confidence < confidence_threshold)[0]]

    fig, (ax_img, ax_curve) = plt.subplots(
        2,
        1,
        figsize=(8, 6),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )
    ax_img.imshow(arr, cmap="gray", aspect="auto")
    ax_img.imshow(seg_map, cmap="jet", alpha=0.4, aspect="auto")
    ax_img.set_title("AO-OCT B-scan with segmentation-like overlay")
    ax_img.axis("off")

    xs = np.arange(width)
    ax_curve.plot(xs, confidence, label="confidence (max P_retina)")
    ax_curve.plot(xs, uncertainty, label="uncertainty (1 - confidence)")
    ax_curve.axhline(confidence_threshold, color="red", linestyle="--", label="threshold")
    for idx in dip_indices:
        ax_curve.axvline(idx, color="red", alpha=0.2)
    ax_curve.set_ylim(0.0, 1.05)
    ax_curve.set_xlabel("A-scan index (x)")
    ax_curve.set_ylabel("Score")
    ax_curve.legend(loc="upper right")
    ax_curve.grid(True, alpha=0.3)

    fig.tight_layout()
    overlay_path = out_dir / "overlay.png"
    fig.savefig(overlay_path, dpi=150)
    plt.close(fig)

    csv_path = out_dir / "column_metrics.csv"
    json_path = out_dir / "column_metrics.json"
    records = []
    for idx in range(width):
        rec = {
            "x_index": idx,
            "max_prob": float(confidence[idx]),
            "uncertainty": float(uncertainty[idx]),
            "dip_flag": bool(idx in dip_indices),
        }
        records.append(rec)

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["x_index", "max_prob", "uncertainty", "dip_flag"],
        )
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

    with json_path.open("w") as f:
        json.dump(records, f, indent=2)

    manifest_path = out_dir / "manifest.json"
    manifest = {
        "run_id": run_id,
        "model_name": model_name,
        "model_version": model_version,
        "confidence_threshold": confidence_threshold,
        "input_image_path": input_image_path,
        "overlay_image_uri": str(overlay_path),
        "metrics_csv_uri": str(csv_path),
        "metrics_json_uri": str(json_path),
        "dip_columns": dip_indices,
        "dip_count": len(dip_indices),
    }
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)

    return EngRunArtifacts(
        overlay_image_uri=str(overlay_path),
        metrics_csv_uri=str(csv_path),
        metrics_json_uri=str(json_path),
        manifest_uri=str(manifest_path),
        dip_columns=dip_indices,
    )

