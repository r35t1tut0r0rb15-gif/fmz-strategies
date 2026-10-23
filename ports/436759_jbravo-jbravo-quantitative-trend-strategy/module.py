"""Broker days: the session VWAP of hlc3 (on a daily chart, the bar's own hlc3) above the EMA 20 goes long, below it goes short; reversing.
Port of FMZ strategy #436759 "JBravo量化趋势策略JBravo-Quantitative-Trend-Strategy" (JBravo Swing (bradvaughn)).

FMZ source id: 436759

Source
    https://www.fmz.com/strategy/436759 (PineScript v4, FMZ last modified 2023-12-27 14:53:07).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 145-226), SMA 9 / EMA 20 / SMA 180 and the Buy / Sell / Strong labels are plots only; VWAP display on
    vwap1 = vwap(hlc3);  vwaplong = vwap1 > ema(close, 20) -> entry GoGo Long, close GoGo Short;  vwapshort = vwap1 < ema20 -> entry GoGo Short, close GoGo Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the header's 1-day chart each bar is its own VWAP session, so vwap(hlc3) is the bar's hlc3 and
      volume drops out (volume not used; weird case: held for volume). The entries fire on every bar of
      the state; a repeated same-side entry adds nothing, so the strategy is the state of hlc3 against the
      EMA 20. The Buy / Sell / StrongBuy / StrongSell logic only feeds plots and alerts. vwapInput is on.
      REVERSAL INTENDED. qty 1 is sizing. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, typical price against an EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 1 unit, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the VWAP session is the daily bar.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436759_daily_hlc3_vs_ema20_state_reversal"
FAMILY = "ma_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50],
}
DEFAULT_PARAMS = {"ema_len": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    tp = (h + lo + c) / 3
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    st = np.where(tp > e, 1, np.where(tp < e, -1, 0))
    m = len(st)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if st[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif st[i] == -1 and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
