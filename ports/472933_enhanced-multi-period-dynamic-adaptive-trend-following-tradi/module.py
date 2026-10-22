"""EMA 9 / 21 crossings with RSI and ADX filters, daily bars, long only: the cross up with the RSI under 60 and the ADX 14 over 15 buys; the cross down with the RSI over 40 and the ADX over 15 sells. Same rules as #471697 with an ADX threshold of 15 (near-duplicate group, rule 7).
Port of FMZ strategy #472933 "Enhanced Multi Period Dynamic Adaptive Trend Following Trading System" (Enhanced EMA + RSI + ADX Strategy (Focused on 70% Win Rate)).

FMZ source id: 472933

Source
    https://www.fmz.com/strategy/472933 (PineScript v5, FMZ last modified 2024-11-25 10:58:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-140), EMA 9 / 21; RSI 14, levels 60 / 40; DMI 14 with ADX smoothing 1, threshold 15; bracket from the average price x risk / reward 1.5
    crossover(ema9, ema21) and rsi < 60 and adx > 15 -> entry Buy + exit(limit = avg + (close - avg) x 1.5, stop = avg - (close - avg))
    crossunder(ema9, ema21) and rsi > 40 and adx > 15 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rules are those of #471697 (C210) with the ADX threshold 15 and a 1.5 risk / reward. The exit
      levels use strategy.position_avg_price on the signal bar, na from flat, so the entry's own bracket
      is never placed; only a cross-up while a long is still held would arm one (as #437800: not ported,
      mark trailing_stop_pending). ADX smoothing 1 is the plain DX. Long only. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the bracket armed only by a repeat signal not ported (mark).
    2 generic: PASS, EMA crossings with RSI and ADX filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND471697 (2 members, best partner #471697, Jaccard 0.676); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_472933_ema9_21_cross_rsi_adx15_filter_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
    "adx_th": [15, 20],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "adx_th": 15, "rsi_len": 14, "adx_len": 14, "adx_smooth": 1}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _adx(b, n, sm):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), sm)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    adx = _adx(bars_df, int(p["adx_len"]), int(p["adx_smooth"]))
    th = float(p["adx_th"])
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 60) & (adx > th)
    lx = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 40) & (adx > th)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
