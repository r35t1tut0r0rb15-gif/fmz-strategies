"""Daily-pivot pullbacks, 1-hour bars: after a bar closing above the previous broker day's R2, a bar trading below that
day's TC, BC or S1 goes long; after a bar closing below S2, a bar trading above BC, TC or R1 goes short.
Port of FMZ strategy #430771 "Classic Dual Trend Tracking Strategy" (swing trade (vinay_swing)).

FMZ source id: 430771

Source
    https://www.fmz.com/strategy/430771 (PineScript v2, FMZ last modified 2023-11-01 16:54:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 195-270), classic daily pivots of the previous day (filtered pivots off)
    from the previous day (security('D', x[1])): pivot = (H + L + C) / 3; r1 = 2 pivot - L; s1 = 2 pivot - H;
      r2 = pivot + (H - L); s2 = pivot - (H - L); BC = (H + L) / 2; TC = 2 pivot - BC
    longCondition = (close > r2)[1] and (low < TC or low < BC or low < s1) -> entry long
    shortCondition = (close < s2)[1] and (high > BC or high > TC or high > r1) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily values are read with [1]: the last completed day (SURVEY_README request.security
      rule), built from the port's own bars on broker days (17:00 America/New_York, DST by the zone)
      and used on every bar of the next broker day. Filtered pivots are off (r1 / s1 as above).
    * The EMA 50 / RSI 7 "engulfing" series only plot. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed daily values.
    2 generic: PASS, pivot levels of the previous day.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily pivots; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430771_daily_pivot_pullbacks"
FAMILY = "pivot_levels"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "r2_mult": [1.0, 0.5],
}
DEFAULT_PARAMS = {"r2_mult": 1.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lab = broker_day(bars_df.index)
    day = pd.DataFrame({"h": h.to_numpy(), "l": lo.to_numpy(), "c": c.to_numpy()}, index=lab)
    d = day.groupby(level=0).agg({"h": "max", "l": "min", "c": "last"})
    piv = (d["h"] + d["l"] + d["c"]) / 3
    rng = (d["h"] - d["l"]) * float(p["r2_mult"])
    lv = pd.DataFrame({"r1": 2 * piv - d["l"], "s1": 2 * piv - d["h"], "r2": piv + rng, "s2": piv - rng,
                       "bc": (d["h"] + d["l"]) / 2})
    lv["tc"] = 2 * piv - lv["bc"]
    prev = lv.shift(1)                                  # the last completed broker day
    mp = prev.reindex(lab)
    r1, s1, r2, s2, bc, tc = (mp[k].to_numpy() for k in ("r1", "s1", "r2", "s2", "bc", "tc"))
    hv, lw, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    bull1 = cv > r2
    bear1 = cv < s2
    bull1p = np.concatenate(([False], bull1[:-1]))
    bear1p = np.concatenate(([False], bear1[:-1]))
    longc = bull1p & ((lw < tc) | (lw < bc) | (lw < s1))
    shortc = bear1p & ((hv > bc) | (hv > tc) | (hv > r1))
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if longc[i]:
            pos = 1
        if shortc[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
