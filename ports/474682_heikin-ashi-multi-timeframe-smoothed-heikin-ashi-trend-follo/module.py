"""Two-bar average colour, daily bars, long only ("Buy Only"): while the 2-bar SMA of closes is over the 2-bar SMA of opens it buys from flat, while under it sells; each long has a 2 % stop and a 4 % target from its fill price.
Port of FMZ strategy #474682 "多周期平滑Heikin-Ashi趋势跟踪量化交易系统-Multi-Timeframe-Smoothed-Heikin-Ashi-Trend-Following-Quantitative-Trading-System" (Optimized Heikin Ashi Strategy with Buy/Sell Options).

FMZ source id: 474682

Source
    https://www.fmz.com/strategy/474682 (PineScript v5, FMZ last modified 2024-12-11 15:42:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-142), HA timeframe "D" (the chart); stop 2 %, target 4 % of avg (both on); trade type Buy Only
    ha_open = sma(open, 2), ha_close = sma(close, 2) on "D" with lookahead_on;  ha_close > ha_open and size <= 0 -> entry Buy;  ha_close < ha_open and size > 0 -> close Buy;  exit(stop = avg x 0.98), exit(limit = avg x 1.04)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" request equals the daily chart, so lookahead_on reads only the bar itself (no future
      value). The script's "Heikin Ashi" is the 2-bar SMA of opens and of closes. The two exits are
      re-sent with strategy.position_avg_price, the fill price: fixed fractions, active from the fill
      (as #440797). Entries repeat while the colour holds and are ignored while long; after a bracket
      exit the next green bar re-enters, as written. The "Sell Only" type and the date window are not
      ported (defaults). Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars:
      mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the average-price bracket as fixed fractions.
    2 generic: PASS, two-bar average colour with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474682_sma2_open_close_colour_avg_bracket_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.02, 0.04],
    "tp_pct": [0.04, 0.08],
}
DEFAULT_PARAMS = {"sl_pct": 0.02, "tp_pct": 0.04}


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
    o2 = bars_df["open"].rolling(2).mean()
    c2 = bars_df["close"].rolling(2).mean()
    le = c2 > o2
    lx = c2 < o2
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
