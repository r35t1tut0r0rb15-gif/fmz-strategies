"""RSI(2) dip with close-checked exits around the signal prices, long only, broker days: RSI 2 crossing under
14 goes long; the long closes when a close is 0.33 % above, or 0.55 % below, the average of the signal
closes of the current run (up to two signals).
Port of FMZ strategy #428854 "Trend Following Moving Stop Loss MA Strategy" (Autoview Build-a-bot - 1m chart).

FMZ source id: 428854

Source
    https://www.fmz.com/strategy/428854 (PineScript v3, FMZ last modified 2023-10-10 10:36:16).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 161-397), RSI 2 vs 14, take profit 33 / stop 55 (x 0.01 %), counts <= 2, Longs Only
    rsi = rma-based RSI(2) of close; long = crossunder(rsi, 14) (shorts na: Longs Only)
    longCondition = long and (count <= 2 or count == 1 or count >= 1000000)   (count = long signals since the last reset)
    averageLongs = mean of the closes of the longCondition bars since the last reset
    close > avg x (1 + 0.33 %) and not longCondition -> close; close < avg x (1 - 0.55 %) and no longCondition -> close
    reset counts and averages on a close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: default pyramiding 0, so a second long signal adds
      nothing at the broker, but it still enters the script's own average (as written).
    * After a reset the average is 0 / 0 = na, so no exit fires until the next long signal. The
      trailing-stop option defaults to false (stored). `? 1 : 0 and vrsi < 20` parses as
      `? 1 : (0 and ...)`: the RSI 6 filter never acts (as written).
    * Exits are close checks, so they are exit signals (rule 3), not stops.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, RSI levels and percentages only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() and the pyramiding counters stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428854 (2 members, best partner #430128, Jaccard 0.982); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428854_rsi2_dip_signal_average_exits"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsin": [14, 10],
    "tp": [33, 66],
}
DEFAULT_PARAMS = {"length": 2, "rsin": 14, "tp": 33, "sl": 55, "pyrl": 2, "pyre": 1, "pyrg": 1000000}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), int(p["length"])), _rma((-d).clip(lower=0), int(p["length"]))
    rsi = pd.Series(np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn))), index=c.index)
    rsi = rsi.where(up.notna() & dn.notna())
    ln = float(p["rsin"])
    sig = ((rsi < ln) & (rsi.shift(1) >= ln)).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp, sl = p["tp"] / 10000, p["sl"] / 10000
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    count = nconds = 0
    total = 0.0
    for i in range(m):
        if sig[i]:
            count += 1
        cond = bool(sig[i]) and (count <= p["pyrl"] or count >= p["pyrg"] or count == p["pyre"])
        if cond:
            nconds += 1
            total += cv[i]
        avg = total / nconds if nconds else np.nan
        close_ = (not cond) and not np.isnan(avg) and (cv[i] > avg * (1 + tp) or cv[i] < avg * (1 - sl))
        if close_:
            count = nconds = 0
            total = 0.0
        le[i], lx[i] = cond, close_
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
