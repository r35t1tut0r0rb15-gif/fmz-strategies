"""Bollinger squeeze against ATR, daily bars, long only: twice the ATR(20) above twice the 20-bar deviation with the average ATR falling goes long from flat; a ratchet stop (the previous close less the
entry's 2 ATR, never lowered) tested on the bar's low closes the trade.
Port of FMZ strategy #442502 "Bollinger Bands Consolidation Strategy" ([KL] Bollinger Bands Consolidation Strategy).

FMZ source id: 442502

Source
    https://www.fmz.com/strategy/442502 (PineScript v4, FMZ last modified 2024-02-22 13:43:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-180), BB 20 / 2 on the close; ATR 20 x 2; SMA 20 of it; pyramiding 1; dates dropped
    entry: ATR_x2 > 2 stdev and avg_volat < avg_volat[1]: flat -> entry_price = close, buffer = ATR_x2, stop = close - ATR_x2, entry Long;  long -> entry Long "+"
    in position: stop = max(stop, close[1] - buffer);  low <= stop -> close (take profit when close > entry_price, else stop loss when low <= entry_price)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "+" entry while long is refused at pyramiding 1. The two close branches together always fire
      when the low reaches the stop (a low at or below the stop is at or below any close at or under the
      entry price), so the exit is "low <= stop" read at the bar close and filled at the next open, not
      a broker stop. The flat-bar stop update is overwritten by the entry's. Pine's stdev is the
      population deviation. The date window is dropped. Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR / deviation squeeze; ratchet level tested on the low.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442502_atr_band_squeeze_ratchet_low_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, k = int(p["length"]), float(p["mult"])
    dev2 = k * c.rolling(n).std(ddof=0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr2 = _rma(tr, n) * k
    avg = atr2.rolling(n).mean()
    cond = ((atr2 > dev2) & (avg < avg.shift(1))).to_numpy()
    cv, lv, av = c.to_numpy(dtype=float), lo.to_numpy(dtype=float), atr2.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, buf, stop = False, 0.0, np.nan
    for i in range(m):
        start = held
        if start and i > 0:
            stop = max(stop, cv[i - 1] - buf)
        if cond[i] and not start:
            le[i], buf, stop = True, av[i], cv[i] - av[i]
        if start and lv[i] <= stop:
            lx[i] = True
        held = (start and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
