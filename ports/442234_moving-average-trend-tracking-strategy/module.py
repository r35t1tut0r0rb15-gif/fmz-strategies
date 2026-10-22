"""+DI crossing over -DI with a 3 % trailing stop on highs, broker days, long only: the +DI (6) crossing over the -DI goes long; a stop 3 % under the highest previous high since entry closes.
Port of FMZ strategy #442234 "Moving Average Trend Tracking Strategy" (+DI Crossover).

FMZ source id: 442234

Source
    https://www.fmz.com/strategy/442234 (PineScript v5, FMZ last modified 2024-02-20 14:36:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-218), DI length 6; ADX smoothing 14 (plotted); ADX buying area 0-50 (unused); trail 3 %
    enterLong = crossover(plus, minus) ? plus : na -> entry EL;  longStopPrice = position open ? max(high[1] (1 - 3 %), longStopPrice[1]) : 0;  strategy.exit(stop = longStopPrice) while open

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop ratchets on the previous bar's high, 3 % under it: a percent trailing stop on highs, the
      house trail {"type": "percent", "pct": 0.03, "anchor": "high_low"} (its best high runs to the
      previous minute rather than the previous bar; stated approximation, mark trailing_stop). The ADX
      limits are not used by the orders. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, DI crossings and a percent trail on highs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442234_plus_di_cross_pct_trail_long"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "di_len": [6, 14],
    "trail_pct": [0.03, 0.05],
}
DEFAULT_PARAMS = {"di_len": 6, "trail_pct": 0.03}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["di_len"])
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    le = (plus > minus) & (plus.shift(1) <= minus.shift(1)) & (plus != 0)
    false = pd.Series(False, index=c.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
