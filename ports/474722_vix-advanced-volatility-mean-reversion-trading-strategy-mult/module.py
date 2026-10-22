"""Connors-style stretch reversals on the instrument's own daily prices (the "VIX symbol" input is "swap", the pair's own perpetual), daily bars: a low over the SMA 10 with the close 10 % over it goes long, a high under the SMA 10 with the close 10 % under it goes short; a low under yesterday's SMA closes a long, a high over it closes a short; reversing.
Port of FMZ strategy #474722 "高级波动率均值回归交易策略基于VIX与移动平均的多维量化交易系统-Advanced-Volatility-Mean-Reversion-Trading-Strategy-Multi-Dimensional-Quantitative-Trading-System-Based-on-VIX-and-Moving-Average" (Connors VIX Reversal III invented by Dave Landry).

FMZ source id: 474722

Source
    https://www.fmz.com/strategy/474722 (PineScript v5, FMZ last modified 2024-12-11 17:54:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-147), VIX symbol "swap"; SMA 10; threshold 10 %
    low > sma10 and close > sma10 x 1.10 -> entry Buy;  high < sma10 and close < sma10 x 0.90 -> entry Sell;  low < sma10[1] -> close Buy;  high > sma10[1] -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * "swap" is the FMZ contract type of the header pair (its perpetual), so the "VIX" series is read as
      the chart instrument's own daily close / high / low (ambiguity below). The SMA of yesterday is the
      SMA 10 of the previous bar. A close acts only on the side held into the bar and not reversed on it
      (#437773); a loop follows that. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA stretch entries with SMA re-touch exits.
    3 crypto-exchange-only: no (exchange pair in the header only; the "VIX" request read as the same pair).
    4 signals only: no sizing code.
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

NAME = "fmz_474722_own_price_sma10_stretch_10pct_reversal_retouch_exit"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "pct": [10, 5],
}
DEFAULT_PARAMS = {"length": 10, "pct": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["length"])).mean()
    ma1 = ma.shift(1)
    k = float(p["pct"]) / 100
    buy = ((lo > ma) & (c > ma * (1 + k))).to_numpy()
    sell = ((h < ma) & (c < ma * (1 - k))).to_numpy()
    bx = (lo < ma1).to_numpy()
    sxx = (h > ma1).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if buy[i] and nxt != 1:
            le[i], nxt = True, 1
        if sell[i] and nxt != -1:
            se[i], nxt = True, -1
        if bx[i] and pos == 1 and nxt == 1:
            lx[i], nxt = True, 0
        if sxx[i] and pos == -1 and nxt == -1:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
