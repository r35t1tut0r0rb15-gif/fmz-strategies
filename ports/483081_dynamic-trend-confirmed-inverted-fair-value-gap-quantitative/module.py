"""Inverted fair-value-gap fades in the SMA 50 / 200 trend, always in the market, 2-minute bars: after the first gap bar
has been seen, a close breaking back through the previous bar's high (low) records that bar's high (low) as the
inverted-gap level; in an up-trend a close below the recorded low goes long, in a down-trend a close above the recorded
high goes short.
Port of FMZ strategy #483081 "动态趋势确认的反转公平价值缺口量化交易策略-Dynamic-Trend-Confirmed-Inverted-Fair-Value-Gap-Quantitative-Trading-Strategy" (Inverted FVG Strategy with Trend Check and Trailing Stops).

FMZ source id: 483081

Source
    https://www.fmz.com/strategy/483081 (PineScript v6, FMZ last modified 2025-02-21 11:55:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-176), SMA 50 / 200, stop 100 points, 3 R, trail after 0.5 R
    fvg (var, never reset) = a bar with close > close[1] and low > high[1] (or the mirror) has occurred
    while fvg: (close > high[1] and close[1] < high[1]) or (close < low[1] and close[1] > low[1]) -> ifvg = true,
    ifvgHigh = close > high[1] ? high : na, ifvgLow = close < low[1] ? low : na
    long = ifvg and close < ifvgLow and sma50 > sma200; short = ifvg and close > ifvgHigh and sma50 < sma200
    exit(stop = close -+ 100, limit = close +- 300); trailing exit once 50 points in profit

Interpretation choices (Pine rules in SURVEY_README.md)
    * fvg and ifvg are `var` flags that are only ever set: once the first gap (and then the first break) has occurred
      they stay true, as written; the levels are replaced on every qualifying break (na on the other side).
    * The 100-point stop, the 300-point target and the trail that starts 50 points in profit are price units, judged
      on the author's market (Binance SOL_USDT, 2-minute bars, price about 150-250 USD, ATR about 0.3 USD): unreachable,
      so they are dropped as inert (as #492009, #490798). What remains is a stop-and-reverse on the entry signals.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, gap bars and moving averages; the price-unit exits are inert and dropped.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the inert exits quoted in original_sizing.txt.
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

NAME = "fmz_483081_inverted_fvg_fade_sma_trend_reversal"
FAMILY = "price_action"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    cs = bars_df["close"]
    up = (cs.rolling(int(p["fast"])).mean() > cs.rolling(int(p["slow"])).mean()).to_numpy()
    dn = (cs.rolling(int(p["fast"])).mean() < cs.rolling(int(p["slow"])).mean()).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    fvg = ifvg = False
    i_hi = i_lo = np.nan
    for t in range(1, m):
        if (c[t] > c[t - 1] and lo[t] > h[t - 1]) or (c[t] < c[t - 1] and h[t] < lo[t - 1]):
            fvg = True
        if fvg:
            if (c[t] > h[t - 1] and c[t - 1] < h[t - 1]) or (c[t] < lo[t - 1] and c[t - 1] > lo[t - 1]):
                ifvg = True
                i_hi = h[t] if c[t] > h[t - 1] else np.nan
                i_lo = lo[t] if c[t] < lo[t - 1] else np.nan
        if ifvg:
            if c[t] < i_lo and up[t]:
                le[t] = True
            if c[t] > i_hi and dn[t]:
                se[t] = True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
