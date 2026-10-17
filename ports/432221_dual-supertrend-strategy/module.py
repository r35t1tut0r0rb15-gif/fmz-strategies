"""Band trend from SMA-ATR bands, broker days: a close above the previous final lower band (hl2 - 3 x SMA 10 of the true
range, ratcheted) goes long; otherwise a close below the previous final upper band goes short.
Port of FMZ strategy #432221 "Dual SuperTrend Strategy" (Double Supertrend Strategy).

FMZ source id: 432221

Source
    https://www.fmz.com/strategy/432221 (PineScript v4, FMZ last modified 2023-11-15 16:33:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 164-194), length 10, multiplier 3
    atr = sma(tr, 10); upperBasic = hl2 + 3 atr; lowerBasic = hl2 - 3 atr
    finalUpper := close[1] > finalUpper[1] ? max(upperBasic, finalUpper[1]) : upperBasic
    finalLower := close[1] < finalLower[1] ? min(lowerBasic, finalLower[1]) : lowerBasic
    close > finalLower[1] -> entry long;  else close < finalUpper[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band ratchets are kept exactly as written (the upper band only rises after a close above
      it, the lower band only falls after a close below it), although they differ from the usual
      SuperTrend. The ATR is the SMA of the true range.
    * The long test comes first (if / else if). strategy.entry reverses: REVERSAL INTENDED. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432221_double_band_trend"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "mult": [3.0, 1.5],
}
DEFAULT_PARAMS = {"length": 10, "mult": 3.0}


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
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.rolling(int(p["length"])).mean()
    k = float(p["mult"])
    ub = ((h + lo) / 2 + k * atr).to_numpy()
    lb = ((h + lo) / 2 - k * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    fu, fl = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if i >= 1 and cv[i - 1] > fu[i - 1]:
            fu[i] = max(ub[i], fu[i - 1])
        else:
            fu[i] = ub[i]
        if i >= 1 and cv[i - 1] < fl[i - 1]:
            fl[i] = min(lb[i], fl[i - 1])
        else:
            fl[i] = lb[i]
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        if cv[i] > fl[i - 1]:
            pos = 1
        elif cv[i] < fu[i - 1]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
