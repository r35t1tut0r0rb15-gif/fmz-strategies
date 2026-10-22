"""Stochastic 14 extremes from flat with spacing, daily bars: %K under 20 goes long and over 80 goes short, only from flat and at least 20 bars after the last entry, each with a stop and target 2 ATR 14 from the signal close.
Port of FMZ strategy #454334 "Volatility Range Trading Strategy Based on Stochastic Oscillator" (Range Trading with Stochastic).

FMZ source id: 454334

Source
    https://www.fmz.com/strategy/454334 (PineScript v5, FMZ last modified 2024-06-17 14:52:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-147), %K 14 (SMA 3), %D 3; levels 80 / 20; ATR 14; stop / target 2 ATR; 20 bars between trades; quantity 1
    k < 20 and flat and bars since last entry >= 20 -> entry Long, exit(stop = close - 2 atr, limit = close + 2 atr), lastTradeBar = bar_index
    k > 80 and flat and spacing -> entry Short, exit(stop = close + 2 atr, limit = close - 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed on the signal bar: ported as the fraction 2 x ATR / close of the signal
      bar, applied to the fill and followed in the loop on each bar's high / low so the flat test lines
      up. The spacing counts from the last entry bar (0 at the start). Opposite entries cannot occur
      (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars:
      mark coarse_bar_stop. The quantity 1 is sizing. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ATR bracket as fractions of the signal close.
    2 generic: PASS, stochastic extremes with entry spacing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 1 stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_454334_stoch_extreme_spaced_from_flat_atr_bracket"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stoch_len": [14, 7],
    "gap_bars": [20, 5],
    "atr_mult": [2.0, 1.0],
}
DEFAULT_PARAMS = {"stoch_len": 14, "gap_bars": 20, "atr_mult": 2.0, "atr_len": 14, "ob": 80.0, "os": 20.0}


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


def _atr_frac(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n)) / c


def _run(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["stoch_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    k = (100 * (c - ll) / rng.where(rng > 0)).rolling(3).mean().to_numpy()
    fr = (float(p["atr_mult"]) * _atr_frac(bars_df, p["atr_len"])).to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    gap = int(p["gap_bars"])
    ob, os_ = float(p["ob"]), float(p["os"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, fi, kf, last = 0, 0, -1, np.nan, 0
    for i in range(m):
        if pend in (1, -1):
            pos, fi, kf = pend, i, fr[i - 1]
        pend = 0
        if pos != 0 and (lv[i] <= ov[fi] * (1 - kf) or hv[i] >= ov[fi] * (1 + kf)):
            pos = 0
        if pos == 0 and i - last >= gap and i + 1 < m:
            if k[i] < os_:
                le[i], pend, last = True, 1, i
            elif k[i] > ob:
                se[i], pend, last = True, -1, i
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["atr_mult"]) * _atr_frac(bars_df, p["atr_len"])
    return {"sl_stop": a.shift(1), "tp_stop": a.shift(1)}


def portfolio_kwargs(**params):
    return {}
