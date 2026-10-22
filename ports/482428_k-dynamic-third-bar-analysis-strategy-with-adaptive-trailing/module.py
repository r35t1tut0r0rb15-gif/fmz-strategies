""""Thirds" bar sequences, broker days: after a bar closing in its upper third, a bar that closes in its upper third from the lower or upper third goes long; the mirror goes short; reversing. The stop at the previous bar's low (high), re-sent every bar, is not ported (pending).
Port of FMZ strategy #482428 "动态跟踪止损的三分之一K线量化交易策略-Dynamic-Third-Bar-Analysis-Strategy-with-Adaptive-Trailing-Stop" (TrinityBar with Trailing Stop).

FMZ source id: 482428

Source
    https://www.fmz.com/strategy/482428 (PineScript v5, FMZ last modified 2025-02-18 13:57:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-175), bar thirds (current and previous bar); trailing stop at low[1] / high[1] (chart time frame); 250 % of equity
    validBuy -> close Short, entry Long if not long;  validSell -> close Long, entry Short if not short;  long: exit(stop = low[1]);  short: exit(stop = high[1])

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same signals as #482242 on broker days. The stop is the previous bar's low (high), re-sent on
      every bar, so it moves with each bar: the house trail settings cannot express it, so it is described
      here and kept pending (mark trailing_stop_pending). Each signal closes the other side and enters,
      which is a reversal; on a zero-range bar the later short call wins (#437773). REVERSAL INTENDED. The
      250 % of equity size and capital are sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the bar-low trailing stop described (pending).
    2 generic: PASS, bar-thirds continuation sequences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: ND482242 (2 members, best partner #482242, Jaccard 0.770); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482428_trinity_bar_thirds_sequence_daily_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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


def _types(o, h, lo, c):
    rng = h - lo
    lt, ut = lo + rng / 3, h - rng / 3
    up_close, dn_close = c >= ut, c <= lt
    open_lo, open_hi = o <= lt, o >= ut
    open_mid = (o > lt) & (o < ut)
    bull_any = up_close & (open_lo | open_hi | open_mid)
    bear_any = dn_close & (open_lo | open_hi | open_mid)
    bull_13_33 = up_close & (open_lo | open_hi)
    bear_11_31 = dn_close & (open_lo | open_hi)
    return bull_any, bear_any, bull_13_33, bear_11_31


def simulate(bars_df, **params):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    bull_any, bear_any, bull_now, bear_now = _types(o, h, lo, c)
    le = bull_any.shift(1, fill_value=False) & bull_now
    se = bear_any.shift(1, fill_value=False) & bear_now
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
