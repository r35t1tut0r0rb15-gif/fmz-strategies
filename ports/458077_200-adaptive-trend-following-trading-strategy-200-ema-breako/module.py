"""Close crossings of the EMA 200, daily bars: the close crossing over goes long with a 1 % stop and 2 % target, crossing under goes short with the mirror bracket; reversing.
Port of FMZ strategy #458077 "自适应趋势跟踪交易策略200均线突破与动态风险管理系统-Adaptive-Trend-Following-Trading-Strategy-200-EMA-Breakout-with-Dynamic-Risk-Management-System" (200 EMA Strategy).

FMZ source id: 458077

Source
    https://www.fmz.com/strategy/458077 (PineScript v5, FMZ last modified 2024-07-29 17:11:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 181-223), EMA 200 of close; stop 1 %, target 2 % of the signal close; buy / sell switches both on
    crossover(close, ema200) -> entry Buy + exit(stop = close x 0.99, limit = close x 1.02);  crossunder -> entry Sell + exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once on the signal bar from its close: ported as the fixed fractions 0.01 /
      0.02 of the fill. Both switches are on by default. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the percent bracket as fixed fractions.
    2 generic: PASS, EMA 200 crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_458077_ema200_close_cross_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [200, 100],
    "sl_pct": [0.01, 0.03],
    "tp_pct": [0.02, 0.06],
}
DEFAULT_PARAMS = {"ema_len": 200, "sl_pct": 0.01, "tp_pct": 0.02}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = (c > e) & (c.shift(1) <= e.shift(1))
    se = (c < e) & (c.shift(1) >= e.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
