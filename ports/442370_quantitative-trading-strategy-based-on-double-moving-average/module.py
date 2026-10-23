"""Hourly bars, long only: from flat, the average of the OBV's and the PVT's percentage distance from their SMA 20 crossing over 1 goes long, with a stop 1 % under the signal bar's low and a target 5 % over its high.
Port of FMZ strategy #442370 "Quantitative Trading Strategy Based on Double Moving Average Crossover" (Pine Script Tutorial Example Strategy 1 (OBV / PVT distance)).

FMZ source id: 442370

Source
    https://www.fmz.com/strategy/442370 (PineScript v5, FMZ last modified 2024-02-21 14:28:28).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 161-201), MA SMA 20; limit 1; stop low x 0.99, target high x 1.05; from 2023-01-01
    obv_diff = (obv - sma(obv, 20)) x 100 / obv;  pvt_diff = (pvt - sma(pvt, 20)) x 100 / pvt;  indicator = (pvt_diff + obv_diff) / 2
    crossover(indicator, 1) and position_size <= 0 -> entry long, exit(stop = low x 0.99, limit = high x 1.05)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The distances divide by the OBV / PVT themselves, so they blow up near zero, as written (weird
      case). The bracket is sent on the signal bar only, as levels from that bar's low and high: ported as
      fractions of the fill, exact (a level the fill has passed is taken at once, 1e-6 floor); the
      signals follow it for the flat test. The 2023 start date is dropped. Long only. 100 % of equity is
      sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket at the signal bar as fractions of the fill.
    2 generic: PASS, OBV / PVT distance-from-average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 100000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV and the PVT; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h; the 2023 start date dropped).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442370_obv_pvt_distance_cross_bar_bracket_1h_long_only"
FAMILY = "obv"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "smoothing": [20, 50],
    "limit": [1.0, 3.0],
}
DEFAULT_PARAMS = {"smoothing": 20, "limit": 1.0, "stop_k": 0.99, "take_k": 1.05}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["smoothing"])
    obv = (np.sign(c.diff()) * v).fillna(0.0).cumsum()
    pvt = (c.diff() / c.shift(1) * v).fillna(0.0).cumsum()
    od = (obv - obv.rolling(n).mean()) * 100 / obv.where(obv != 0)
    pd_ = (pvt - pvt.rolling(n).mean()) * 100 / pvt.where(pvt != 0)
    ind = (pd_ + od) / 2
    lim = float(p["limit"])
    cross = ((ind > lim) & (ind.shift(1) <= lim)).to_numpy()
    stv = (lo * float(p["stop_k"])).to_numpy()
    tgv = (h * float(p["take_k"])).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(cross)
    le = np.zeros(m, dtype=bool)
    pos, pend, sl_px, tp_px = 0, False, np.nan, np.nan
    for i in range(m):
        if pend:
            pos, pend = 1, False
        if pos == 1 and (lv[i] <= sl_px or hv[i] >= tp_px):   # the bracket ends the trade inside the bar
            pos = 0
        if pos == 0 and not pend and cross[i] and i + 1 < m:
            le[i], pend, sl_px, tp_px = True, True, stv[i], tgv[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - (lo * float(p["stop_k"])).shift(1) / o).where(lf)
    tp_f = ((h * float(p["take_k"])).shift(1) / o - 1).where(lf)
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
