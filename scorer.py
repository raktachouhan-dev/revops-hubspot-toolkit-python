"""ICP scoring and tiering. Weights are assumptions: tune them on your own closed-won data."""
from dataclasses import dataclass

SIZE_TIERS = [(50, 30), (10, 22), (2, 14), (0, 6)]
STRATEGY_PTS = {"Buyout": 25, "Private Credit": 25, "Growth Equity": 18, "Real Estate": 12, "Venture": 8}
STRATEGY_DEFAULT = 5
GEO_PTS = {"US": 15, "UK": 12, "DE": 10, "SG": 8}
GEO_DEFAULT = 4
FUNDRAISE_WITHIN_MONTHS = 12
FUNDRAISE_PTS = 20
DEBT_MATURITY_PTS = 10
TIER_A, TIER_B = 70, 40


@dataclass
class Scored:
    score: int
    tier: str
    breakdown: str


def to_bool(value) -> bool:
    """CSV values arrive as text, and the string 'false' must not be truthy."""
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def score_account(row: dict) -> Scored:
    aum = float(row["aum_usd_bn"])
    size = next(pts for minimum, pts in SIZE_TIERS if aum >= minimum)
    strategy = STRATEGY_PTS.get(row["strategy"], STRATEGY_DEFAULT)
    geo = GEO_PTS.get(row["hq_country"], GEO_DEFAULT)
    signals = 0
    if float(row["months_since_fundraise"]) <= FUNDRAISE_WITHIN_MONTHS:
        signals += FUNDRAISE_PTS
    if to_bool(row["debt_maturity_12m"]):
        signals += DEBT_MATURITY_PTS
    score = min(100, size + strategy + geo + signals)
    tier = "A" if score >= TIER_A else "B" if score >= TIER_B else "C"
    return Scored(score, tier, f"size {size} + strategy {strategy} + geo {geo} + signals {signals}")
