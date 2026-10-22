"""SMA 10 / 20 crossings with a 2 % stop, 1-hour bars: the SMA 10 crossing over the SMA 20 goes long, under goes short, each with a stop 2 % from the signal close; the added trailing closes name ids never
entered and never act; reversing. Same rules as #444001 (near-duplicate group, rule 7).
Port of FMZ strategy #444006 "Dynamic Adaptive Trend Trading Strategy" (EfficiVision Trader Strategy (trailing variant)).

FMZ source id: 444006

Source
    https://www.fmz.com/strategy/444006 (PineScript v5, FMZ last modified 2024-03-08 15:17:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 182-240), SMA 10 / 20; stop 2 %; trailing levels (closes on ids never entered)
    crossover -> stopLossPrice = close x 0.98, entry Long;  crossunder -> stopLossPrice = close x 1.02, entry Short;  exit(stop = stopLossPrice) for each id
    trailingStopLossLong < close -> strategy.close("Exit Long Trailing");  trailingStopLossShort > close -> strategy.close("Exit Short Trailing")

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close's first argument is the id: "Exit Long Trailing" / "Exit Short Trailing" are
      never entered, so those closes never act; the rules are those of #444001. The stop is a fixed
      fraction 0.02 of the fill (#437751). strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND444001 (2 members, best partner #444001, Jaccard 0.716); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444006_sma10_20_cross_pct_stop_reversal_trail_variant"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_pct": [0.02, 0.05],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"stop_pct": 0.02, "slow": 20, "fast": 10}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    lsig = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    ssig = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    s_ = float(p["stop_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_pct"])}


def portfolio_kwargs(**params):
    return {}
