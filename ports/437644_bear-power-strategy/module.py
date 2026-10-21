"""Gimelfarb's bear power levels, 1-hour bars: a bear-power range (the candle-case formula) above the sell level is short, at or under the buy level long, in between the state holds; an optional switch trades
the reverse; entries are sent on every bar of the state, reversing.
Port of FMZ strategy #437644 "Bear Power Strategy" (Bear Power Strategy).

FMZ source id: 437644

Source
    https://www.fmz.com/strategy/437644 (PineScript v2, FMZ last modified 2024-01-04 15:13:16).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 181-203), sell level 10, buy level 1 (price units), reverse off
    value = the nested candle-case range formula (non-negative);  pos = -1 if value > 10, 1 if value <= 1, else pos[1];  possig = -pos when reverse

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels are PRICE units; the port tests value / close against fractions (sell_frac;
      the buy fraction is a tenth of it, as 1 / 10): 0.00024 reads 10 on BTC near 42000 (where almost every
      bar is above it), 0.005 a level that bites. The state is a level, so the entry is sent on every bar
      of the state; a same-side entry while in the position is ignored (pyramiding 0). REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND437644 (2 members, best partner #438467, Jaccard 0.712); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437644_bear_power_level_state"
FAMILY = "candle_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sell_frac": [0.00024, 0.005],
}
DEFAULT_PARAMS = {"sell_frac": 0.00024, "buy_ratio": 0.1, "reverse": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _bear_value(o, h, lo, c, c1):
    """The script's nested candle-case formula (na comparisons are false, as in Pine)."""
    if c < o:
        return max(c - o, h - lo) if c1 > o else h - lo
    if c > o:
        return max(c1 - lo, h - c) if c1 > o else max(o - lo, h - c)
    if h - c > c - lo:
        return max(c1 - o, h - lo) if c1 > o else h - lo
    if h - c < c - lo:
        return max(c - lo, h - c) if c > o else o - lo
    if c > o:
        return max(c1 - o, h - c)
    return max(o - lo, h - c) if c1 < o else h - lo


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(cv)
    sf = float(p["sell_frac"])
    bf = sf * float(p["buy_ratio"])
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            v = _bear_value(ov[i], hv[i], lv[i], cv[i], cv[i - 1] if i else np.nan) / cv[i]
            if v > sf:
                prev = -1.0
            elif v <= bf:
                prev = 1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
