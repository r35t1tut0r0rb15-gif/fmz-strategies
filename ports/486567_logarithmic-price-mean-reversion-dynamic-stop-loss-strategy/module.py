"""Log-price z-score mean reversion with a volatility-adjusted stop, entries from flat, broker days: a 7-bar z-score of the
log close at or below -1.825 goes long, at or above +1.825 short; the trade takes profit when the close returns to the
rolling mean and stops out when the close crosses a level 2.125 standard deviations away, which tightens or widens as
the volatility changes.
Port of FMZ strategy #486567 "对数价格均值回归动态止损策略-Logarithmic-Price-Mean-Reversion-Dynamic-Stop-Loss-Strategy" (Mean Reversion Z-Score Strategy with Dynamic SL).

FMZ source id: 486567

Source
    https://www.fmz.com/strategy/486567 (PineScript v5, FMZ last modified 2025-03-14 09:39:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 193-262), window 7, entry z -+1.825, stop z -+2.125
    z = (log(close) - sma(log, 7)) / stdev(log, 7);  take profit = exp(sma(log, 7))
    flat and z <= -1.825 -> long, stop = exp(log + (-2.125) x std), entry_std = std (short mirrored)
    in a trade: new = exp(log -+ 2.125 x std); std > entry_std -> stop loosens to new; std < entry_std -> tightens
    long: close >= take profit -> close; else close <= stop -> close (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * All exits are close-checked: exit signals at the next open (rule 3). The script's own position string gates the
      entries (only from flat); it tracks the position. Opposite entries cannot occur.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked exits.
    2 generic: PASS, a z-score of log prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_486567_log_zscore_reversion_vol_stop"
FAMILY = "zscore_mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [7, 14],
    "z_entry": [1.825, 1.5],
}
DEFAULT_PARAMS = {"window": 7, "z_entry": 1.825, "z_stop": 2.125}


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
    lg = np.log(c)
    n = int(p["window"])
    mean, std = lg.rolling(n).mean(), lg.rolling(n).std(ddof=0)
    z = ((lg - mean) / std).to_numpy()
    lgv, mv, sv, cv = lg.to_numpy(), mean.to_numpy(), std.to_numpy(), c.to_numpy(dtype=float)
    ze, zs = p["z_entry"], p["z_stop"]
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, e_std, stop = 0, np.nan, np.nan
    for i in range(m):
        if pos == 0 and z[i] <= -ze:
            pos, e_std, stop, le[i] = 1, sv[i], np.exp(lgv[i] - zs * sv[i]), True
        if pos == 0 and z[i] >= ze:
            pos, e_std, stop, se[i] = -1, sv[i], np.exp(lgv[i] + zs * sv[i]), True
        tp = np.exp(mv[i])
        if pos == 1:
            new = np.exp(lgv[i] - zs * sv[i])
            if sv[i] > e_std:
                stop = min(stop, new)
            elif sv[i] < e_std:
                stop = max(stop, new)
            if cv[i] >= tp or cv[i] <= stop:
                pos, lx[i] = 0, True
        elif pos == -1:
            new = np.exp(lgv[i] + zs * sv[i])
            if sv[i] > e_std:
                stop = max(stop, new)
            elif sv[i] < e_std:
                stop = min(stop, new)
            if cv[i] <= tp or cv[i] >= stop:
                pos, sx[i] = 0, True
    le &= ~lx
    se &= ~sx
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
