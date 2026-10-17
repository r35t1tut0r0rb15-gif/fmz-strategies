"""Last month's close against its monthly EMA, broker days, long only: while the last completed month's close is above
the EMA 8 of monthly closes (as of that month) the strategy is long; below it, flat.
Port of FMZ strategy #433025 "Monthly Close Price and Moving Average Crossover Strategy" (Monthly MA Close (MMAC)).

FMZ source id: 433025

Source
    https://www.fmz.com/strategy/433025 (PineScript v4, FMZ last modified 2023-11-23 17:09:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 180-242), Time MA "M", period 8, exponential on, own ticker (other ticker off)
    f_secureSecurity(sym, res, src) = security(sym, res, src[1], lookahead_on)  (the last completed higher bar)
    cl1 = f_secureSecurity(tickerid, 'M', close);  ma_long = f_secureSecurity(tickerid, 'M', ema(close, 8))
    cl1 > ma_long -> entry long;  cl1 < ma_long -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * src[1] with lookahead_on is the standard non-repainting form: the previous completed month's
      values, no future. Months are calendar months of the broker day (17:00 America/New_York), built
      from the port's own daily bars; the EMA runs over the monthly closes.
    * The other-ticker option (BTC_USDT:swap) is off by default and not ported. The date window is
      always true. Long only; Opposite entries cannot occur. Daily bars are broker days, stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; monthly values from completed months.
    2 generic: PASS, a close against its moving average.
    3 crypto-exchange-only: no (exchange pair in the header only (the other-ticker option is off)).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); calendar months of broker days; no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433025_monthly_close_vs_ema"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_ma": [8, 12],
    "exponential": [True, False],
}
DEFAULT_PARAMS = {"len_ma": 8, "exponential": True}


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
    month = broker_day(bars_df.index).to_period("M")
    mc = pd.Series(c.to_numpy(), index=month).groupby(level=0).last()
    n = int(p["len_ma"])
    ma = mc.ewm(span=n, adjust=False).mean() if bool(p["exponential"]) else mc.rolling(n).mean()
    cl1 = pd.Series(mc.shift(1).reindex(month).to_numpy(), index=c.index)
    ma1 = pd.Series(ma.shift(1).reindex(month).to_numpy(), index=c.index)
    bull, bear = (cl1 > ma1).to_numpy(), (cl1 < ma1).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and bull[i]:
            pos = 1
        elif pos == 1 and bear[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
