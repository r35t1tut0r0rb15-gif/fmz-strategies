"""A 7-bar z-score of the log close, broker days, from flat: z at or under -1.825 goes long, at or over 1.825 goes short; a close back through the rolling mean takes profit, and a close beyond a stop 2.125 standard deviations away (moved with the current volatility) cuts the loss.
Port of FMZ strategy #486567 "Logarithmic Price Mean Reversion Dynamic Stop Loss Strategy" (Mean Reversion Z-Score Strategy with Dynamic SL).

FMZ source id: 486567

Source
    https://www.fmz.com/strategy/486567 (PineScript v5, FMZ last modified 2025-03-14 09:39:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 189-268), window 7; entries at z -1.825 / 1.825; stops at z -2.125 / 2.125
    z = (log close - sma(log close, 7)) / stdev(log close, 7);  flat and z <= -1.825 -> entry Long, stop := exp(log close - 2.125 sd);  flat and z >= 1.825 -> entry Short, stop := exp(log close + 2.125 sd)
    long: new = exp(log close - 2.125 sd);  sd > entry sd -> stop := min(stop, new);  sd < entry sd -> stop := max(stop, new);  close >= exp(mean) -> close (TP);  else close <= stop -> close (SL);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The position flag, the entry standard deviation and the moving stop are followed in a loop, as
      written; the stop and target are tested on bar closes and sent as closes (exit signals, no stop
      module). Entries only from flat: Opposite entries cannot occur. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based target and volatility stop.
    2 generic: PASS, log-price z-score mean reversion.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_486567_log_zscore7_reversion_mean_target_vol_stop_flat"
FAMILY = "zscore_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    w = int(p["window"])
    lp = np.log(c)
    mu, sd = lp.rolling(w).mean(), lp.rolling(w).std(ddof=0)
    z = ((lp - mu) / sd).to_numpy()
    lv, mv, sv, cv = lp.to_numpy(), mu.to_numpy(), sd.to_numpy(), c.to_numpy(dtype=float)
    ze, zs = float(p["z_entry"]), float(p["z_stop"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    esd = stop = 0.0
    for i in range(m):
        if np.isnan(z[i]):
            continue
        if z[i] <= -ze and pos == 0:
            esd, stop, pos = sv[i], np.exp(lv[i] - zs * sv[i]), 1
            le[i] = True
        if z[i] >= ze and pos == 0:
            esd, stop, pos = sv[i], np.exp(lv[i] + zs * sv[i]), -1
            se[i] = True
        tp = np.exp(mv[i])
        if pos == 1:
            new = np.exp(lv[i] - zs * sv[i])
            if sv[i] > esd:
                stop = min(stop, new)
            elif sv[i] < esd:
                stop = max(stop, new)
            if cv[i] >= tp or cv[i] <= stop:
                lx[i], pos = True, 0
        elif pos == -1:
            new = np.exp(lv[i] + zs * sv[i])
            if sv[i] > esd:
                stop = max(stop, new)
            elif sv[i] < esd:
                stop = min(stop, new)
            if cv[i] <= tp or cv[i] >= stop:
                sx[i], pos = True, 0
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~le), S(se), S(sx & ~se)


def portfolio_kwargs(**params):
    return {}
