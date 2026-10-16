"""Streak-continuation odds, one-bar trades, 5-minute bars: when a bar completes exactly two green bars in a row and
the running share of two-green streaks that became three-green streaks is under 50 %, go short for one bar; the
mirror (two red bars) goes long for one bar.
Port of FMZ strategy #429575 "多Bar同向策略Multi-Bar-Direction-Strategy" (BO - Bar's direction Signal - Backtesting).

FMZ source id: 429575

Source
    https://www.fmz.com/strategy/429575 (PineScript v4, FMZ last modified 2023-10-18 12:20:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 287-546), streak sets 2..6 on, trading time 05:00-04:59 at GMT+7
    blue_n = cumulative count of bars ending n green bars in a row (red_n for red); pblue3 = blue3 / blue2 x 100
    put = pblue3 < 50 and blue2 rose this bar and blue3 did not -> entry short ("Put")
    call = pred3 < 50 and red2 rose this bar and red3 did not -> entry long ("Call")
    strategy.close_all(when = barstate.isnew): every position is closed on the next bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * `set1 ? x1 : false or set2 ? x2 : ...` parses as `set1 ? x1 : ((false or set2) ? x2 : ...)`; with set1
      on (default) only the two-to-three rule is used, as written.
    * The running counts are expanding (from the first bar of the data to the current one): no look-ahead.
    * barstate.isnew is true on every historical bar, so each position lasts one bar: the target is
      long / short for the bar after a signal and flat otherwise (time exits as signals; consecutive
      signals in one direction keep the position).
    * The trading time 05:00-04:59 at GMT+7 is 22:00-21:59 UTC, which covers every 5-minute bar. The date
      windows are dropped. pyramiding 15 is sizing (stored).
    * A Call after a Put reverses in one bar: REVERSAL INTENDED. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; one-bar holds as exit signals.
    2 generic: PASS, candle colours and frequencies only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 15 stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: trading time 22:00-21:59 UTC daily (every bar); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429575_streak_odds_one_bar"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [50.0, 40.0],
}
DEFAULT_PARAMS = {"threshold": 50.0}


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
    g = (c > o).astype(float)
    r = (c < o).astype(float)
    g2, g3 = g.rolling(2).min() == 1, g.rolling(3).min() == 1
    r2, r3 = r.rolling(2).min() == 1, r.rolling(3).min() == 1
    blue2, blue3 = g2.astype(float).cumsum(), g3.astype(float).cumsum()
    red2, red3 = r2.astype(float).cumsum(), r3.astype(float).cumsum()
    pblue3 = blue3 / blue2.where(blue2 != 0) * 100
    pred3 = red3 / red2.where(red2 != 0) * 100
    thr = float(p["threshold"])
    put = ((pblue3 < thr) & g2 & ~g3).to_numpy()
    call = ((pred3 < thr) & r2 & ~r3).to_numpy()
    tgt = np.where(call, 1, np.where(put, -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
