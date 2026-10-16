"""SMA 10 / 30 cross with an RSI 50 filter and an ATR bracket, broker days: a golden cross with RSI 14 above 50 goes
long with a stop 2 ATR under the signal bar's low and a target 2 ATR over its high; a death cross with RSI under 50
goes short with the mirror bracket.
Port of FMZ strategy #430053 "Going with the Trend Moving Average Crossover Strategy" (MA cross strategy).

FMZ source id: 430053

Source
    https://www.fmz.com/strategy/430053 (PineScript v5, FMZ last modified 2023-10-24 16:14:10).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 169-201), SMA 10 / 30, RSI 14 vs 50, ATR 14 x 2
    crossover(sma10, sma30): entry long when rsi > 50; exit("exit", "long", stop = low - 2 atr, limit = high + 2 atr)
    crossunder(sma10, sma30): entry short when rsi < 50; exit("exit", "short", stop = high + 2 atr, limit = low - 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket prices come from the signal bar (its low / high and Wilder ATR 14); stops() gives
      them as fractions of the signal bar's close, shifted one bar (re-based on the fill).
    * Approximation: both exits share the id "exit", so in the source a later cross in the other
      direction re-binds that exit order to the other side's entry; when that cross brings no entry
      (RSI filter), the held position loses its bracket and is held until the next reversal. The port
      keeps each position's bracket from its own signal bar (not modelled: the re-binding).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (the shared-id re-binding approximated).
    2 generic: PASS, moving averages, an RSI level and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430053 (2 members, best partner #436783, Jaccard 0.777); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430053_sma_cross_rsi_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "rsi_len": 14, "rsi_mid": 50, "atr_len": 14, "atr_mult": 2.0}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _signals(bars_df, p):
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    xo = (f > s) & (f.shift(1) <= s.shift(1))
    xu = (f < s) & (f.shift(1) >= s.shift(1))
    return (xo & (r > p["rsi_mid"])).astype(bool), (xu & (r < p["rsi_mid"])).astype(bool)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = _atr(bars_df, int(p["atr_len"])) * float(p["atr_mult"])
    below = (c - (lo - a)) / c          # long stop / short target distance
    above = ((h + a) - c) / c           # long target / short stop distance
    sl = pd.Series(np.where(long_e, below, np.where(short_e, above, np.nan)), index=bars_df.index)
    tp = pd.Series(np.where(long_e, above, np.where(short_e, below, np.nan)), index=bars_df.index)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
