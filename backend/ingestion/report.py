from datetime import datetime


def _parse_date(value: str):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace(" ", "T", 1))
    except ValueError:
        return None
    # Google Play dates are naive, Apple's are tz-aware — drop tzinfo so the
    # two sort together. Only used for a human-readable date-range summary,
    # not for exact ordering, so losing the offset is fine here.
    return parsed.replace(tzinfo=None)


def _source_stats(rows: list[dict]) -> dict:
    total = len(rows)
    ratings = [r["rating"] for r in rows if r.get("rating") is not None]
    rating_distribution = {star: ratings.count(star) for star in range(1, 6)}

    parsed_dates = sorted(d for d in (_parse_date(r.get("date")) for r in rows) if d is not None)
    date_range = (parsed_dates[0].isoformat(), parsed_dates[-1].isoformat()) if parsed_dates else (None, None)

    lengths = [len((r.get("text") or "").split()) for r in rows]
    avg_length = round(sum(lengths) / len(lengths), 1) if lengths else 0.0

    return {
        "total": total,
        "date_range": date_range,
        "rating_distribution": rating_distribution,
        "avg_length_words": avg_length,
    }


def build_summary(product: str, rows: list[dict], drop_counts: dict, issues: list[str], merge_counts: dict) -> dict:
    by_source: dict[str, list[dict]] = {}
    for row in rows:
        by_source.setdefault(row["source"], []).append(row)

    return {
        "generated_at": datetime.now().isoformat(),
        "product": product,
        "sources": {source: _source_stats(source_rows) for source, source_rows in by_source.items()},
        "combined": _source_stats(rows),
        "drop_counts": drop_counts,
        "issues": issues,
        "merge_counts": merge_counts,
    }


def _rating_line(dist: dict) -> str:
    return " | ".join(f"{star}★: {dist.get(star, 0)}" for star in range(1, 6))


def render_markdown(summary: dict) -> str:
    lines = [
        f"# {summary['product']} review dataset",
        "",
        f"Generated {summary['generated_at']}",
        "",
        "Every row below came from a live Google Play or Apple App Store response — nothing in this "
        "dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source "
        "returned.",
        "",
        "## Since last pull",
        "",
    ]

    mc = summary["merge_counts"]
    lines += [
        f"- New reviews: **{mc['new']}**",
        f"- Edited since last seen: {mc['updated']}",
        f"- Returned again, unchanged: {mc['unchanged']}",
        f"- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's "
        f"~500-review RSS window): {mc['carried_over']}",
        "",
        "## By source",
        "",
    ]

    for source, stats in summary["sources"].items():
        start, end = stats["date_range"]
        lines += [
            f"### {source}",
            "",
            f"- Total reviews: **{stats['total']}**",
            f"- Date range: {start or 'n/a'} to {end or 'n/a'}",
            f"- Rating distribution: {_rating_line(stats['rating_distribution'])}",
            f"- Average review length: {stats['avg_length_words']} words",
            "",
        ]

    combined = summary["combined"]
    start, end = combined["date_range"]
    lines += [
        "## Combined",
        "",
        f"- Total reviews: **{combined['total']}**",
        f"- Date range: {start or 'n/a'} to {end or 'n/a'}",
        f"- Rating distribution: {_rating_line(combined['rating_distribution'])}",
        f"- Average review length: {combined['avg_length_words']} words",
        "",
        "## Filtering applied",
        "",
        f"- Dropped as empty/near-empty (<5 words): {summary['drop_counts']['dropped_empty_or_short']}",
        f"- Dropped as duplicates (same review_id + text): {summary['drop_counts']['dropped_duplicate']}",
        "- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, "
        "5-star reviews included.",
        "",
        "## Rate-limiting / access issues hit during this pull",
        "",
    ]

    if summary["issues"]:
        lines += [f"- {issue}" for issue in summary["issues"]]
    else:
        lines.append("- None.")

    lines.append("")
    return "\n".join(lines)
