"""Adaptive CCI oversold buys with a trailing stop, 1-hour bars, long only: the CCI 20 under an entry level buys; the level starts at -145 and is raised by later checks whenever the lowest CCI of
a look-back window stays above a higher level (-90 over 40 bars up to +70 over 180 bars); a trailing stop follows the price.
Port of FMZ strategy #436119 "望远适应-CCI-底部捕捉商品交易策略Extended-Adaptive-CCI-Bottom-Fishing-Trading-Strategy-for-Commodities" (Extended Adaptive CCI Entry Strategy for Commodities).

FMZ source id: 436119

Source
    https://www.fmz.com/strategy/436119 (PineScript v5, FMZ last modified 2023-12-21 14:30:03).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 145-197), CCI 20; default level -145; eight adaptive levels with look-backs 40 to 180; trail offset 10 USD
    entryLevel (var, starts at -145): in code order, if lowest(cci, 40) > -90: level = -90; if lowest(cci, 50) > -70: level = -70; ... if lowest(cci, 180) > 70: level = 70   (later lines override, never reset)
    cci < entryLevel -> entry long;  exit(trail_offset = 10 USD, trail_price = close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The level variable is never reset, as written, so once a quiet stretch has raised it, it stays. The
      checks run in the script's order each bar (a later true check overrides an earlier one).
      Criterion 2: the trailing offset is in price units (10 ticks, 1 USD at a 0.1 tick); ported natively
      as a percent trail from the best high (mark trailing_stop): 0.00025 reads 1 USD on BTC near 40000,
      0.002 is wider. The trail_price activation at the signal close is immediate. Long only. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-hour bars: not coarse. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; trailing stop native.
    2 generic: ADAPT, price-unit trail -> percent trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity and the USD offset input quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436119_adaptive_cci_oversold_trail_long"
FAMILY = "cci_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cci_length": [20, 30],
    "trail_pct": [0.00025, 0.002],
}
DEFAULT_PARAMS = {"cci_length": 20, "trail_pct": 0.00025, "default_level": -145}
ADAPTIVE = ((40, -90), (50, -70), (60, -50), (90, -4), (120, 0), (140, 25), (160, 50), (180, 70))   # (look-back, level)


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
    c = bars_df["close"]
    n = int(p["cci_length"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        cci = (c - ma) / (0.015 * md)
    checks = [(cci.rolling(lb).min() > lv).fillna(False).to_numpy() for lb, lv in ADAPTIVE]
    cv = cci.to_numpy()
    level = float(p["default_level"])
    m = len(cv)
    le = np.zeros(m, dtype=bool)
    for i in range(m):
        for (lb, lv), chk in zip(ADAPTIVE, checks):
            if chk[i]:
                level = float(lv)                                # a later true check overrides; never reset
        le[i] = bool(cv[i] < level)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
