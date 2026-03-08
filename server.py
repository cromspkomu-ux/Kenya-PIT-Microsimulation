# server.py
import os
import csv
import json
import traceback
from flask import Flask, jsonify, request, send_from_directory

# ------------------ Configuration (adjust to your paths) ------------------
BASE_DIR = "C:/Users/ssj34/Documents/OneDrive/python_latest/Microsimulation/Kenya-Tax-Microsimulation"
# ensure no trailing slash differences
BASE_DIR = os.path.normpath(BASE_DIR)
WEB_DIR = os.path.join(BASE_DIR, "web")   # UI files (index.html, policy.html, policy.js, etc.)
POLICY_JSON_PATH = os.path.join(BASE_DIR, "taxcalc", "current_law_policy_pit_training.json")
REFORM_PATH = os.path.join(BASE_DIR, "reform.json")
OUT_CSV = os.path.join(BASE_DIR, "pit_revenue_projection.csv")

# Make the process working directory the project folder so relative reads in the generator work
try:
    os.chdir(BASE_DIR)
except Exception as e:
    print("Warning: failed to chdir to BASE_DIR:", BASE_DIR, "error:", e)

# Flask app (serve the static UI directly)
app = Flask(__name__, template_folder=WEB_DIR, static_folder=None)

# Note: DO NOT import generate_policy_revenues at module import time.
# Many of its operations expect files to exist and run code on import.
# We'll import it lazily inside the endpoints that call it.

# ------------------ Helpers ------------------
def load_policy_json():
    """Load current law policy JSON used to populate dropdown options."""
    if not os.path.exists(POLICY_JSON_PATH):
        raise FileNotFoundError(f"Policy JSON not found at: {POLICY_JSON_PATH}")
    with open(POLICY_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def policy_option_list():
    pj = load_policy_json()
    keys = sorted(pj.keys())
    out = []
    for k in keys:
        if k.endswith("curr_law"):
            continue
        if k.startswith("_elasticity") or ("elasticity" in k and k.startswith("_")):
            continue
        display = k[1:] if k.startswith("_") else k
        out.append(display)
    return out

# ------------------ Routes ------------------
@app.route("/")
def index():
    """Serve the UI page."""
    return send_from_directory(WEB_DIR, "index.html")

# Serve tab partials and JS from web/ (UI files are directly in the web folder)
@app.route("/web/<path:fname>")
def serve_tab_file(fname):
    return send_from_directory(WEB_DIR, fname)

@app.route("/policy_options", methods=["GET"])
def get_policy_options():
    try:
        pj = load_policy_json()
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"status":"error","message":str(e),"trace":tb}), 500

    opts = {}
    for raw_key, spec in pj.items():
        if raw_key.endswith("curr_law"):
            continue
        if raw_key.startswith("_elasticity") or (raw_key.startswith("_") and "elasticity" in raw_key):
            continue
        display_key = raw_key[1:] if raw_key.startswith("_") else raw_key
        row_label = spec.get("row_label", None)
        if not row_label or len(row_label) == 0:
            sy = spec.get("start_year", None)
            row_label = [str(sy)] if sy is not None else []
        val = spec.get("value", None)
        default_value = None
        if isinstance(val, list) and len(val) > 0:
            default_value = val[0]
        else:
            default_value = val
        opts[display_key] = {"row_label": [str(x) for x in row_label], "value": default_value}
    return jsonify({"status":"ok","options":opts})

@app.route("/run_reform", methods=["POST"])
def run_reform():
    """
    Accepts JSON: { "changes": [ { "param": "rate2", "years": ["2022"], "values": ["0.18"] }, ... ] }
    Builds the reform dict, writes reform.json, lazy-imports generate_policy_revenues,
    runs it, and returns the generated CSV rows.
    """
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"status":"error","message":"Invalid JSON payload","detail":str(e)}), 400

    changes = payload.get("changes", [])
    if not isinstance(changes, list):
        return jsonify({"status":"error","message":"'changes' must be a list"}), 400

    block_selected_dict = {}
    for i, ch in enumerate(changes, start=1):
        param = ch.get("param")
        years = ch.get("years", [])
        values = ch.get("values", [])
        if (not param) or (not isinstance(years, list)) or (not isinstance(values, list)):
            continue
        block_selected_dict[str(i)] = {
            "selected_item": param,
            "selected_year": [str(y) for y in years],
            "selected_value": [v for v in values]
        }

    # write reform.json (generator reads this file directly)
    try:
        with open(REFORM_PATH, "w", encoding="utf-8") as f:
            json.dump(block_selected_dict, f, indent=2)
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"status":"error","message":"Failed to write reform.json","trace":tb}), 500

    # Lazy import the generator so server can start even if module import would fail.
    try:
        import generate_policy_revenues as gpr_module
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"status":"error", "message": "generate_policy_revenues import error: " + str(e), "trace": tb}), 500

    # Call the generator
    try:
        gpr_module.generate_policy_revenues()
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"status":"error","message":"Exception in generate_policy_revenues","trace":tb}), 500

    # Read and return CSV
    if not os.path.exists(OUT_CSV):
        return jsonify({"status":"error","message":"Expected output CSV not found","files":os.listdir(BASE_DIR)}), 500

    rows = []
    try:
        with open(OUT_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"status":"error","message":"Failed to read output CSV","trace":tb}), 500

    return jsonify({"status":"ok","rows":rows})

@app.route("/run", methods=["POST"])
def run_policy():
    # lazy import for the same reason as above
    try:
        import generate_policy_revenues as gpr_module
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"status":"error", "message": "generate_policy_revenues import error: " + str(e), "trace": tb}), 500

    try:
        gpr_module.generate_policy_revenues()
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"status":"error","message":f"Exception while running generate_policy_revenues(): {e}","trace":tb}), 500

    if not os.path.exists(OUT_CSV):
        files = os.listdir(BASE_DIR)
        return jsonify({"status":"error","message":"Expected output file pit_revenue_projection.csv not found after run.","files_in_dir":files}), 500

    rows = []
    with open(OUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return jsonify({"status":"ok","rows":rows})

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
