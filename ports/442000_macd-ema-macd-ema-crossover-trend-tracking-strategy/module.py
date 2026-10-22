"""MACD signal crossings on the far side of zero with a 15-minute EMA 206 trend, 1-hour bars: two closes above the EMA with MACD (SMA 15 / 24, SMA 9 signal) under zero crossing over its signal goes long,
the mirror short; the stop at the 46-bar low (25-bar high for shorts) and a target 1.9 (2.1) times the stop distance; entries only from flat.
Port of FMZ strategy #442000 "MACD-EMA黄金交叉趋势追踪策略MACD-EMA-Crossover-Trend-Tracking-Strategy" (MACD EMA STRAT).

FMZ source id: 442000

Source
    https://www.fmz.com/strategy/442000 (PineScript v4, FMZ last modified 2024-02-18 15:17:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-273), EMA timeframe "15", EMA 206; MACD 15 / 24 / 9 with SMAs; long and short on; profit factors 1.9 / 2.1; lookbacks 46 / 25; 100 % of equity, capital 5000
    emaSmooth = security("15", ema(close, 206), gaps_on, lookahead_off);  long = close > emaSmooth and close[1] > emaSmooth[1] and macd < 0 and crossover(macd, signal) and opentrades < 1 -> entry long
    short = close < emaSmooth and close[1] < emaSmooth[1] and macd > 0 and crossunder(macd, signal) and opentrades < 1 -> entry short
    long: strategy.exit(stop = lowest(low, 46)[1] at the fill bar, limit = avg + (avg - stop) 1.9);  short: stop = highest(high, 25)[1] at the fill bar, limit = avg - (stop - avg) 2.1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 15-minute EMA requested from a 1-hour chart is the value at the last 15-minute bar inside the
      hour (as #436765), built from the minutes in precompute. lowest(low, 46)[1] read at the fill bar is
      the 46-bar low up to the signal bar, so the stop is set from the signal bar: sl = (close - low46) /
      close, tp = 1.9 sl (shorts: (high25 - close) / close, 2.1 sl), shifted one bar inside stops() and
      re-based on the fill; the script places the exit from the fill bar's close, the port's is active from
      the fill bar (as #440797). Entries need no open trade: opposite entries cannot occur (entries only from
      flat). Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size and capital are sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from signal-bar data.
    2 generic: PASS, lower-timeframe EMA, MACD crossings and swing bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
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

NAME = "fmz_442000_macd_cross_ltf_ema206_swing_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "len1": [206, 100],
    "profit_long": [1.9, 1.0],
}
DEFAULT_PARAMS = {"len1": 206, "profit_long": 1.9, "profit_short": 2.1, "lo_len": 46, "hi_len": 25,
                  "fast": 15, "slow": 24, "signal": 9}
LTF = "15min"  # the security() timeframe "15"


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    b15 = _resample(raw_1m_df, LTF)
    e15 = b15["close"].ewm(span=int(p["len1"]), adjust=False).mean()
    last = e15.groupby(e15.index.floor(FREQ)).last()     # the last 15-minute bar inside each hour
    bars["ema_ltf"] = last.reindex(bars.index)
    return bars


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    es = bars_df["ema_ltf"]
    macd = c.rolling(int(p["fast"])).mean() - c.rolling(int(p["slow"])).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    up = (c > es) & (c.shift(1) > es.shift(1))
    dn = (c < es) & (c.shift(1) < es.shift(1))
    lc = up & (macd < 0) & (macd > sig) & (macd.shift(1) <= sig.shift(1))
    sc = dn & (macd > 0) & (macd < sig) & (macd.shift(1) >= sig.shift(1))
    sl_l = (c - lo.rolling(int(p["lo_len"])).min()) / c
    sl_s = (h.rolling(int(p["hi_len"])).max() - c) / c
    sl = sl_l.where(~sc, sl_s)
    tp = (sl_l * float(p["profit_long"])).where(~sc, sl_s * float(p["profit_short"]))
    return lc.to_numpy(), sc.to_numpy(), sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lc, sc, sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
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
        if pos == 0 and i + 1 < m and not np.isnan(sl[i]):
            if lc[i]:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif sc[i]:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
