"""Bull Power level state, 1-hour bars: a bull-power value above the sell level holds a short, a value at or under the buy level holds a long; reversing; the price-unit levels become fractions of the close.
Port of FMZ strategy #438467 "Bull Power Trading Strategy" (Bull Power Strategy).

FMZ source id: 438467

Source
    https://www.fmz.com/strategy/438467 (PineScript v2, FMZ last modified 2024-01-12 12:02:49).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 225-247), SellLevel 40, BuyLevel 3 (price units); reverse off
    value = the bull-power case table (close, open, close[1], high, low);  pos = -1 if value > 40, 1 if value <= 3, else pos[1];  entries by pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels are PRICE units; the port tests value / close against fractions (sell_frac;
      the buy fraction is 3 / 40 of it, as written; as #437644): 0.00095 reads 40 on BTC near 42000,
      0.01 a level that bites. The case table is ported line for line, close[1] compared with the current
      open as written. The state is a level, so the entry is sent on every bar of the state. reverse is
      off. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit levels -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND437644 (2 members, best partner #437644, Jaccard 0.712); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438467_bull_power_level_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sell_frac": [0.00095, 0.01],
    "buy_ratio": [0.075, 0.5],
}
DEFAULT_PARAMS = {"sell_frac": 0.00095, "buy_ratio": 0.075, "reverse": False}


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


def _bull_value(o, h, lo, c, c1):
    """The source's bull-power case table (c1 = close[1]; nan comparisons are false)."""
    if c < o:
        return max(h - c1, c - lo) if c1 < o else max(h - o, c - lo)
    if c > o:
        return h - lo if c1 > o else max(o - c1, h - lo)
    if h - c > c - lo:
        return max(h - c1, c - lo) if c1 < o else h - o
    if h - c < c - lo:
        return h - lo if c1 > o else max(o - c, h - lo)
    if c1 > o:
        return max(h - o, c - lo)
    return max(o - c, h - lo) if c1 < o else h - lo


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
            v = _bull_value(ov[i], hv[i], lv[i], cv[i], cv[i - 1] if i else np.nan) / cv[i]
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
