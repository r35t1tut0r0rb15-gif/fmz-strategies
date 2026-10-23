"""LazyBear's Volume Flow Indicator (130 bars, cutoff 0.2, volume cap 2.5) against its EMA 5: the difference turning positive goes long, turning negative closes; broker days, long only.
Port of FMZ strategy #432240 "Volume Flow Indicator Based Trend Following Strategy" (Strategy for Volume Flow Indicator with alerts and markers on the chart).

FMZ source id: 432240

Source
    https://www.fmz.com/strategy/432240 (PineScript v4, FMZ last modified 2023-11-15 17:53:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 142-182), VFI length 130, coef 0.2, vcoef 2.5, signal 5, smoothing SMA 3; year > 2018
    cutoff = 0.2 x stdev(log hlc3 change, 30) x close;  vave = sma(volume, 130)[1];  vc = min(volume, 2.5 vave);  vcp = mf > cutoff ? vc : mf < -cutoff ? -vc : 0
    vfi = sma(sum(vcp, 130) / vave, 3);  dVFI = vfi - ema(vfi, 5);  dVFI > 0 and dVFI[1] <= 0 -> entry Long;  dVFI < 0 and dVFI[1] >= 0 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * vc = iff(volume < vmax, volume, vmax), so a bar with no vmax yet gives no value. stdev is the
      population form (Pine's). The "year > 2018" gate on the entry is the author's window and is dropped.
      The close comes after the entry in the script; the two conditions cannot hold on one bar. Long only.
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume flow indicator against its signal.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VFI (capped signed volume over its 130-bar average); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); the author's year > 2018 gate dropped.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432240_volume_flow_indicator_signal_cross_long"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vfi_len": [130, 50],
    "coef": [0.2, 0.1],
}
DEFAULT_PARAMS = {"vfi_len": 130, "coef": 0.2, "vcoef": 2.5, "signal_len": 5}


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
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["vfi_len"])
    typ = (h + lo + c) / 3
    inter = np.log(typ) - np.log(typ.shift(1))
    cutoff = float(p["coef"]) * inter.rolling(30).std(ddof=0) * c
    vave = v.rolling(n).mean().shift(1)
    vmax = vave * float(p["vcoef"])
    vc = v.where(v < vmax, vmax)
    mf = typ - typ.shift(1)
    vcp = pd.Series(np.where(mf > cutoff, vc, np.where(mf < -cutoff, -vc, 0.0)), index=c.index)
    vfi = (vcp.rolling(n).sum() / vave.where(vave != 0)).rolling(3).mean()
    d = vfi - vfi.ewm(span=int(p["signal_len"]), adjust=False).mean()
    dp = d.shift(1)
    up = ((d > 0) & (dp <= 0)).to_numpy()
    dn = ((d < 0) & (dp >= 0)).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and up[i]:
            le[i], pos = True, 1
        elif pos == 1 and dn[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
