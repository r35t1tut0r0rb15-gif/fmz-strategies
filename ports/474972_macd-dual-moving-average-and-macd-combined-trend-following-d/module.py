"""MACD crossings in an SMA 50 / 200 trend, hourly bars, entries only from flat with at least 5 bars since the last signal: a MACD cross up with the close over a rising stack goes long, the mirror goes short; a MACD cross the other way or a close back through the SMA 50 closes it; each trade has a 5-pip stop and 10-pip target from its fill (fractions of 42000).
Port of FMZ strategy #474972 "双移动平均线与MACD结合的趋势跟踪动态止盈智能交易系统-Dual-Moving-Average-and-MACD-Combined-Trend-Following-Dynamic-Take-Profit-Smart-Trading-System" (Trend Following Scalping Strategy).

FMZ source id: 474972

Source
    https://www.fmz.com/strategy/474972 (PineScript v5, FMZ last modified 2024-12-13 11:23:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-220), SMA 50 / 200; MACD 12 / 26 / 9, threshold 0.00005; min 5 bars between signals; stop 5 / target 10 pips (pip = mintick x 10 = 1.0) from avg; 200 % of equity
    bars := nz(bars[1]) + 1;  long = close > ma50 and macdCrossUp and bars >= 5 and up-trend;  short mirror;  long or short -> bars := 0;  flat: long -> entry Long, short -> entry Short;  long and (macdCrossDown or close < ma50) -> close Long;  short mirror;  long: exit(stop = avg - 5 pips, limit = avg + 10 pips)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pips are price amounts (pip = mintick x 10 = 1.0), ported as fractions of 42000 of the fill
      (0.000119 / 0.000238), from strategy.position_avg_price: fixed fractions, active from the fill (as
      #440797); the MACD threshold 0.00005 likewise (a fraction 1.19e-9 of the close). The bar counter
      resets on every signal, taken or not (a loop). Entries only from flat: the loop follows the bracket
      on the bar's high / low and the close tests so the flat gate lines up (as 449508). Opposite entries
      cannot occur. The stats label feeds nothing. Stop module: portfolio_kwargs {} (driver D4). The
      equity share is not ported. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the pip bracket as fixed fractions of the fill.
    2 generic: PASS, trend MACD crossings with close exits and a pip bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474972_ma50_200_trend_macd_cross_spaced_pip_bracket_from_flat"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast_ma": [50, 20],
    "slow_ma": [200, 100],
}
DEFAULT_PARAMS = {"fast_ma": 50, "slow_ma": 200, "sl_frac": 0.000119, "tp_frac": 0.000238,
                  "min_bars": 5, "macd_frac": 1.19e-09}


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
    m50, m200 = c.rolling(int(p["fast_ma"])).mean(), c.rolling(int(p["slow_ma"])).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    big = (macd - sig).abs() > float(p["macd_frac"]) * c
    cu = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & big).to_numpy()
    cd = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & big).to_numpy()
    upt = ((c > m50) & (m50 > m200)).to_numpy()
    dnt = ((c < m50) & (m50 < m200)).to_numpy()
    above = (c > m50).to_numpy()
    below = (c < m50).to_numpy()
    ov, hv, lv = (z.to_numpy(dtype=float) for z in (o, h, lo))
    slf, tpf, k = float(p["sl_frac"]), float(p["tp_frac"]), int(p["min_bars"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cnt, pos, pend, sl, tp = 0, 0, 0, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend = pend, 0
            sl = ov[i] * (1 - slf) if pos == 1 else ov[i] * (1 + slf)
            tp = ov[i] * (1 + tpf) if pos == 1 else ov[i] * (1 - tpf)
        elif pend == 3:
            pos, pend = 0, 0
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        cnt += 1
        lcond = above[i] and cu[i] and cnt >= k and upt[i]
        scond = below[i] and cd[i] and cnt >= k and dnt[i]
        if lcond or scond:
            cnt = 0
        if pend != 0:
            continue
        if pos == 0 and lcond:
            le[i], pend = True, 1
        elif pos == 0 and scond:
            se[i], pend = True, -1
        elif pos == 1 and (cd[i] or below[i]):
            lx[i], pend = True, 3                # the close test: flat from the next open
        elif pos == -1 and (cu[i] or above[i]):
            sx[i], pend = True, 3
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
