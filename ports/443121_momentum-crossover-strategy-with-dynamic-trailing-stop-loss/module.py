"""EMA 9 / 21 crossings confirmed by the DMI, daily bars: a cross up with +DI above -DI (or +DI non-zero with the ADX above -DI) goes long, the mirror short; the opposite EMA crossing closes; reversing.
Port of FMZ strategy #443121 "Momentum Crossover Strategy with Dynamic Trailing Stop Loss" (Combined EMA and DMI Strategy with Enhanced Table).

FMZ source id: 443121

Source
    https://www.fmz.com/strategy/443121 (PineScript v5, FMZ last modified 2024-02-29 13:55:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-175), EMA 9 / 21; DI 17, ADX smoothing 17 (DI over the bar's own true range); risk percentage (unused)
    +DI / -DI = fixnan(100 rma(DM, 17) / tr) (the bar's true range, unsmoothed);  ADX = 100 rma(|+DI - -DI| / sum, 17)
    long = emaCrossUp and (+DI > -DI or (+DI and ADX > -DI)) -> entry Long;  short mirrored -> entry Short;  cross down -> close Long;  cross up -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DI lines divide by the bar's own true range, not a smoothed one, as written. "up and ..." tests
      +DI as a boolean (non-zero). The closes repeat the reversals when the entries fire and otherwise
      close on the crossing. Ported in call order with one position at a time. The table only displays.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a DMI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443121_ema9_21_cross_dmi_confirm_reversal"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ema": [9, 5],
    "di_len": [17, 14],
}
DEFAULT_PARAMS = {"short_ema": 9, "di_len": 17, "long_ema": 21, "adx_len": 17}


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
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]) or np.isinf(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    cu = ((es > el) & (es.shift(1) <= el.shift(1))).to_numpy()
    cd = ((es < el) & (es.shift(1) >= el.shift(1))).to_numpy()
    n = int(p["di_len"])
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = _fixnan(100 * _rma(pdm, n) / tr)
        minus = _fixnan(100 * _rma(mdm, n) / tr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), int(p["adx_len"]))
    buy_dmi = ((plus > minus) | ((plus != 0) & plus.notna() & (adx > minus))).to_numpy()
    sell_dmi = ((minus > plus) | ((minus != 0) & minus.notna() & (adx > plus))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if cu[i] and buy_dmi[i] and new != 1:
            new = 1
        if cd[i] and sell_dmi[i] and new != -1:
            new = -1
        if cd[i] and held == 1 and new == 1:
            new = 0
        if cu[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
