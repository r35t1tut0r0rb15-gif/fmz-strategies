"""MACD line level crosses, long only, 1-hour bars: the MACD (12 / 26) crossing above a level just below zero goes long,
crossing above a level just above zero closes it; a 0.05 % stop from the fill. The price-unit levels become ATR
multiples.
Port of FMZ strategy #432361 "基于MACD指标的趋势跟踪策略MACD-Trend-Following-Strategy" (EURUSD MACD).

FMZ source id: 432361

Source
    https://www.fmz.com/strategy/432361 (PineScript v3, FMZ last modified 2023-11-16 17:42:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 145-204), MACD 12 / 26, enter -0.0002, close +0.0001 (price units), stop 0.05 %
    crossover(macd, -0.0002) -> entry long;  crossover(macd, 0.0001) -> close long
    exit("Stop Loss", stop = avg price x (1 - 0.05 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels are MACD values in price units, written for EURUSD (the title); at an
      hourly EURUSD ATR of about 0.001 they are -0.2 / +0.1 ATR. They become buy_atr / sell_atr x the
      Wilder ATR 14 of the same bar; the grid adds 0 (on the BTC header the levels are about 0 ATR).
    * The stop is a fixed fraction of the fill (strategy.exit with no entry id covers the long);
      Pine places it once a position exists, the house stop is live on the fill bar too (stated).
      The second MACD (fast_length / slow_length inputs) only draws. Long only; Opposite entries
      cannot occur; a close acts on the position held at the bar's start (with both levels 0 a flat
      bar's cross enters, a long's cross closes), and the port's state machine follows the house stop
      on bars. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, price-unit MACD levels -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG432361 (3 members, best partner #438452, Jaccard 0.969); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432361_macd_level_cross_long"
FAMILY = "macd_momentum"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "buy_atr": [-0.2, 0.0],
    "sell_atr": [0.1, 0.0],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "atr_len": 14, "buy_atr": -0.2, "sell_atr": 0.1, "sl_pct": 0.05}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    lb, ls = float(p["buy_atr"]) * atr, float(p["sell_atr"]) * atr
    le = ((macd > lb) & (macd.shift(1) <= lb.shift(1))).astype(bool)
    lx = ((macd > ls) & (macd.shift(1) <= ls.shift(1))).astype(bool)
    return le, lx


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le_raw, lx_raw = (s.to_numpy() for s in _signals(bars_df, p))
    ov, lv = bars_df["open"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    sl = float(p["sl_pct"]) / 100
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=bool)
    pos, e_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= e_i and lv[i] <= ov[e_i] * (1 - sl):   # house stop from the fill price
            pos = 0
        start = pos
        if le_raw[i] and start == 0:
            pos, e_i = 1, i + 1
            ent[i] = True
        if lx_raw[i] and start == 1:                       # the close acts on the position held at the bar's start
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    lx = (prev == 1) & (tgt == 0)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (ent, lx, false, false.copy()))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = pd.Series(float(p["sl_pct"]) / 100, index=bars_df.index)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
