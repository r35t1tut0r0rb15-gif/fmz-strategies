"""Aggressive 7-count sequential setups on highs / lows, 1-hour bars: a 7th consecutive lower low (against two bars back) goes long, a 7th higher high goes short (reversing); a long closes on a close crossing
under the 7-count support, a 5-count up bar or a short setup; a short mirrors.
Port of FMZ strategy #438948 "Dynamic Trend Tracking Reversal Strategy" (JD Aggressive Sequential Setup 1.0 [NeoButane]).

FMZ source id: 438948

Source
    https://www.fmz.com/strategy/438948 (PineScript v3, FMZ last modified 2024-01-16 15:35:18).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 224-259), S/R crosses in the stop on; count shown 1-4
    up = high > high[2], dn = low < low[2];  count := up ? (up[1] and same colour ? inc(count[1]) : 1) : dn ? (dn[1] and same colour ? inc(count[1]) : 1) : na (inc wraps 7 -> 1)
    usr / dsr = valuewhen(count 7 and up / dn, sma(hlc3, 2)), kept when within 0.42 % of the last value;  long = count 7 and dn;  short = count 7 and up
    sl_l = crossunder(close, dsr) or (count 5 and up) or short;  sl_s = crossover(close, usr) or (count 5 and dn) or long;  entry L / close L / entry S / close S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The colour is green on an up bar, else red, so the count continues only through runs of the same
      side. The closes act on the position held at the bar close; on a bar with both setups the short
      entry comes last and stands (as #437773); a reversing entry with the opposite close leaves the
      reversal (as #438020). strategy.entry reverses: REVERSAL INTENDED. The quantity 1 is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, high / low counts and support / resistance levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 1 stored.
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

NAME = "fmz_438948_jd_aggressive_sequential_7"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "band": [0.0042, 0.01],
    "xx": [True, False],
}
DEFAULT_PARAMS = {"band": 0.0042, "xx": True}


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
    up = (h > h.shift(2)).to_numpy()
    dn = (lo < lo.shift(2)).to_numpy()
    hlc = ((h + lo + c) / 3).rolling(2).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    band = float(p["band"])
    m = len(cv)
    ct = np.full(m, np.nan)
    usr, dsr = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        pu = up[i - 1] if i > 0 else False
        pdn = dn[i - 1] if i > 0 else False
        same = (up[i] == pu) if i > 0 else False         # colour green on up bars, else red
        prev = ct[i - 1] if i > 0 and not np.isnan(ct[i - 1]) else 0.0
        inc = 1.0 if prev == 7 else prev + 1
        if up[i]:
            ct[i] = inc if (pu and same) else 1.0
        elif dn[i]:
            ct[i] = inc if (pdn and same) else 1.0
        u_raw = hlc[i] if (ct[i] == 7 and up[i]) else (usr[i - 1] if i > 0 else np.nan)
        d_raw = hlc[i] if (ct[i] == 7 and dn[i]) else (dsr[i - 1] if i > 0 else np.nan)
        u1 = usr[i - 1] if i > 0 else np.nan
        d1 = dsr[i - 1] if i > 0 else np.nan
        usr[i] = u1 if (u_raw <= u1 * (1 + band) and u_raw >= u1 * (1 - band)) else u_raw
        dsr[i] = d1 if (d_raw <= d1 * (1 + band) and d_raw >= d1 * (1 - band)) else d_raw
    com = ct == 7
    long_ = com & dn
    short_ = com & up
    us, ds = pd.Series(usr, index=c.index), pd.Series(dsr, index=c.index)
    x_dn = ((c < ds) & (c.shift(1) >= ds.shift(1))).to_numpy()
    x_up = ((c > us) & (c.shift(1) <= us.shift(1))).to_numpy()
    five_up, five_dn = (ct == 5) & up, (ct == 5) & dn
    if p["xx"]:
        sl_l = x_dn | five_up | short_
        sl_s = x_up | five_dn | long_
    else:
        sl_l = five_up | short_
        sl_s = five_dn | long_
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if short_[i] and pos != -1 and i + 1 < m:
            se[i], pos = True, -1
        elif long_[i] and pos != 1 and i + 1 < m:
            le[i], pos = True, 1
        elif pos == 1 and sl_l[i]:
            lx[i], pos = True, 0
        elif pos == -1 and sl_s[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
