#!/usr/bin/env python3
"""
update_leaderboard.py — rebuild LEADERBOARD.md from every results/*.json file.

Headline table: ONE row per (model, cluster) group = that group's best full run,
sorted by Deployability (desc). Groups with more than one run get a collapsible
detail section listing every run; the headline Model name links to it
("click the model name to see the other evals").

Columns now include Quant / Cluster / Ctx. Each run can set these explicitly via
run_eval.py --quant/--cluster/--ctx; older runs that predate those flags get the
values inferred from the model id + label + note.

    python3 update_leaderboard.py
"""

import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")
LEADERBOARD = os.path.join(HERE, "LEADERBOARD.md")

# A "real" run covers the full gauntlet; smaller = smoke/partial (kept in details,
# never fronted as the headline).
FULL_RUN_MIN_SCENARIOS = 50


def infer_quant(model, blob):
    m = model.lower()
    if "nvfp4" in m or "nvfp4" in blob:
        return "NVFP4"
    if "autoround" in m:
        return "AutoRound-INT4"
    if "q2_k_xl" in m:
        return "UD-Q2_K_XL"
    if "iq2_m" in m:
        return "UD-IQ2_M"
    if "reap50-q3" in m or "reap50" in blob:
        return "REAP50-Q3_K_M"
    if "awq" in m or "awq" in blob:
        return "AWQ-INT4"
    if m == "deepseek-v4-flash":
        return "FP8-fusion"
    if m == "minimax-m3":
        return "NVFP4"
    return "—"


def infer_cluster(model, blob):
    m = model.lower()
    gguf = any(t in m for t in ("q2_k_xl", "iq2_m", "reap50", "gguf"))
    if "tp3" in blob or "tp=3" in blob:
        return "3× Spark TP=3"
    if "tp2" in blob or "tp=2" in blob:
        return "2× Spark TP=2"
    if "3x dgx" in blob or "3-spark" in blob or "3x spark" in blob:
        return "3× Spark PP=3 (llama.cpp)" if gguf else "3× Spark TP=3"
    if "2-spark" in blob or "2x dgx" in blob or "2x spark" in blob:
        return "2× Spark RoCE (llama.cpp)" if gguf else "2× Spark TP=2"
    if m == "deepseek-v4-flash":
        return "2× Spark TP=2"
    if m == "minimax-m3":
        return "3× Spark TP=3"
    if "autoround" in m:
        return "RTX 3090"
    return "—"


def infer_ctx(model, blob):
    m = model.lower()
    if "1m" in blob or "1mctx" in blob:
        return "1M"
    if "500k" in blob:
        return "500K"
    if "375" in blob:
        return "375K"
    if "300k" in blob:
        return "300K"
    if "230" in blob:
        return "230K"
    if "262" in blob or "autoround" in m:
        return "262K"
    if m == "minimax-m3":
        return "375K"
    if m == "deepseek-v4-flash":
        return "1M"
    return "—"


def enrich(meta):
    """Return (quant, cluster, ctx): explicit meta value if set, else inferred."""
    model = meta.get("model", "") or ""
    blob = " ".join([
        (meta.get("label", "") or ""),
        (meta.get("note", "") or ""),
        model,
    ]).lower()
    quant = meta.get("quant") or infer_quant(model, blob)
    cluster = meta.get("cluster") or infer_cluster(model, blob)
    ctx = meta.get("ctx") or infer_ctx(model, blob)
    return quant, cluster, ctx


def load_rows():
    rows = []
    for path in glob.glob(os.path.join(RESULTS_DIR, "*.json")):
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception:
            continue
        meta = data.get("meta", {})
        agg = data.get("aggregate", {})
        if not agg:
            continue
        stars = agg.get("stars", 0)
        quant, cluster, ctx = enrich(meta)
        scn = agg.get("scenarios", 0)
        rows.append({
            "label": meta.get("label", "?"),
            "model": meta.get("model", "?"),
            "quant": quant,
            "cluster": cluster,
            "ctx": ctx,
            "quality": agg.get("quality", 0.0),
            "responsiveness": agg.get("responsiveness", 0.0),
            "deployability": agg.get("deployability", 0.0),
            "token_efficiency": agg.get("token_efficiency", 0.0),
            "passed": agg.get("passed", 0),
            "partial": agg.get("partial", 0),
            "failed": agg.get("failed", 0),
            "scenarios": scn,
            "full": scn >= FULL_RUN_MIN_SCENARIOS,
            "stars": stars,
            "star_str": "★" * stars + "☆" * (5 - stars),
            "date": meta.get("utc", "")[:10],
            "file": os.path.basename(path),
        })
    return rows


def group_key(r):
    return (r["model"], r["cluster"])


def best_of(group):
    """Best run in a group: prefer full runs, then highest deployability."""
    return sorted(group, key=lambda r: (r["full"], r["deployability"]), reverse=True)[0]


def cells(r):
    pof = f"{r['passed']}/{r['partial']}/{r['failed']}"
    return (f"{r['quant']} | {r['cluster']} | {r['ctx']} "
            f"| {r['quality']:.1f} | {r['responsiveness']:.1f} | {r['deployability']:.1f} "
            f"| {r['token_efficiency']:.3f} | {pof} | {r['star_str']} | {r['date']} |")


def render(rows):
    out = []
    out.append("# 2Wild Model-Eval Leaderboard")
    out.append("")
    out.append("Auto-generated by `update_leaderboard.py` from `results/*.json`. "
               "One headline row per (model × cluster) — the group's best full run, "
               "sorted by Deployability (0.7·Quality + 0.3·Responsiveness). "
               "A `+N` link on the model name expands to every run in that group.")
    out.append("")
    if not rows:
        out.append("_No results yet. Run `run_eval.py` to add a row._")
        out.append("")
        return "\n".join(out)

    groups = {}
    for r in rows:
        groups.setdefault(group_key(r), []).append(r)

    headline = []
    for key, grp in groups.items():
        headline.append({"best": best_of(grp), "group": grp, "n": len(grp)})
    headline.sort(key=lambda h: h["best"]["deployability"], reverse=True)
    for i, h in enumerate(headline):
        h["anchor"] = f"runs-{i}" if h["n"] > 1 else None

    out.append("| Model | Quant | Cluster | Ctx | Quality | Resp. | Deploy. | Tok-Eff | ✅/⚠️/❌ | Stars | Date |")
    out.append("|---|:--:|---|--:|---:|---:|---:|---:|:--:|:--:|---|")
    for h in headline:
        b = h["best"]
        name = b["label"]
        if h["anchor"]:
            name = f"[{b['label']}](#{h['anchor']}) <sup>+{h['n'] - 1}</sup>"
        out.append(f"| {name} (`{b['model']}`) | " + cells(b))
    out.append("")

    multi = [h for h in headline if h["anchor"]]
    if multi:
        out.append("---")
        out.append("")
        out.append("## All runs (click a model name above to jump here)")
        out.append("")
        for h in multi:
            b = h["best"]
            out.append(f'<a id="{h["anchor"]}"></a>')
            out.append(f"### {b['label']} — `{b['model']}` · {b['cluster']} ({h['n']} runs)")
            out.append("")
            out.append("| Run | Quant | Cluster | Ctx | Quality | Resp. | Deploy. | Tok-Eff | ✅/⚠️/❌ | Stars | Date |")
            out.append("|---|:--:|---|--:|---:|---:|---:|---:|:--:|:--:|---|")
            for r in sorted(h["group"], key=lambda r: r["deployability"], reverse=True):
                tag = " ⭐" if r["file"] == b["file"] else ""
                out.append(f"| {r['label']}{tag} | " + cells(r))
            out.append("")
    return "\n".join(out)


def main():
    rows = load_rows()
    text = render(rows)
    with open(LEADERBOARD, "w") as f:
        f.write(text)
    groups = {}
    for r in rows:
        groups.setdefault(group_key(r), []).append(r)
    print(f"Wrote {LEADERBOARD}: {len(rows)} run(s) -> {len(groups)} headline row(s).")


if __name__ == "__main__":
    main()
