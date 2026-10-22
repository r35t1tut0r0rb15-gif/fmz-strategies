"""Close crossing an EMA 22 of hl2, 1-hour bars, 05:00-16:00 UTC: the close crossing over goes long, under goes short; a fixed target and stop from the entry (tick distances, re-expressed as ATR
multiples); reversing.
Port of FMZ strategy #442410 "基于Renko平均线的趋势追踪策略Trend-Following-Strategy-Based-on-Renko-Moving-Average" (HL2 - 22 Cross).

FMZ source id: 442410

Source
    https://www.fmz.com/strategy/442410 (PineScript v3, FMZ last modified 2024-02-21 16:36:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-184), take profit 300, stop loss 200, trail 200 with offset 0 (ticks); hours 0500-1600
    crossover(close, ema(hl2, 22)) and in hours -> entry Long;  crossunder and in hours -> entry Short
    strategy.exit(profit = 300, loss = 200, trail_points = 200, trail_offset = na) for each id

Interpretation choices (Pine rules in SURVEY_README.md)
    * The hours are read on the UTC bar open: bars opening 05:00-15:00. The offset input 0 is na, so the
      trail has points but no offset and places nothing (#441084). Criterion 2: the 300 / 200-tick
      target and stop are 30 / 20 price units at mintick 0.1 on the BTC reading; as ATR multiples at the
      1-hour ATR(14) reading of about 150, a target of 0.2 ATR and a stop of 0.1333 ATR of the signal
      bar, shifted one bar inside stops() and re-based on the fill. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on bars opening 05:00-15:00 UTC (bar open time).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442410_hl2_ema22_cross_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [22, 50],
    "tp_atr": [0.2, 1.0],
}
DEFAULT_PARAMS = {"length": 22, "tp_atr": 0.2, "sl_atr": 0.1333, "atr_len": 14, "h_start": 5, "h_end": 16}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    return float(p["sl_atr"]) * a, float(p["tp_atr"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = ((h + lo) / 2).ewm(span=int(p["length"]), adjust=False).mean()
    hour = bars_df.index.tz_convert("UTC").hour
    sess = (hour >= int(p["h_start"])) & (hour < int(p["h_end"]))
    lsig = (((c > e) & (c.shift(1) <= e.shift(1))).to_numpy()) & sess
    ssig = (((c < e) & (c.shift(1) >= e.shift(1))).to_numpy()) & sess
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov, hv, lv = bars_df["open"].to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
