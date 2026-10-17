"""HPotter filtered Chande momentum, 1-hour bars: the 9-bar CMO counting only bar changes larger than a filter (3 price units,
re-expressed as an ATR multiple) above 70 goes long, below -70 goes short; held in between and reversed on the opposite
level.
Port of FMZ strategy #435105 "Momentum Filtering Moving Average Strategy" (CMOfilt).

FMZ source id: 435105

Source
    https://www.fmz.com/strategy/435105 (PineScript v2, FMZ last modified 2023-12-12 12:35:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 145-171), length 9, filter 3 (price units), bands 70 / -70; reverse false
    mom = close - close[1];  kept only where |mom| > 3;  cmo = 100 sum(kept mom, 9) / sum(kept |mom|, 9)
    pos = cmo > 70 ? 1 : cmo < -70 ? -1 : pos[1];  1 -> entry long;  -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the filter is 3 price units; on hourly BTC that is about 0.015 x the Wilder ATR 14
      in late 2023, so the port keeps changes larger than filt_atr x ATR. A zero denominator gives no
      value (held). strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit filter -> an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435105_filtered_cmo_bands"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 20],
    "filt_atr": [0.015, 0.3],
}
DEFAULT_PARAMS = {"length": 9, "filt_atr": 0.015, "top": 70, "low": -70, "atr_len": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    mom = c - c1
    keep = mom.abs() > float(p["filt_atr"]) * atr
    n = int(p["length"])
    s = mom.where(keep, 0.0).rolling(n).sum()
    a = mom.abs().where(keep, 0.0).rolling(n).sum()
    cmo = 100 * s / a.replace(0.0, np.nan)
    up, dn = (cmo > float(p["top"])).to_numpy(), (cmo < float(p["low"])).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
