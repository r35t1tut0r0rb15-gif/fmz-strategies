"""EMA 15 / EMA 95 cross inside a 22:00-12:00 UTC session, 15-minute bars: a cross in the session closes any
position and enters its way; at the 22:00 UTC bar a flat book enters the side the EMAs point to; outside the
session everything is closed.
Port of FMZ strategy #429147 "Double Moving Average Crossover Trading Strategy" (Arch1tect's New Toy (Strategy Tester Version)).

FMZ source id: 429147

Source
    https://www.fmz.com/strategy/429147 (PineScript v4, FMZ last modified 2023-10-13 15:40:49).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 248-352), EMA 15 / 95, session "2200-1200", start "2200-2201", fixed TP / SL off
    in session: crossover -> close_all + entry long; crossunder -> close_all + entry short
    start bar and flat -> entry long if ema15 > ema95 else short
    not in session -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session strings are read in exchange time, taken as UTC (FMZ crypto data; as #428812), every
      day of the week (":1234567"); a bar is in a session when its open time is inside it (22:00-12:00
      crosses midnight; the start session is the 22:00 bar only).
    * "Fixed TP/SL PIPS" defaults to false: no bracket (the inputs are stored). The daily-loss / drawdown
      risk calls are commented out. The date window is dropped.
    * close_all then entry is a one-bar reversal: REVERSAL INTENDED. FREQ = "15min" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; clock-time exits as signals.
    2 generic: PASS, moving-average crosses only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy(), contract size and the off-by-default TP / SL stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: trading session 22:00-12:00 UTC daily (UTC, no DST; not a venue open); start-of-session entry on the 22:00 UTC bar.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429147_ema15_95_session_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len1": [15, 10],
    "ma_len2": [95, 50],
}
DEFAULT_PARAMS = {"ma_len1": 15, "ma_len2": 95, "sess_start": 1320, "sess_end": 720, "start_end": 1321}


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
    f = c.ewm(span=int(p["ma_len1"]), adjust=False).mean()
    s = c.ewm(span=int(p["ma_len2"]), adjust=False).mean()
    buy = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    above = (f > s).to_numpy()
    idx = bars_df.index.tz_convert("UTC")
    mins = np.asarray(idx.hour * 60 + idx.minute)
    in_sess = (mins >= p["sess_start"]) | (mins < p["sess_end"])           # 22:00-12:00 crosses midnight
    start = (mins >= p["sess_start"]) & (mins < p["start_end"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        p0 = pos
        if in_sess[i]:
            if buy[i]:
                pos = 1
            if sell[i]:
                pos = -1
            if start[i] and p0 == 0 and not (buy[i] or sell[i]):
                pos = 1 if above[i] else -1
        else:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
