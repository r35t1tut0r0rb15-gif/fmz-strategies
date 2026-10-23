"""SMA 20 slope trading gated by volume: the SMA rising with the 5-bar average of an adjusted volume above its 40-bar mean minus one standard deviation goes long, falling with the same gate goes short; the SMA turning against a position closes it; broker days, reversing.
Port of FMZ strategy #432756 "Trading Strategy Based on Standard Deviation of Trading Volume" (交易量底部标准差系统 (dongyun, volume bottom standard deviation system)).

FMZ source id: 432756

Source
    https://www.fmz.com/strategy/432756 (PineScript v4, FMZ last modified 2023-11-21 11:11:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 149-216), options 1; length 40; nlow 5; factor 1.0
    adjvol := volume (or the last non-zero);  adjvol > 2 x factor x nz(vsd[1]) ? savevol : adjvol[1];  vavg = sma(adjvol, 40), vsd = stdev(adjvol, 40), vavgn = sma(adjvol, 5);  lowlimit = vavg - factor x vsd
    options 1: mavg > mavg[1] and vavgn > lowlimit -> entry Long;  mavg < mavg[1] and vavgn > lowlimit -> entry Short;  mavg < mavg[1] -> close Long;  mavg > mavg[1] -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The adjusted volume runs as written: a bar whose volume is above 2 x the previous standard deviation
      keeps its volume, any other bar takes the previous adjusted value (the comment says high volume is
      replaced; the code replaces the rest: weird case). mavg = sma(close, length / 2) = SMA 20 (integer
      division). options = 1 takes the second entry set and the plain slope exits. A close acts only on a
      position the bar's entries leave unchanged (call order), so a falling SMA with the volume gate open
      reverses a long, and without it closes the long. stdev is the population form. REVERSAL INTENDED.
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average slope with a low-volume gate.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the adjusted volume and its 40-bar mean / standard deviation gate; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432756_sma20_slope_volume_stdev_gate_reversal"
FAMILY = "volume_filter"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [40, 20],
    "factor": [1.0, 0.5],
}
DEFAULT_PARAMS = {"length": 40, "nlow": 5, "factor": 1.0}


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
    c, v = bars_df["close"], bars_df["volume"]
    n, f = int(p["length"]), float(p["factor"])
    vv = v.to_numpy(dtype=float)
    m = len(vv)
    adj = np.full(m, np.nan)
    vsd = np.full(m, np.nan)
    sv_p, adj_p, vsd_p = 0.0, np.nan, np.nan
    for i in range(m):
        sv = vv[i] if vv[i] != 0 else sv_p
        a = vv[i] if vv[i] != 0 else sv
        a = sv if a > 2 * f * (0.0 if np.isnan(vsd_p) else vsd_p) else adj_p
        adj[i] = a
        if i >= n - 1:
            w = adj[i - n + 1:i + 1]
            vsd[i] = w.std() if not np.isnan(w).any() else np.nan
        sv_p, adj_p, vsd_p = sv, a, vsd[i]
    adj_s = pd.Series(adj, index=c.index)
    vavg = adj_s.rolling(n).mean()
    vavgn = adj_s.rolling(int(p["nlow"])).mean()
    gate = (vavgn > vavg - f * pd.Series(vsd, index=c.index)).to_numpy()
    mavg = c.rolling(n // 2).mean()
    rise = (mavg > mavg.shift(1)).to_numpy()
    fall = (mavg < mavg.shift(1)).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        tgt = -1 if (fall[i] and gate[i]) else (1 if (rise[i] and gate[i]) else 0)
        if tgt != 0 and tgt != pos:
            if tgt == 1:
                le[i] = True
            else:
                se[i] = True
            pos = tgt
        elif pos == 1 and fall[i]:
            lx[i], pos = True, 0
        elif pos == -1 and rise[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
