"""Green bars closing at (or within 5 % of the body under) their high buy, 1-hour bars, long only; a close under the previous bar's low closes.
Port of FMZ strategy #451396 "无上引线看涨K线突破策略-No-Upper-Wick-Bullish-Candle-Breakout-Strategy" (My strategy (no-upper-wick bullish candle)).

FMZ source id: 451396

Source
    https://www.fmz.com/strategy/451396 (PineScript v5, FMZ last modified 2024-05-14 16:11:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-132), wick under 5 % of the body; exit close < low[1]; margins 100 / 100
    close > open and (high - close) / |open - close| x 100 < 5 -> entry Long Entry;  close < low[1] (security on the chart period, lookahead on) and long -> close Long Entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * The request on the chart's own period with lookahead on returns the chart's low[1]. A repeated
      entry while long is ignored; a same-bar close only acts on a held long. Long only. The margin
      settings are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, strong green candles with a previous-low exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451396_no_upper_wick_green_bar_prev_low_exit_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wick_pct": [5.0, 10.0],
}
DEFAULT_PARAMS = {"wick_pct": 5.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body = (o - c).abs()
    with np.errstate(divide="ignore", invalid="ignore"):
        wick = (h - c) / body.where(body > 0) * 100
    go = ((c > o) & (wick < float(p["wick_pct"]))).to_numpy()
    out = (c < lo.shift(1)).to_numpy()
    m = len(go)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
