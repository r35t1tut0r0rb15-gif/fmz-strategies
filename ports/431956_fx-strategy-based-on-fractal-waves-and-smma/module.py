"""Fractal entries against the SMMA 30, broker days: a down fractal (the low two bars back under its four neighbours) with
the previous close under the SMMA 30 goes long, an up fractal with the previous close over it goes short; a stop 2.7 ATR
10 from the close follows each position.
Port of FMZ strategy #431956 "FX Strategy Based on Fractal Waves and SMMA" (FX Strategy Based on Fractals and SMMA).

FMZ source id: 431956

Source
    https://www.fmz.com/strategy/431956 (PineScript v4, FMZ last modified 2023-11-13 16:39:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 133-192), SMMA 30, ATR 10 x 2.7, fractal 5 bars, stop 7 % (unused)
    lowFractal = low[2] < low[1], low[3], low[4], low;  long = lowFractal and close[1] < smma(close, 30) -> entry long
    highFractal mirrored -> entry short;  exit(stop = close - 2.7 ATR(10)) re-issued every bar (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-issued every bar at the latest close -+ 2.7 ATR (a level that moves both ways,
      not a best-price trail): rule 2, mark trailing_stop_pending; the port fixes it at the signal
      bar's 2.7 ATR as a fraction of its close, shifted one bar. The 7 % stop input is unused, as
      written. The two entry blocks are the same signals (the 2007-2022 window dropped).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at entry (rule 2).
    2 generic: PASS, fractals, an SMMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431956_fractal_smma_atr_stop"
FAMILY = "pivot_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "smma_len": [30, 60],
    "stop_coef": [2.7, 1.5],
}
DEFAULT_PARAMS = {"smma_len": 30, "stop_coef": 2.7, "atr_len": 10}


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
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sm = _rma(c, int(p["smma_len"]))
    l2, h2 = lo.shift(2), h.shift(2)
    lf = (l2 < lo.shift(1)) & (l2 < lo.shift(3)) & (l2 < lo.shift(4)) & (l2 < lo)
    hf = (h2 > h.shift(1)) & (h2 > h.shift(3)) & (h2 > h.shift(4)) & (h2 > h)
    c1 = c.shift(1)
    lg = (lf & (c1 < sm)).astype(bool)
    sh = (hf & (c1 > sm)).astype(bool)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    af = _rma(tr, int(p["atr_len"])) / c
    return lg & ~sh, sh, af


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["stop_coef"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
