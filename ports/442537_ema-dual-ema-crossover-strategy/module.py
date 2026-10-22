"""EMA 25 / 50 crossings, 1-hour bars, long only: the EMA 25 crossing over the EMA 50 goes long with a 2 % target and 2 % stop from the entry (the short side is off by default).
Port of FMZ strategy #442537 "双EMA快慢线交叉策略Dual-EMA-Crossover-Strategy" (SEMA-X).

FMZ source id: 442537

Source
    https://www.fmz.com/strategy/442537 (PineScript v5, FMZ last modified 2024-02-22 16:18:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 166-270), EMA 25 / 50; long on (TP 2 %, SL 2 %), short off; 100 % of equity, capital 1000000, commission 0.075, slippage 3; dates dropped; IRISBOT alert text
    longCondition = isLong and crossover(ema25, ema50) -> entry L;  shortCondition = isShort and crossunder -> entry S
    price = close when a signal fires flat;  exit XL(profit = price 2 % / mintick, loss = price 2 % / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is the signal close times a percentage divided by the tick, a tick distance from the
      fill: a fixed fraction 0.02 / 0.02 of the fill (#437751). The alert strings, table and leverage
      input are display or bot settings. Long only (the short side is off). Stop module:
      portfolio_kwargs {} (driver D4). The percent-of-equity size, capital, commission and slippage are
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, percent-over-tick bracket -> fixed fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital, commission and slippage stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442537_ema25_50_cross_pct_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.02, 0.04],
    "fast": [25, 12],
}
DEFAULT_PARAMS = {"tp_pct": 0.02, "sl_pct": 0.02, "fast": 25, "slow": 50}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
