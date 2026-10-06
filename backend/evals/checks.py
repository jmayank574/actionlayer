"""Deterministic checks for Assistant answers -- no model calls, so they're
free, fast, and can't themselves be wrong in a fuzzy way. The important one is
number grounding: every statistic in an answer must trace to something a tool
actually returned. This is the automated version of the project's core rule
("nothing is invented"), which until now was enforced only by a prompt.

Used by assistant_eval.py; unit-tested in test_checks.py.
"""

import re
from bisect import bisect_left
from dataclasses import dataclass
from itertools import combinations

# ---- formatting checks (the answer-format rules from assistant/agent.py) ----

# Emoji/pictograph ranges. Deliberately NOT the whole 2600 block: the star
# glyph (U+2605) is legitimate in "rated 4-5★", which the Assistant is told to use.
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF✀-➿⭐⭕⚠️]")
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
LONG_ID_RE = re.compile(r"\b\d{9,}\b")  # App Store review ids are 11 digits

# The prompt tells the Assistant to say "rated 4-5 stars", never "positive
# sentiment" -- the number is a star-rating proxy, not inferred sentiment.
# Covers the qualitative phrasings too ("more negative sentiment", "sentiment
# turned/shifted"), which overstate precision just as much as a percentage would.
BANNED_PATTERNS = (
    re.compile(r"\b(?:positive|negative)\s+sentiment\b", re.I),
    re.compile(r"\bsentiment\s+(?:turned|shift\w*|is|has|remains|sits|improv\w*|declin\w*)\b", re.I),
)

REFUSAL_MARKERS = (
    "can't", "cannot", "don't have", "do not have", "not able", "unable",
    "outside", "beyond", "no data", "doesn't contain", "does not contain",
    "isn't something", "is not something", "only cover", "not in the", "not available",
    "isn't in", "not part of", "won't", "will not",
)


def word_count(text: str) -> int:
    return len(text.split())


def has_markdown_header(text: str) -> bool:
    return any(line.lstrip().startswith("#") for line in text.splitlines())


def has_table(text: str) -> bool:
    lines = text.splitlines()
    has_pipe_rows = sum(1 for l in lines if l.strip().startswith("|") and l.strip().endswith("|")) >= 2
    has_rule = any(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$", l) for l in lines)
    return has_pipe_rows and has_rule


def has_emoji(text: str) -> bool:
    return bool(EMOJI_RE.search(text))


def leaks_review_id(text: str) -> bool:
    return bool(UUID_RE.search(text) or LONG_ID_RE.search(text))


def banned_phrases_found(text: str) -> list[str]:
    return [m.group(0).lower() for p in BANNED_PATTERNS for m in p.finditer(text)]


def has_recommendation(text: str) -> bool:
    return "**Recommendation:**" in text


def looks_like_refusal(text: str) -> bool:
    low = text.lower().replace("’", "'")
    return any(m in low for m in REFUSAL_MARKERS)


# ---- number grounding ----

_NUM = r"\d+(?:\.\d+)?"
# "20-28%" -> both ends are claims
_RANGE_PCT_RE = re.compile(rf"(?<![\w.])({_NUM})\s*[–\-]\s*({_NUM})\s*%")
# 23.8%  |  -5.4pp  |  2.1x / 3.4x  |  29-point swing  |  4 percentage points
_UNIT_RE = re.compile(
    rf"(?<![\w.])({_NUM})\s*(%|pp\b|[x×](?![a-zA-Z])|-points?\b|\s+points?\b|\s+percentage points?\b)"
)
# "126 mentions", "3,591 reviews" -- only these nouns: "top 3 complaints" is
# an enumeration, not a statistic, and would be a constant false positive.
_COUNT_RE = re.compile(rf"(?<![\w.])(\d{{1,3}}(?:,\d{{3}})+|\d+)\s+(?:recent\s+|total\s+|new\s+)?(?:reviews?|mentions?)\b")


@dataclass(frozen=True)
class Claim:
    value: float      # absolute value -- sign/direction words ("down", "-5.4pp") aren't checked here
    decimals: int
    raw: str


def _decimals(s: str) -> int:
    return len(s.split(".")[1]) if "." in s else 0


def extract_claims(text: str) -> list[Claim]:
    text = text.replace("−", "-").replace("‑", "-")
    claims: list[Claim] = []
    consumed: list[tuple[int, int]] = []

    def _add(numstr: str, raw: str) -> None:
        claims.append(Claim(abs(float(numstr.replace(",", ""))), _decimals(numstr), raw))

    for m in _RANGE_PCT_RE.finditer(text):
        _add(m.group(1), m.group(0))
        _add(m.group(2), m.group(0))
        consumed.append(m.span())
    for m in _UNIT_RE.finditer(text):
        if any(s <= m.start() < e for s, e in consumed):
            continue
        _add(m.group(1), m.group(0))
    for m in _COUNT_RE.finditer(text):
        _add(m.group(1), m.group(0))
    return claims


def _numeric_leaves(obj, out: list[float]) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        if obj == obj:  # not NaN
            out.append(abs(float(obj)))
    elif isinstance(obj, dict):
        for v in obj.values():
            _numeric_leaves(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _numeric_leaves(v, out)


def _derived_from_rows(obj, out: list[float]) -> None:
    """Differences and sums between numbers in the same record. The Assistant
    is allowed to do simple arithmetic on a row it was given ("a 29-point
    swing" = recent minus baseline) -- that's still traceable, just not
    literally present."""
    if isinstance(obj, dict):
        nums = [abs(float(v)) for v in obj.values()
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v == v]
        for a, b in combinations(nums, 2):
            out.append(abs(a - b))
            out.append(a + b)
        for v in obj.values():
            _derived_from_rows(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _derived_from_rows(v, out)


def tool_number_pool(tool_trace: list[dict], extra_texts: tuple[str, ...] = ()) -> list[float]:
    """Every number the Assistant legitimately had access to this turn, sorted.
    search_reviews results contribute only their count (review text and star
    ratings are noise here -- a "4" rating would ground any stray "4%").
    extra_texts: prior turns' assistant answers, so a follow-up can restate a
    number it already gave."""
    pool: list[float] = []
    for call in tool_trace:
        result = call["result"]
        if call["name"] == "search_reviews":
            pool.append(float(len(result)) if isinstance(result, list) else 0.0)
            continue
        _numeric_leaves(result, pool)
        _derived_from_rows(result, pool)
    for t in extra_texts:
        pool.extend(c.value for c in extract_claims(t))
    return sorted(pool)


def _grounded(claim: Claim, sorted_pool: list[float]) -> bool:
    tol = 0.5 * 10 ** (-claim.decimals) + 0.011
    i = bisect_left(sorted_pool, claim.value - tol)
    return i < len(sorted_pool) and sorted_pool[i] <= claim.value + tol


def ungrounded_claims(text: str, tool_trace: list[dict], extra_texts: tuple[str, ...] = ()) -> list[Claim]:
    pool = tool_number_pool(tool_trace, extra_texts)
    return [c for c in extract_claims(text) if not _grounded(c, pool)]
