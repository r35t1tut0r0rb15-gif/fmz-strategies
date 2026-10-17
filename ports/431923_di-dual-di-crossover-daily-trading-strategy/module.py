"""DI+ / DI- crosses (TheHulkTrading), broker days: +DI crossing above -DI goes long, below goes short; each position has a
1 ATR stop and a 2 ATR target from its entry price.
Port of FMZ strategy #431923 "基于DI交叉的日内交易策略Dual-DI-Crossover-Daily-Trading-Strategy" (DI Crossing Daily Straregy HulkTrading).

FMZ source id: 431923

Source
    https://www.fmz.com/strategy/431923 (PineScript v4, FMZ last modified 2023-11-13 11:32:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 196-226), DI 14, ATR 14, multiplier 1
    crossover(di+, di-) -> entry long;  crossunder -> entry short
    exit(stop = avg - 1 ATR, limit = avg + 2 ATR) re-issued every bar (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket distances follow the current ATR on every bar (a moving level): rule 2, mark
      trailing_stop_pending; the port fixes them at the signal bar's ATR 14 (Wilder), as fractions of
      its close, shifted one bar. DI as written (rma of +DM / -DM over rma(tr, 14), fixnan).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (rule 2).
    2 generic: PASS, DI crosses and ATR multiples.
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

NAME = "fmz_431923_di_cross_atr_bracket"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 28],
    "atr_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "atr_mult": 1.0}


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


def _fixnan(x):
    """Pine fixnan: an indicator value that is na keeps the last valid value (no bars are filled)."""
    v = x.to_numpy(dtype=float).copy()
    for i in range(1, len(v)):
        if np.isnan(v[i]):
            v[i] = v[i - 1]
    return pd.Series(v, index=x.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, down = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    rng = _rma(tr, 14)
    n = int(p["length"])
    pdm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    mdm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=h.index).where(down.notna())
    dp, dm = _fixnan(100 * _rma(pdm, n) / rng), _fixnan(100 * _rma(mdm, n) / rng)
    lg = ((dp > dm) & (dp.shift(1) <= dm.shift(1))).astype(bool)
    sh = ((dp < dm) & (dp.shift(1) >= dm.shift(1))).astype(bool)
    return lg, sh, rng / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    k = float(p["atr_mult"])
    return {"sl_stop": (af * k).shift(1), "tp_stop": (af * 2 * k).shift(1)}


def portfolio_kwargs(**params):
    return {}
