"""
eval_core.py — scoring, metrics, and report formatting for 2wild-model-eval.

Methodology adapted from "tool-eval-bench v2.0.1" by wolttam (credited in README).

Per-scenario scoring:
    PASS    = 2 pts  (✅)
    PARTIAL = 1 pt   (⚠️)
    FAIL    = 0 pts  (❌)

Quality Score      = (points / max_points) * 100
Responsiveness     = derived from median per-turn latency (see responsiveness_score)
Deployability      = 0.7 * Quality + 0.3 * Responsiveness
Token Efficiency   = points per 1000 total tokens
"""

import statistics

# ---- verdict constants -------------------------------------------------------

PASS = "PASS"
PARTIAL = "PARTIAL"
FAIL = "FAIL"

VERDICT_POINTS = {PASS: 2, PARTIAL: 1, FAIL: 0}
VERDICT_ICON = {PASS: "✅", PARTIAL: "⚠️", FAIL: "❌"}
MAX_POINTS_PER_SCENARIO = 2


# ---- metric formulas ---------------------------------------------------------

def responsiveness_score(median_turn_latency_ms):
    """
    Map median per-turn latency (ms) -> 0..100 responsiveness score.

    Formula (documented): a piecewise-linear curve anchored on practical
    interactive-latency expectations for a self-hosted model.

        latency <=   500 ms -> 100   (instant)
        latency >= 20000 ms ->   0   (unusable)
        in between           -> linear interpolation on a log-ish scale via
                                 100 * (1 - (latency-500)/(20000-500))

    We use a simple linear ramp between the 500ms floor and 20s ceiling so the
    score is easy to reason about and reproduce.
    """
    if median_turn_latency_ms is None:
        return 0.0
    lo, hi = 500.0, 20000.0
    if median_turn_latency_ms <= lo:
        return 100.0
    if median_turn_latency_ms >= hi:
        return 0.0
    frac = (median_turn_latency_ms - lo) / (hi - lo)
    return round(100.0 * (1.0 - frac), 1)


def stars_for_quality(quality):
    """90+=5, 80-89=4, 70-79=3, 60-69=2, <60=1."""
    if quality >= 90:
        return 5
    if quality >= 80:
        return 4
    if quality >= 70:
        return 3
    if quality >= 60:
        return 2
    return 1


def rating_label(stars):
    return {
        5: "Excellent",
        4: "Good",
        3: "Fair",
        2: "Weak",
        1: "Poor",
    }[stars]


def star_string(stars):
    return "★" * stars + "☆" * (5 - stars)


# ---- aggregate scoring -------------------------------------------------------

def summarize(scenario_results):
    """
    scenario_results: list of dicts, each with keys:
        id, category, verdict (PASS/PARTIAL/FAIL), points, reason,
        ttft_ms, turns, wall_s, prompt_tokens, completion_tokens, total_tokens,
        turn_latencies_ms (list)

    Returns an aggregate-metrics dict.
    """
    n = len(scenario_results)
    passed = sum(1 for r in scenario_results if r["verdict"] == PASS)
    partial = sum(1 for r in scenario_results if r["verdict"] == PARTIAL)
    failed = sum(1 for r in scenario_results if r["verdict"] == FAIL)

    points = sum(r["points"] for r in scenario_results)
    max_points = n * MAX_POINTS_PER_SCENARIO
    quality = round((points / max_points) * 100, 1) if max_points else 0.0

    # collect every per-turn latency across all scenarios for the median
    all_turn_latencies = []
    for r in scenario_results:
        all_turn_latencies.extend(r.get("turn_latencies_ms", []) or [])
    median_turn_latency = (
        round(statistics.median(all_turn_latencies), 1) if all_turn_latencies else None
    )
    responsiveness = responsiveness_score(median_turn_latency)

    deployability = round(0.7 * quality + 0.3 * responsiveness, 1)

    total_tokens = sum(r.get("total_tokens", 0) or 0 for r in scenario_results)
    token_efficiency = (
        round(points / (total_tokens / 1000.0), 3) if total_tokens else 0.0
    )

    stars = stars_for_quality(quality)

    return {
        "scenarios": n,
        "passed": passed,
        "partial": partial,
        "failed": failed,
        "points": points,
        "max_points": max_points,
        "quality": quality,
        "median_turn_latency_ms": median_turn_latency,
        "responsiveness": responsiveness,
        "deployability": deployability,
        "total_tokens": total_tokens,
        "token_efficiency": token_efficiency,
        "stars": stars,
        "rating": rating_label(stars),
    }


# ---- report formatting -------------------------------------------------------

def format_summary_block(agg):
    """
    ✅ 60 passed   ⚠️ 5 partial   ❌ 4 failed
    Points: 125/138
    Rating: ★★★★★ Excellent
    """
    lines = []
    lines.append(
        f"✅ {agg['passed']} passed   "
        f"⚠️ {agg['partial']} partial   "
        f"❌ {agg['failed']} failed"
    )
    lines.append(f"Points: {agg['points']}/{agg['max_points']}")
    lines.append(
        f"Rating: {star_string(agg['stars'])} {agg['rating']}"
    )
    return "\n".join(lines)


def format_scenario_log(r):
    """
    TC-01 ✅ PASS 2/2  6.4s  ttft=753ms  t2  Used get_weather with Berlin only.
    """
    icon = VERDICT_ICON[r["verdict"]]
    ttft = f"{int(r['ttft_ms'])}ms" if r.get("ttft_ms") is not None else "n/a"
    wall = f"{r['wall_s']:.1f}s"
    return (
        f"{r['id']} {icon} {r['verdict']} {r['points']}/{MAX_POINTS_PER_SCENARIO}  "
        f"{wall}  ttft={ttft}  t{r['turns']}  {r['reason']}"
    )


def format_metrics_block(agg):
    return "\n".join([
        f"Quality:        {agg['quality']:.1f} / 100",
        f"Responsiveness: {agg['responsiveness']:.1f} / 100  "
        f"(median turn latency {agg['median_turn_latency_ms']} ms)",
        f"Deployability:  {agg['deployability']:.1f}  (0.7*Quality + 0.3*Responsiveness)",
        f"Token Eff.:     {agg['token_efficiency']:.3f}  pts / 1K tokens "
        f"(total {agg['total_tokens']} tokens)",
    ])


def category_breakdown(scenario_results):
    """Return {category: {passed, partial, failed, points, max_points, quality}}."""
    cats = {}
    for r in scenario_results:
        c = cats.setdefault(r["category"], {
            "passed": 0, "partial": 0, "failed": 0, "points": 0, "n": 0,
        })
        c["n"] += 1
        c["points"] += r["points"]
        if r["verdict"] == PASS:
            c["passed"] += 1
        elif r["verdict"] == PARTIAL:
            c["partial"] += 1
        else:
            c["failed"] += 1
    for c in cats.values():
        mp = c["n"] * MAX_POINTS_PER_SCENARIO
        c["max_points"] = mp
        c["quality"] = round((c["points"] / mp) * 100, 1) if mp else 0.0
    return cats


def format_markdown_report(meta, scenario_results, agg):
    """Build the full markdown scorecard string."""
    out = []
    out.append(f"# 2Wild Model-Eval Scorecard — {meta['label']}")
    out.append("")
    out.append(f"- **Model ID:** `{meta['model']}`")
    out.append(f"- **Endpoint:** `{meta['endpoint']}`")
    out.append(f"- **Run (UTC):** {meta['utc']}")
    out.append(f"- **Scenarios:** {agg['scenarios']}")
    if meta.get("note"):
        out.append(f"- **Note:** {meta['note']}")
    out.append("")
    out.append("## Summary")
    out.append("```")
    out.append(format_summary_block(agg))
    out.append("```")
    out.append("")
    out.append("## Metrics")
    out.append("```")
    out.append(format_metrics_block(agg))
    out.append("```")
    out.append("")
    out.append("## Category breakdown")
    out.append("")
    out.append("| Category | Pass | Partial | Fail | Points | Quality |")
    out.append("|---|---|---|---|---|---|")
    cats = category_breakdown(scenario_results)
    for name in sorted(cats):
        c = cats[name]
        out.append(
            f"| {name} | {c['passed']} | {c['partial']} | {c['failed']} | "
            f"{c['points']}/{c['max_points']} | {c['quality']:.1f} |"
        )
    out.append("")
    out.append("## Per-scenario log")
    out.append("```")
    for r in scenario_results:
        out.append(format_scenario_log(r))
    out.append("```")
    out.append("")
    return "\n".join(out)
