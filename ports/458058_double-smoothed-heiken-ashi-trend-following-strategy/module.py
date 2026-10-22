"""Double-smoothed Heikin Ashi colour turns, 1-hour bars, long only: the smoothed candle turning lime (EMA 10 of the HA open at or under the EMA 10 of the HA close) buys; turning red sells.
Port of FMZ strategy #458058 "Double Smoothed Heiken Ashi Trend Following Strategy" (Smoothed Heiken Ashi Strategy Long Only).

FMZ source id: 458058

Source
    https://www.fmz.com/strategy/458058 (PineScript v5, FMZ last modified 2024-07-29 16:02:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 180-217), EMA 10 of open / high / low / close; Heikin Ashi of those; second EMA 10 of the HA open / close
    o, c, h, l = ema10 of each;  haclose = (o + h + l + c) / 4;  haopen = (haopen[1] + haclose[1]) / 2 (first (o + c) / 2);  col = ema10(haopen) > ema10(haclose) ? red : lime
    col turns lime -> entry Long;  col turns red -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The HA open starts from (o + c) / 2 on the first bar and recurses, as written. Long only. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed Heikin Ashi colour turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458058_double_smoothed_heikin_ashi_turn_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [10, 20],
    "len2": [10, 5],
}
DEFAULT_PARAMS = {"len": 10, "len2": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, n2 = int(p["len"]), int(p["len2"])
    o, h, lo, c = (bars_df[k].ewm(span=n, adjust=False).mean() for k in ("open", "high", "low", "close"))
    hac = ((o + h + lo + c) / 4).to_numpy()
    ov, cv = o.to_numpy(), c.to_numpy()
    m = len(hac)
    hao = np.full(m, np.nan)
    for i in range(m):
        hao[i] = (ov[i] + cv[i]) / 2 if i == 0 else (hao[i - 1] + hac[i - 1]) / 2
    o2 = pd.Series(hao, index=bars_df.index).ewm(span=n2, adjust=False).mean()
    c2 = pd.Series(hac, index=bars_df.index).ewm(span=n2, adjust=False).mean()
    lime = ~(o2 > c2)
    red = ~lime
    le = lime & red.shift(1, fill_value=False)       # col[1] is na on the first bar
    lx = red & lime.shift(1, fill_value=False)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
