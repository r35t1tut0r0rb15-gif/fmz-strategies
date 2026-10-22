"""55-bar high breakouts over the SMA 200, daily bars, long only: a bar whose high is the 55-bar high with the close over the SMA 200 buys; a bar whose low is the 20-bar low sells.
Port of FMZ strategy #474020 "HBTSHistorical Breakout Trend System with Moving Average Filter HBTS" (Turtle Traders - Andrei).

FMZ source id: 474020

Source
    https://www.fmz.com/strategy/474020 (PineScript v5, FMZ last modified 2024-12-05 14:40:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-161), buy lookback 55; sell lookback 20; SMA 200 (type SMA); 10 % of equity
    high == highest(high, 55) and close > sma200 -> entry Comprar;  low == lowest(low, 20) -> close Comprar

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both windows include the current bar. The close acts only on a long held into the bar (#437773):
      a bar with both sends the entry from flat and closes a held long; a loop follows that. The other
      average types are separate settings, not ported (default SMA). Long only. The equity share is not
      ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian-style breakouts with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474020_high55_breakout_sma200_low20_exit_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback_buy": [55, 20],
    "lookback_sell": [20, 10],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"lookback_buy": 55, "lookback_sell": 20, "ma_length": 200}


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
    go = ((h == h.rolling(int(p["lookback_buy"])).max()) & (c > c.rolling(int(p["ma_length"])).mean())).to_numpy()
    out = (lo == lo.rolling(int(p["lookback_sell"])).min()).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if go[i] and pos == 0:
            le[i], nxt = True, 1
        if out[i] and pos == 1:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
