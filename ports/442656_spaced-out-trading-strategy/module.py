"""Close crossing its EMA 30, 1-hour bars, long only: from flat, the close crossing over the EMA goes long with a 2 % stop and 3 % target from the signal close; the close crossing under closes.
Port of FMZ strategy #442656 "Spaced Out Trading Strategy" (Spaced Out Trading Strategy).

FMZ source id: 442656

Source
    https://www.fmz.com/strategy/442656 (PineScript v5, FMZ last modified 2024-02-23 15:09:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 130-159), EMA 30; stop 2 %, target 3 %; 5 contracts
    crossover(close, ema) and flat -> entry Buy Call (qty 5), lastTradePrice = close;  else crossunder and long -> close, lastTradePrice = na
    exit(Sell Call, stop = lastTradePrice (1 - 2 %), limit = lastTradePrice (1 + 3 %)) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent every bar at the same levels from the signal close: fixed fractions 0.02 /
      0.03 of the fill (#437751). Entries come only from flat. Long only. Stop module: portfolio_kwargs
      {} (driver D4). The 5-contract quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the contract quantity stored.
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

NAME = "fmz_442656_close_ema30_cross_pct_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_period": [30, 60],
    "tp_pct": [0.03, 0.06],
}
DEFAULT_PARAMS = {"ema_period": 30, "tp_pct": 0.03, "sl_pct": 0.02}


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
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    go = ((c > e) & (c.shift(1) <= e.shift(1))).to_numpy()
    out = ((c < e) & (c.shift(1) >= e.shift(1))).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and go[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
        elif pos == 1 and i >= entry_i and out[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
