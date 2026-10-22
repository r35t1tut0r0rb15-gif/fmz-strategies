"""Candle-colour reversals, 2-day bars: a green bar goes long, a red bar goes short; a position is closed only when a whole bar passes without a coloured candle (a doji), as the bar counter is reset by every entry call.
Port of FMZ strategy #474839 "基于K线收盘方向的高频交易突破策略-High-Frequency-Breakout-Trading-Strategy-Based-on-Candlestick-Close-Direction" (Candle Close Strategy).

FMZ source id: 474839

Source
    https://www.fmz.com/strategy/474839 (PineScript v5, FMZ last modified 2024-12-12 14:35:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-158), fixed size 1; 200 trades a day; close when barsSinceTrade == 2
    close > open -> entry Buy, barsSinceTrade := 0;  close < open -> entry Sell, barsSinceTrade := 0;  opentrades > 0 -> barsSinceTrade := nz(barsSinceTrade) + 1;  barsSinceTrade == 2 -> close Buy, close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every coloured bar sends an entry and resets the counter (also a same-side entry that is ignored
      while held), and the counter then counts that bar if a trade is open, so it reaches 2 only after a
      bar with close == open: a loop follows the counter and the position, as written. The daily trade
      cap resets on every bar's day change and never binds. A close acts only on the side held into the
      bar and not reversed on it (#437773). REVERSAL INTENDED. The fixed size is not ported. FREQ = "2D"
      from the backtest header (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle-colour reversals with a counter close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed size stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474839_candle_colour_reversal_doji_counter_close"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {"days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    o, c = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    bull, bear = c > o, c < o
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, cnt = 0, 0, np.nan
    for i in range(m):
        pos = nxt
        if bull[i]:
            if nxt != 1:
                le[i], nxt = True, 1
            cnt = 0
        if bear[i]:
            if nxt != -1:
                se[i], nxt = True, -1
            cnt = 0
        if pos != 0:
            cnt = (0 if np.isnan(cnt) else cnt) + 1
        if cnt == 2:
            if pos == 1 and nxt == 1:
                lx[i], nxt = True, 0
            if pos == -1 and nxt == -1:
                sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
