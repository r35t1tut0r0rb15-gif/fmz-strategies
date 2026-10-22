"""Previous-day extremes against an EMA 10 / 30 trend, daily bars: the close crossing under the previous day's low with the EMA 10 above the EMA 30 goes long, crossing over the previous high with the EMA 10
below goes short; the stop and target, re-set every bar from the close and the fill, are kept pending; reversing.
Port of FMZ strategy #443229 "Double Confirmation Breakthrough Strategy" (Estrategia de Trading con Senales de Maximo/Minimo Diario).

FMZ source id: 443229

Source
    https://www.fmz.com/strategy/443229 (PineScript v5, FMZ last modified 2024-03-01 10:55:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-198), previous day high / low (security D, [1], lookahead on); EMA 10 / 30; risk-reward 4
    crossunder(close, prevLow) and ema10 > ema30 -> entry Compra;  crossover(close, prevHigh) and ema10 < ema30 -> entry Venta
    risk = close - avg;  exit(stop = close - risk / 4, limit = close + 4 risk) for both ids, every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily chart the requests with [1] and lookahead on are the previous day's high and low, no
      look-ahead. The bracket is re-sent on every bar from that bar's close and the average price, so it
      moves after entry (and is na on the flat signal bar): kept pending (mark trailing_stop_pending, as
      #438034); positions end at the opposite entry until then. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket pending.
    2 generic: PASS, previous-day extreme crossings with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_443229_prev_day_extreme_cross_ema_trend_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30}


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
    ph, pl = h.shift(1), lo.shift(1)
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (c < pl) & (c.shift(1) >= pl.shift(1)) & (f > s)
    se = (c > ph) & (c.shift(1) <= ph.shift(1)) & (f < s)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
