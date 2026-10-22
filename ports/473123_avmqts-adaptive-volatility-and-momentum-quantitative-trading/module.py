"""Alternating MACD 8 / 7 / 9 crossings with a 37-bar momentum and SMA 50 filter, daily bars: a MACD cross up with positive momentum and the close over the SMA 50 goes long, the mirror goes short; the sides alternate (the first is a long) with at least 5 bars between trades, and each trade has a 9 % target and 9.9 % stop from the fill; reversing.
Port of FMZ strategy #473123 "AVMQTS Adaptive Volatility and Momentum Quantitative Trading System AVMQTS" ([ETH] Volatility & Momentum Adaptive Strategy).

FMZ source id: 473123

Source
    https://www.fmz.com/strategy/473123 (PineScript v5, FMZ last modified 2024-11-27 14:20:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-160), MACD 8 / 7 / 9; momentum 37; SMA 50; 5 bars between trades; alternate signals on; target 9 %, stop 9.9 % of the average price; trade size 5 ETH
    crossover(macd, signal) and mom > 0 and close > sma50 and 5 bars passed and last signal not long -> (close Short) entry Long
    crossunder and mom < 0 and close < sma50 and 5 bars passed and last signal long -> (close Long) entry Short;  while held: exit(limit / stop from avg)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The last-signal flag starts as na, so the first trade must be a long, and the sides alternate.
      The bracket comes from the average (fill) price and is sent every bar while held: ported active
      from the fill bar (#440797) as the fixed fractions 0.09 / 0.099. Each close plus opposite entry is a
      reversal. The 5-ETH size is not ported; the title names ETH, the rules are generic. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, alternating MACD crossings with momentum and SMA filters.
    3 crypto-exchange-only: no (exchange pair in the header only (ETH named in the title)).
    4 signals only: fixed trade size stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473123_alternating_macd8_7_9_cross_momentum_sma50_pct_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "momentum_length": [37, 20],
    "tp_pct": [0.09, 0.05],
    "sl_pct": [0.099, 0.05],
}
DEFAULT_PARAMS = {"momentum_length": 37, "tp_pct": 0.09, "sl_pct": 0.099, "min_gap": 5}


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
    c = bars_df["close"]
    macd = c.ewm(span=8, adjust=False).mean() - c.ewm(span=7, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    mom = c - c.shift(int(p["momentum_length"]))
    s50 = c.rolling(50).mean()
    up = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (mom > 0) & (c > s50)).to_numpy()
    dn = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (mom < 0) & (c < s50)).to_numpy()
    gap = int(p["min_gap"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_long, last_bar = None, None
    for i in range(m):
        elapsed = last_bar is None or i - last_bar >= gap
        buy = up[i] and elapsed and last_long is not True
        sell = dn[i] and elapsed and last_long is True
        if buy:
            le[i], last_long, last_bar = True, True, i
        if sell:
            se[i], last_long, last_bar = True, False, i
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
