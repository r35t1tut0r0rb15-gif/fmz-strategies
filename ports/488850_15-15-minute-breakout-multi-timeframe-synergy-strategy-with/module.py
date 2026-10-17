"""Previous-bar breakouts with a 3 R bracket, 15-minute bars: a close above the previous bar's high goes long with the
stop at the previous bar's low and a target three times the risk; a close below the previous low goes short.
Port of FMZ strategy #488850 "15分钟突破多周期协同策略基于风险收益比优化模型15-Minute-Breakout-Multi-Timeframe-Synergy-Strategy-with-Risk-Reward-Optimization-Model" (15-min Breakout via 2-min Candle (R:R=1:3)).

FMZ source id: 488850

Source
    https://www.fmz.com/strategy/488850 (PineScript v5, FMZ last modified 2025-03-31 17:32:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 185-229), RR 3
    15-minute high / low / time via request.security on the (15-minute) chart: the bar's own;
    on each new 15-minute bar: last15High = high[1], last15Low = low[1]
    close > last15High -> entry long + exit(stop = last15Low, limit = close + 3 x risk);  close < last15Low -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "15" security on the 15-minute chart is the bar itself, so every bar is a new 15-minute bar and the levels
      are the previous bar's high and low. (The title's 2-minute candle is not the backtest's chart.)
    * The bracket of the signal bar: sl_stop = (close - low[1]) / close, tp_stop = 3 x that (mirrored for shorts),
      shifted one bar inside stops(), re-based on the fill. Each later signal bar while in the trade re-places the
      exit (the entry is ignored): mark trailing_stop_pending; the port keeps the entry's bracket.
    * Every signal bar is an entry; entries reverse (REVERSAL INTENDED); the two cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, bar levels and a reward ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488850_previous_bar_breakout_3r"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [3.0, 1.5],
}
DEFAULT_PARAMS = {"rr": 3.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    long_e = (c > h.shift(1)).astype(bool)
    short_e = (c < lo.shift(1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    long_e, short_e = c > h.shift(1), c < lo.shift(1)
    d = ((c - lo.shift(1)) / c).where(long_e, ((h.shift(1) - c) / c).where(short_e))
    return {"sl_stop": d.shift(1), "tp_stop": (p["rr"] * d).shift(1)}


def portfolio_kwargs(**params):
    return {}
