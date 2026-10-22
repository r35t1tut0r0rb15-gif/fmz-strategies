"""EMA 11 / 21 crossings, intraday, 1-hour bars, long only: the EMA 11 crossing over the EMA 21 on a bar opening by 15:00 UTC goes long; the cross back, a bar low under 99 % or a high over 103 % of the
signal close, or any bar from 15:00 UTC closes.
Port of FMZ strategy #440361 "基于EMA指标的跨周期交易策略EMA-Crossover-Quantitative-Trading-Strategy" (EMA Crossover Strategy by Vikrant Singh).

FMZ source id: 440361

Source
    https://www.fmz.com/strategy/440361 (PineScript v5, FMZ last modified 2024-01-29 15:56:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-231), EMA 11 / 21; stop 1 %, target 3 % (close-tested); Long Only on; intraday on (square off from hour 15)
    crossover and not runningPOS and hour <= 15 -> entry Long, runningPOS, levels = close x (1 -/+ 1 % / 3 %);  (crossunder or low < stop or high > target) and runningPOS -> close Long, not runningPOS
    intraday and runningPOS and hour >= 15 -> close_all, not runningPOS;  (the short branch needs Long Only off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour is read on the UTC bar open. The levels are bar-close tests, not orders: the close goes at the
      next open. runningPOS is the script's own flag, kept as written: a close acts only on a held long,
      so a close test true on the entry bar clears the flag while the entry still fills (later bars
      then see no position until the next crossing). close_all after an entry leaves the bar flat (as
      #430380): an entry on the 15:00 bar is cancelled at once. Long only. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested levels.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on bars opening by 15:00 UTC; square off on bars from 15:00 UTC (bar open time).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440361_ema11_21_intraday_long_levels"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_pct": [1.0, 2.0],
    "target_pct": [3.0, 1.5],
}
DEFAULT_PARAMS = {"stop_pct": 1.0, "target_pct": 3.0, "short_len": 11, "long_len": 21, "cut_hour": 15}


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
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    xo = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    xu = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    hour = bars_df.index.tz_convert("UTC").hour.to_numpy()
    cut = int(p["cut_hour"])
    cv = c.to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    sp, tp = float(p["stop_pct"]) / 100, float(p["target_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, run, sl, tl = 0, False, np.nan, np.nan
    for i in range(m):
        new = pos
        if xo[i] and not run and hour[i] <= cut:
            new, run = 1, True
            sl, tl = cv[i] * (1 - sp), cv[i] * (1 + tp)
        if (xu[i] or lv[i] < sl or hv[i] > tl) and run:
            if pos == 1 and new == 1:
                new = 0
            run = False
        if run and hour[i] >= cut:
            new, run = 0, False                          # close_all also cancels a same-bar entry
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
