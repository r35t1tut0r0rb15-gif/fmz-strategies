"""Bullish engulfing bars in an uptrend, daily bars, long only: a green bar opening under and closing over the previous red bar's high, with the close over the EMA 50 and the 5 / 34 oscillator positive, buys with a 2 % stop from the signal close; there is no other exit.
Port of FMZ strategy #452824 "EMA趋势动量K线形态策略-EMA-Trend-Momentum-Candlestick-Pattern-Strategy" (EMA & K-Pattern Trend Trading (Long Only)).

FMZ source id: 452824

Source
    https://www.fmz.com/strategy/452824 (PineScript v5, FMZ last modified 2024-05-29 17:11:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-129), EMA 50; AO = sma(high, 5) - sma(low, 34); stop 2 % of the signal close
    close > open and close[1] < open[1] and open < close[1] and close > high[1] and close > ema50 and ao > 0 -> entry, exit(stop = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 'AO' is the SMA 5 of highs minus the SMA 34 of lows, as written. The stop is fixed on the
      signal bar from its close: ported as the fixed fraction 0.02 of the fill (as #437751). A repeat
      signal inside the trade re-issues the stop from that bar's close, which stops() cannot express:
      the port keeps the opening level and marks trailing_stop_pending (as #434428). The stop is the
      only exit. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop as a fixed fraction; re-issued stops pending (mark).
    2 generic: PASS, engulfing bars in an EMA uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452824_bullish_engulfing_ema50_ao_2pct_stop_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [50, 100],
    "sl_pct": [0.02, 0.05],
}
DEFAULT_PARAMS = {"ema_len": 50, "sl_pct": 0.02, "ao_short": 5, "ao_long": 34}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    ao = h.rolling(int(p["ao_short"])).mean() - lo.rolling(int(p["ao_long"])).mean()
    engulf = (c > o) & (c.shift(1) < o.shift(1)) & (o < c.shift(1)) & (c > h.shift(1))
    le = engulf & (c > ema) & (ao > 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
