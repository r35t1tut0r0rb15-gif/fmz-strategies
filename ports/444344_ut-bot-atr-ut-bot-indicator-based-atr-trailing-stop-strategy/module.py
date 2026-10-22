"""Close above the SMA 50 buys, daily bars, long only. The 20 % ratcheting stop from the closes is re-sent every bar and is not ported, so the port has no exit (one long held from the first signal).
Port of FMZ strategy #444344 "基于UT-Bot指标的ATR移动止损策略UT-Bot-Indicator-Based-ATR-Trailing-Stop-Strategy" (Trailingstop (UT Bot ATR trailing stop)).

FMZ source id: 444344

Source
    https://www.fmz.com/strategy/444344 (PineScript v4, FMZ last modified 2024-03-11 11:17:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 120-170), SMA 50; trailing 0.20 of the close (long and short blocks); UT Bot key value 3, ATR 10 (plot only)
    close > sma(close, 50) -> entry long;  long: price_stop_long = max(close x 0.8, price_stop_long[1]) -> exit(stop = price_stop_long)  (the short block never acts: no short entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the highest close since the entry less 20 %, recomputed and re-sent at every bar
      close of the trade: a level that moves after entry on the daily closes. stops() cannot express it
      (the percent trail follows minute closes, not daily closes), so it is not ported (as #437800) and
      the module gets the mark trailing_stop_pending (the intended stop is owed). Without it the port
      has no exit. The short stop block never acts (no short entry), and the UT Bot ATR stop only
      plots. Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop not ported (mark).
    2 generic: PASS, close above the SMA 50.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the 20 % trailing stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: DG444344 (2 members, best partner #444361, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_444344_close_above_sma50_long_entries"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [50, 100],
}
DEFAULT_PARAMS = {"ma_len": 50}


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
    le = (c > c.rolling(int(p["ma_len"])).mean()).to_numpy()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
