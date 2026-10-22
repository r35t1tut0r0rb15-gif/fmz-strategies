"""Hull MA (12) crossings of the Kijun-sen (26) outside the displaced cloud, 1-hour bars: a cross up with the close above both displaced spans goes long, a cross down below both goes short; the opposite
crossing closes; reversing.
Port of FMZ strategy #449710 "基于修正Hull移动平均与一目均衡的量化交易策略-Quantitative-Trading-Strategy-Based-on-Modified-Hull-Moving-Average-and-Ichimoku-Kinko-Hyo" (HMX+IKHS (Hull MA_X + Ichimoku Kinko Hyo Strategy)).

FMZ source id: 449710

Source
    https://www.fmz.com/strategy/449710 (PineScript v4, FMZ last modified 2024-04-28 13:39:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-163), Hull MA 12; Tenkan 9, Kijun 26 (max of the two), Senkou B 52, displacement 26; 100 % of equity
    hull = wma(2 wma(close, 6) - wma(close, 12), 3);  crossover(hull, kijun) and close > spanA[26] and close > spanB[26] -> entry Long;  crossunder and below both -> entry Short
    crossunder(hull, kijun) -> close Long;  crossover(hull, kijun) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Kijun-sen uses the longer of the two lengths (26), as written; the spans are compared 26 bars
      back. The closes come after the entries: a close after a reversing entry on the same bar leaves
      the reversal. REVERSAL INTENDED. The 100 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the spans from 26 bars back.
    2 generic: PASS, Hull / Kijun crossings with a cloud filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449710_hull12_kijun_cross_cloud_filter_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "keh": [12, 20],
    "displacement": [26, 13],
}
DEFAULT_PARAMS = {"keh": 12, "displacement": 26, "tenkan": 9, "kijun": 26, "span_b": 52}


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


def _wma(x, n):
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    keh = int(p["keh"])
    hull = _wma(2 * _wma(c, int(round(keh / 2))) - _wma(c, keh), int(round(np.sqrt(keh))))

    def mid(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    tenkan = mid(p["tenkan"])
    kijun = mid(max(int(p["tenkan"]), int(p["kijun"])))
    a = (tenkan + kijun) / 2
    b = mid(p["span_b"])
    k = int(p["displacement"])
    a_k, b_k = a.shift(k), b.shift(k)
    xo = (hull > kijun) & (hull.shift(1) <= kijun.shift(1))
    xu = (hull < kijun) & (hull.shift(1) >= kijun.shift(1))
    le = xo & (c > a_k) & (c > b_k)
    se = xu & (c < a_k) & (c < b_k)
    return le, xu & ~se, se, xo & ~le


def portfolio_kwargs(**params):
    return {}
