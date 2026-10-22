"""A DEMA 40 normalised inside its 20-bar 2-sigma band, hourly bars: the bar after a reading over 55 with the low over the upper band goes long (stop at that band, 1.5 R target), the mirror goes short; entries alternate sides; reversing (the 2-ATR trail is pending).
Port of FMZ strategy #491035 "Dual Exponential Moving Average Trend Oscillator Strategy A Standard Deviation Based Dynamic Quantitative Trading Model" (DEMA Trend Oscillator Strategy).

FMZ source id: 491035

Source
    https://www.fmz.com/strategy/491035 (PineScript v6, FMZ last modified 2025-04-18 09:19:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 204-259), DEMA 40; base 20; 2 sd; thresholds 55 / 45; RR 1.5; trail 2 ATR 14 (points and offset)
    long_cond = norm > 55 and low > upperSD;  long_cond[1] and last direction != long -> entry Long + exit(stop = upperSD, limit = close + 1.5 (close - upperSD), trail 2 atr), last := long;  mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the trigger bar (the bar after the condition) from its band and close and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). The trail activates and trails by 2 ATR fixed at the trigger, which the house volatility
      trail (current ATR) cannot express: not ported, mark trailing_stop_pending (as #440449). The last-entry
      flag makes the sides alternate; an entry on the other side reverses (REVERSAL INTENDED). Stop module:
      portfolio_kwargs {} (driver D4). MPL 2.0 source (the notice is kept: Mozilla Public License 2.0,
      © PakunFX). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; band bracket as fractions of the fill; the trail pending.
    2 generic: PASS, normalised DEMA band breakouts.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491035_dema40_norm_band_breakout_band_stop_15r_reversal"
FAMILY = "band_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "len_dema": [40, 20],
    "RR": [1.5, 3.0],
}
DEFAULT_PARAMS = {"len_dema": 40, "RR": 1.5, "base_len": 20, "Lu": 55.0, "Su": 45.0}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len_dema"])
    e1 = c.ewm(span=n, adjust=False).mean()
    dema = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    b = int(p["base_len"])
    base = dema.rolling(b).mean()
    sd = dema.rolling(b).std(ddof=0) * 2
    up, dn = base + sd, base - sd
    norm = 100 * (dema - dn) / (up - dn).where(up != dn)
    trig_l = ((norm > float(p["Lu"])) & (lo > up)).shift(1, fill_value=False).to_numpy()
    trig_s = ((norm < float(p["Su"])) & (h < dn)).shift(1, fill_value=False).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = 0
    for i in range(m):
        if trig_l[i] and last != 1:
            le[i], last = True, 1
        if trig_s[i] and last != -1:
            se[i], last = True, -1
    rr = float(p["RR"])
    lvl = {"l_sl": up, "l_tp": c + (c - up) * rr, "s_sl": dn, "s_tp": c - (dn - c) * rr}
    return pd.Series(le, index=c.index), pd.Series(se, index=c.index), lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
