"""Small reversal candles outside the Bollinger band, broker days, with a tick bracket: a small green candle after a red one that closed under the
lower band (2.1 sd, 21 bars) goes long; a small red candle after a green one that closed over the upper band goes short (reversing); a tick
bracket of 3 / 1.5 ticks is re-expressed as ATR multiples.
Port of FMZ strategy #435957 "Bollinger Band based Price Action Strategy" (Price Action + Bollinger Strategy).

FMZ source id: 435957

Source
    https://www.fmz.com/strategy/435957 (PineScript v4, FMZ last modified 2023-12-20 14:03:52).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 112-137), SMA 21, 2.1 sd; body under half the previous body; profit 3, loss 1.5 (ticks)
    up1 = body < body[1] / 2 and bar[1] == 1 and bar == -1 and close[1] > upper;  dn1 = body < body[1] / 2 and bar[1] == -1 and bar == 1 and close[1] < lower
    dn1 -> entry long, exit(profit = 3, loss = 1.5);  up1 -> entry short, exit(profit = 3, loss = 1.5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick bracket (3 ticks target, 1.5 ticks stop, a fixed small distance) is
      re-expressed as tp_stop = 2 x k_atr x ATR / close and sl_stop = k_atr x ATR / close of the signal
      bar, shifted one bar inside stops() (re-based on the fill); 0.0001 is the tick reading (a tick
      is a tiny fraction of a daily ATR), 0.5 a volatility-sized bracket. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435957_bollinger_reversal_candle_bracket"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.0001, 0.5],
    "b_sma": [21, 34],
}
DEFAULT_PARAMS = {"k_atr": 0.0001, "b_sma": 21, "dev": 2.1, "atr_len": 14}


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
    o, c = bars_df["open"], bars_df["close"]
    bar = pd.Series(np.where(c > o, 1, np.where(c < o, -1, 0)), index=c.index)
    body = (c - o).abs()
    n = int(p["b_sma"])
    sig = c.rolling(n).mean()
    dev = float(p["dev"]) * c.rolling(n).std(ddof=0)
    up1 = (body < body.shift(1) / 2) & (bar.shift(1) == 1) & (bar == -1) & (c.shift(1) > (sig + dev))
    dn1 = (body < body.shift(1) / 2) & (bar.shift(1) == -1) & (bar == 1) & (c.shift(1) < (sig - dev))
    false = pd.Series(False, index=bars_df.index)
    return dn1.fillna(False).astype(bool), false, up1.fillna(False).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f * 2.0}


def portfolio_kwargs(**params):
    return {}
