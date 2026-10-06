"""Unit tests for evals/checks.py -- the checkers must be trustworthy before
their verdicts on the Assistant mean anything. Free (no model calls).

Run with: python -m pytest evals/test_checks.py   (from backend/)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from evals import checks as c


def _claims(text):
    return sorted((cl.value, cl.decimals) for cl in c.extract_claims(text))


# ---- claim extraction ----

def test_percentages_and_deltas():
    assert _claims("Rose from 6.1% to 12.6% (+6.5pp).") == [(6.1, 1), (6.5, 1), (12.6, 1)]

def test_unicode_minus_and_spaced_pp():
    assert _claims("down −5.4 pp") == [(5.4, 1)]

def test_ratio_and_point_swing():
    assert _claims("a 2.1x rise, a 29-point swing") == [(2.1, 1), (29.0, 0)]

def test_range_yields_both_ends():
    assert _claims("holding around 20–28%") == [(20.0, 0), (28.0, 0)]

def test_counts_with_commas():
    assert _claims("126 mentions across 3,591 reviews") == [(126.0, 0), (3591.0, 0)]

def test_non_statistics_are_ignored():
    # rating bands, dates, enumerations and durations are not claims about the data
    assert _claims("1–2 stars, 4-5 stars, May 2026–Jul 2026, top 3 complaints, past 2 months") == []


# ---- grounding ----

def _trace(result, name="get_category_stats"):
    return [{"name": name, "input": {}, "result": result}]

def test_rounded_value_is_grounded():
    t = _trace([{"recent_rate_pct": 12.642}])
    assert c.ungrounded_claims("up to 12.6%", t) == []

def test_invented_number_is_flagged():
    t = _trace([{"recent_rate_pct": 12.642}])
    bad = c.ungrounded_claims("it is 47.3% of reviews", t)
    assert [b.value for b in bad] == [47.3]

def test_truncation_is_flagged_but_rounding_is_not():
    t = _trace([{"recent_rate_pct": 23.774}])
    assert c.ungrounded_claims("about 24%", t) == []
    assert [b.value for b in c.ungrounded_claims("about 23%", t)] == [23.0]

def test_simple_arithmetic_on_a_row_is_grounded():
    t = _trace([{"recent_pct_positive": 64.2, "baseline_pct_positive": 35.1}])
    assert c.ungrounded_claims("a 29.1-point swing", t) == []

def test_arithmetic_across_unrelated_rows_is_not_free():
    t = _trace([{"recent_rate_pct": 10.0}, {"recent_rate_pct": 3.0}])
    # 13.0 would need a sum across two different categories -- flagged as a claim to verify
    assert [b.value for b in c.ungrounded_claims("that's 13.0% combined", t)] == [13.0]

def test_star_ratings_in_search_results_dont_ground_stray_numbers():
    t = _trace([{"rating": 4, "text": "3 days in"}], name="search_reviews")
    assert [b.value for b in c.ungrounded_claims("4% of reviews", t)] == [4.0]

def test_search_result_count_is_usable():
    t = _trace([{"rating": 1}, {"rating": 2}, {"rating": 1}], name="search_reviews")
    assert c.ungrounded_claims("3 reviews", t) == []

def test_followup_may_restate_a_prior_answers_number():
    t = _trace([{"recent_rate_pct": 5.0}])
    assert c.ungrounded_claims("still 23.8% overall", t, extra_texts=("earlier: 23.8%",)) == []

def test_nan_and_bool_never_ground_anything():
    t = _trace([{"x": float("nan"), "flag": True}])
    assert [b.value for b in c.ungrounded_claims("1%", t)] == [1.0]


# ---- format checks ----

def test_emoji_detected_but_star_glyph_allowed():
    assert c.has_emoji("\U0001F534 top issue")
    assert not c.has_emoji("rated 4-5★ by most")

def test_header_and_table_detection():
    assert c.has_markdown_header("## Overview\ntext")
    assert not c.has_markdown_header("**Bold** lead\n- bullet")
    assert c.has_table("| a | b |\n|---|---|\n| 1 | 2 |")
    assert not c.has_table("a | b in prose, not a table")

def test_review_id_leaks():
    assert c.leaks_review_id("see 70da0325-4e30-4771-a1aa-c514b0b6d2cb")
    assert c.leaks_review_id("review 14342033977 said")
    assert not c.leaks_review_id("126 mentions in 2026")

def test_banned_sentiment_phrasing():
    assert c.banned_phrases_found("64% positive sentiment") == ["positive sentiment"]
    assert c.banned_phrases_found("a shift toward more negative sentiment") == ["negative sentiment"]
    assert c.banned_phrases_found("Sentiment turned in August") == ["sentiment turned"]
    assert c.banned_phrases_found("64% were rated 4-5 stars") == []
    # explaining the limitation is fine -- the word alone isn't banned
    assert c.banned_phrases_found("I don't measure sentiment directly; I use star ratings") == []

def test_recommendation_and_refusal():
    assert c.has_recommendation("x\n\n**Recommendation:** fix billing")
    assert not c.has_recommendation("Recommendation: fix billing")
    assert c.looks_like_refusal("I don’t have data on Garmin")
    assert not c.looks_like_refusal("Pricing is the top issue")
