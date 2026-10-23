"""RSI 20 of the session VWAP of the close (on broker-day bars the VWAP is the day's own close), broker days: crossing over 30 goes long and crossing under 85 goes short; a long closes when the RSI crosses under 85 or 28 days after it crossed over 85, a short when it crosses over 30 or 28 days after it crossed under 30; reversing.
Port of FMZ strategy #426355 "RSI Breakout VWAP Strategy" (RSI on VWAP Upgraded strategy).

FMZ source id: 426355

Source
    https://www.fmz.com/strategy/426355 (PineScript v4, FMZ last modified 2023-09-11 14:13:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 65-122), RSI 20 of vwap(close); oversold 30, overbought 85; late leave 28 bars; bet 0.1 coin; pyramiding 3; start 2020-07-01
    crossover(rsiVWAP, 30) -> entry Long;  crossover(rsiVWAP, 85)[28] or crossunder(rsiVWAP, 85) -> close Long
    crossunder(rsiVWAP, 85) -> entry Short;  crossunder(rsiVWAP, 30)[28] or crossover(rsiVWAP, 30) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On daily bars the session VWAP of the close is the bar's own close (one bar per session), so the
      indicator is RSI 20 of the close and volume cancels: ported as not using volume (check 8). The late
      exit is the crossing 28 bars back, as written. Orders follow the call order; a close only acts on a
      position the bar's entries leave unchanged. The adds that pyramiding 3 allows are sizing: the port
      holds one position. The author's 2020-07-01 start is dropped. REVERSAL INTENDED. The 0.1-coin bet and
      commission are sizing / costs. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI band crossings with a timed exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: bet 0.1 coin, pyramiding 3 and commission 0.04 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the author's start date dropped.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426355_rsi20_daily_vwap_band_cross_late_leave_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 14],
    "lateleave": [28, 14],
}
DEFAULT_PARAMS = {"length": 20, "lateleave": 28, "ovrsld": 30.0, "ovrbgt": 85.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(subset=["close"])
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["length"]))                        # vwap(close) of a one-bar session = close
    lo_, hi_ = float(p["ovrsld"]), float(p["ovrbgt"])
    x_up_lo = (r > lo_) & (r.shift(1) <= lo_)
    x_dn_lo = (r < lo_) & (r.shift(1) >= lo_)
    x_up_hi = (r > hi_) & (r.shift(1) <= hi_)
    x_dn_hi = (r < hi_) & (r.shift(1) >= hi_)
    k = int(p["lateleave"])
    lc, sc = x_up_lo.to_numpy(), x_dn_hi.to_numpy()
    lxc = (x_up_hi.shift(k, fill_value=False) | x_dn_hi).to_numpy()
    sxc = (x_dn_lo.shift(k, fill_value=False) | x_up_lo).to_numpy()
    m = len(lc)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        old = pos
        if lc[i]:
            pos = 1
        if sc[i]:
            pos = -1
        if lxc[i] and old == 1 and pos == 1:
            pos = 0
        if sxc[i] and old == -1 and pos == -1:
            pos = 0
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
