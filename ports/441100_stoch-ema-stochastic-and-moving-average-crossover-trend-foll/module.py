"""Stochastic crosses in the extreme zones with an EMA 55 / 89 trend, 1-hour bars: K (14, 6) crossing over D under 20 in an uptrend goes long, crossing under D over 80 in a downtrend short; the same
cross against the trend, or K crossing 80 (long) / 20 (short), closes; an 8 % target from the entry; reversing.
Port of FMZ strategy #441100 "基于Stoch和EMA指标的趋势跟踪量化策略Stochastic-and-Moving-Average-Crossover-Trend-Following-Quantitative-Strategy" (Strategy Stoch/EMA Cross).

FMZ source id: 441100

Source
    https://www.fmz.com/strategy/441100 (PineScript v2, FMZ last modified 2024-02-05 15:27:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 187-298), EMA 55 / 89; stochastic 14, K 6, D 3; levels 80 / 20; shorts on; take profit 8 % on, stop loss 2 % off; date window 2019-2020 (timeInRange true); 100 % of equity, capital 1000, commission 0.01 %
    stochLong = crossover(k, d) and k < 20;  stochShort = crossunder(k, d) and k > 80
    stochLong and diff >= 0 -> entry Long;  stochLong and diff < 0 -> close Long;  crossover(k, 80) -> close Long
    stochShort and diff < 0 -> entry Short;  stochShort and diff >= 0 -> close Short;  crossunder(k, 20) -> close Short
    every bar: strategy.exit(profit = close 8 % / mintick) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is in ticks, re-sized every bar from the close: the port reads it as a fixed fraction of
      the entry (as #437751), 0.08. The stop loss is off by default. timeInRange is fixed true. A close
      acts only on the held position. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The 100 % of equity size, capital and commission are sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: ADAPT, tick target from the close -> fixed fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_441100_stoch_zone_cross_ema_trend_pct_target"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.08, 0.04],
    "stoch_length": [14, 9],
}
DEFAULT_PARAMS = {"tp": 0.08, "stoch_length": 14, "fast": 55, "slow": 89, "smooth_k": 6, "smooth_d": 3,
                  "overbought": 80, "oversold": 20}


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
    diff = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["stoch_length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    ob, os_ = float(p["overbought"]), float(p["oversold"])
    sl_ = (k > d) & (k.shift(1) <= d.shift(1)) & (k < os_)
    ss_ = (k < d) & (k.shift(1) >= d.shift(1)) & (k > ob)
    el, xl1 = (sl_ & (diff >= 0)).to_numpy(), (sl_ & (diff < 0)).to_numpy()
    es, xs1 = (ss_ & (diff < 0)).to_numpy(), (ss_ & (diff >= 0)).to_numpy()
    xl2 = ((k > ob) & (k.shift(1) <= ob)).to_numpy()
    xs2 = ((k < os_) & (k.shift(1) >= os_)).to_numpy()
    t_ = float(p["tp"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and hv[i] >= x * (1 + t_):
                pos = 0
            elif pos == -1 and lv[i] <= x * (1 - t_):
                pos = 0
        held = pos
        if el[i] and pos != 1 and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
        elif (xl1[i] or xl2[i]) and held == 1 and pos == 1 and i >= entry_i:
            lx[i], pos = True, 0
        if es[i] and pos != -1 and i + 1 < m:
            se[i], pos, entry_i = True, -1, i + 1
        elif (xs1[i] or xs2[i]) and held == -1 and pos == -1 and i >= entry_i:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
