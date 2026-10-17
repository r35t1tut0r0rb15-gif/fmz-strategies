"""Close crossing SMA 34 in the SMA 34 / 200 trend with a stochastic filter and a 2 % stop / 4 % target, 1-hour
bars: the close crossing above SMA 34 with SMA 34 above SMA 200 and the smoothed stochastic %K above 20 goes long; the
close crossing below with SMA 34 below SMA 200 and %K below 80 goes short.
Port of FMZ strategy #483679 "双均线交叉与随机指标结合的自适应追踪止损策略-Dual-Moving-Average-Crossover-with-Stochastic-Filter-and-Adaptive-Trailing-Stop-Strategy" ([DRAGON]SMA 34 & SMA 200 with Stochastic 9-3-3 & Trailing Stop).

FMZ source id: 483679

Source
    https://www.fmz.com/strategy/483679 (PineScript v6, FMZ last modified 2025-02-25 11:05:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 172-221), SMA 34 / 200, stochastic 9 smoothed 3, SL 2 %, TP 4 %, BE 2 %
    long = crossover(close, sma34) and sma34 > sma200 and stoK > 20
    short = crossunder(close, sma34) and sma34 < sma200 and stoK < 80
    exit(stop = avg_price x 0.98 (avg_price once close >= avg_price x 1.02), limit = avg_price x 1.04), on signal bars

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are issued only on signal bars, from strategy.position_avg_price, which is na while flat (and the
      opposite trade's price while reversing): a trade opened from flat has, as written, no stop or target until a
      later same-side signal re-issues the exit. The port applies the 2 % / 4 % bracket from the fill (the evident
      intent), as #489289. Decision owed: keep this, or port the literal behaviour.
    * A later same-side signal re-issues the exit, moving the stop to break-even once the close is 2 % in profit:
      mark trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill (re-placement marked).
    2 generic: PASS, moving averages, a stochastic and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483679_sma34_200_stoch_cross_pct_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [2.0, 3.0],
    "tp_pct": [4.0, 6.0],
}
DEFAULT_PARAMS = {"fast": 34, "slow": 200, "k_len": 9, "k_smooth": 3, "sl_pct": 2.0, "tp_pct": 4.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    fast = c.rolling(int(p["fast"])).mean()
    slow = c.rolling(int(p["slow"])).mean()
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    stoch = 100 * (c - ll) / (hh - ll)
    k = stoch.rolling(int(p["k_smooth"])).mean()
    long_e = ((c > fast) & (c.shift(1) <= fast.shift(1)) & (fast > slow) & (k > 20)).astype(bool)
    short_e = ((c < fast) & (c.shift(1) >= fast.shift(1)) & (fast < slow) & (k < 80)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
