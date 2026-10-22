"""MACD histogram zero crossings after three same-colour candles, inside the 09:00 UTC window, 1-hour bars: three green candles with the histogram crossing above zero go long, three red with it crossing
below zero go short; a 0.03 % target and a 100 % stop from the entry; reversing.
Port of FMZ strategy #440299 "时空优化多时间框架MACD策略Time-and-Space-Optimized-Multi-Timeframe-MACD-Strategy" (Very high win rate strategy).

FMZ source id: 440299

Source
    https://www.fmz.com/strategy/440299 (PineScript v4, FMZ last modified 2024-01-29 10:15:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-217), MACD 12 / 26 / 9 (EMAs); HMA 10 unused; entry session 0900-0915; tp 0.0003, sl 1.0; date window to 2021 (unused)
    close > open three bars running and entrytime and crossover(hist, 0) -> entry long;  close < open three bars running and entrytime and crossunder(hist, 0) -> entry short
    every bar: strategy.exit(profit = close tp / mintick, loss = close sl / mintick) for each side;  (the exit-time session is never used)

Interpretation choices (Pine rules in SURVEY_README.md)
    * entrytime is the bar's open inside 09:00-09:15, read on the UTC bar open: on 1-hour bars the 09:00
      bar. The bracket is in ticks from the entry, re-sized every bar from the close: the port reads it as
      fixed fractions of the entry (as #437751), target 0.0003 and stop 1.0 (a long stop at zero; a short
      stop at twice the entry). The time-window flag is fixed true and the HMA only plotted. strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket from the close -> fixed fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on the bar opening 09:00-09:15 UTC (bar open time).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440299_macd_hist_three_candles_0900_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.0003, 0.003],
    "sl": [1.0, 0.01],
}
DEFAULT_PARAMS = {"tp": 0.0003, "sl": 1.0, "fast": 12, "slow": 26, "signal": 9, "win_hour": 9, "win_minutes": 15}


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
    o, c = bars_df["open"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    g, r = c > o, c < o
    ix = bars_df.index
    t = ix.tz_convert("UTC")
    win = pd.Series((t.hour == int(p["win_hour"])) & (t.minute < int(p["win_minutes"])), index=ix)
    lsig = (g & g.shift(1, fill_value=False) & g.shift(2, fill_value=False) & win
            & (hist > 0) & (hist.shift(1) <= 0)).to_numpy()
    ssig = (r & r.shift(1, fill_value=False) & r.shift(2, fill_value=False) & win
            & (hist < 0) & (hist.shift(1) >= 0)).to_numpy()
    s_, t_ = float(p["sl"]), float(p["tp"])
    ov = o.to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
