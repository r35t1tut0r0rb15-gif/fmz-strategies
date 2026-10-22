"""EMA 4 crossings of both the EMA 9 and the EMA 18 on one bar, with the close an ATR 14 beyond the EMA 9, broker days: the cross up goes long, the cross down goes short, each with a stop at the signal bar's EMA 4; reversing.
Port of FMZ strategy #476256 "Multi EMA Cross with Oscillator and Dynamic Support Resistance Trading Strategy" (EMA Crossover + ATR + PPSignal).

FMZ source id: 476256

Source
    https://www.fmz.com/strategy/476256 (PineScript v5, FMZ last modified 2024-12-27 14:45:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-171), EMA 4 / 9 / 18; ATR 14; daily pivot levels from the previous day (plotted only)
    crossover(ema4, ema9) and crossover(ema4, ema18) and close > ema9 + atr -> entry Buy, exit(from Buy, stop = ema4);  the mirror and close < ema9 - atr -> entry Sell, exit(from Sell, stop = ema4)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent on each signal bar at that bar's EMA 4: the opening signal's level is ported, sent
      as a fraction of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256); a repeat signal inside a trade re-sends it and is not followed (as #434428, mark
      trailing_stop_pending). There is no target. The pivot levels are plotted only. REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar EMA stop as a fraction of the fill.
    2 generic: PASS, triple EMA crossings with an ATR distance filter and an EMA stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_476256_ema4_cross_ema9_ema18_atr_filter_ema_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_length": [14, 7],
    "atr_mult": [1.0, 0.5],
}
DEFAULT_PARAMS = {"atr_length": 14, "atr_mult": 1.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signals(bars_df, p):
    c = bars_df["close"]
    e4, e9, e18 = (c.ewm(span=n, adjust=False).mean() for n in (4, 9, 18))
    atr = _atr(bars_df, int(p["atr_length"])) * float(p["atr_mult"])

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    le = xo(e4, e9) & xo(e4, e18) & (c > e9 + atr)
    se = xo(e9, e4) & xo(e18, e4) & (c < e9 - atr)
    return le, se, e4


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, e4 = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = e4.shift(1) >= o     # the stop marketable at the fill
    s_thr = e4.shift(1) <= o
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, e4 = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - e4.shift(1) / o).where(lf, e4.shift(1) / o - 1)
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
