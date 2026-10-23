"""Broker days: the EMA 8 crossing over the EMA 20 goes long, crossing under goes short; a bearish engulfing candle closes a long, a bullish engulfing candle closes a short (also after two engulfing candles in a row); reversing.
Port of FMZ strategy #458068 "EMA-RSI-Volume-Price-Trend-Engulfing-Pattern-均线交叉相对强弱指标成交量价格趋势吞没形态策略" (Combined Strategy with Custom Signals and Reversal Patterns).

FMZ source id: 458068

Source
    https://www.fmz.com/strategy/458068 (PineScript v5, FMZ last modified 2024-07-29 16:56:08).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 242-329), EMA 8 / 20; "divergences" on lowest / highest 6 vs 7 bars with volume / close; engulfing exits
    bullish_divergence = lowest(low, 6) < lowest(low, 7) and volume / close > lowest(volume / close, 6);  buy_signal = bullish_divergence or crossover(ema8, ema20) -> entry Long;  sell mirror -> entry Short
    bearishEngulfing and long -> close Long;  bullishEngulfing and short -> close Short;  count of consecutive engulfings == 2 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * lowest(low, 6) can never be under lowest(low, 7) (a 7-bar low includes the 6-bar window), and
      highest(high, 6) never above highest(high, 7), so both "divergences" are always false and volume
      feeds nothing (weird case; held for volume, not used): the entries are the EMA 8 / 20 crossings. The
      stochastic RSI only plots. The closes act only on a position the bar's entries leave unchanged; the
      "second engulfing" closes repeat the first ones. REVERSAL INTENDED. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 8 / 20 crossings with engulfing-candle exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458068_ema8_20_cross_engulfing_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [20, 26],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    buy = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    o1, c1 = o.shift(1), c.shift(1)
    bull_e = ((c > o) & (c1 < o1) & (c > o1) & (o < c1)).to_numpy()
    bear_e = ((c < o) & (c1 > o1) & (c < o1) & (o > c1)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and bear_e[i]:
                new = 0
            elif pos == -1 and bull_e[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
