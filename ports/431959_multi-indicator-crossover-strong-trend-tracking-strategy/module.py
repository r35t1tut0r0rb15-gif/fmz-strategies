"""Five oscillators of hlc3 over 100 bars all on the bullish side (RSI and a volume money-flow ratio above 50, CCI above 50, stochastic RSI K above 50) go long; all on the bearish side (RSI and money flow under 49, CCI under 0, K under 50) close; broker days, long only.
Port of FMZ strategy #431959 "Multi indicator Crossover Strong Trend Tracking Strategy" (something (SoftKill21)).

FMZ source id: 431959

Source
    https://www.fmz.com/strategy/431959 (PineScript v4, FMZ last modified 2023-11-13 16:59:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 152-203), length 100; src hlc3; K 1, D 1
    mf = 100 - 100 / (1 + sum(volume x up hlc3, 100) / sum(volume x down hlc3, 100));  rsi of hlc3 (rma 100);  cci = (src - sma) / (0.015 dev);  k = stoch(rsi(src, 100), 100)
    long = rsi > 50 and mf > 50 and cci > 50 and (k > 50 or d > 50) -> entry long;  short = rsi < 49 and mf < 49 and cci < 0 and (k < 50 or d < 50) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's _rsi(upper, lower) has two "if" lines whose values are discarded (a Pine function returns
      its last expression), so mf is always 100 - 100 / (1 + upper / lower); a zero falling flow gives no
      value (no signal on that bar), a zero rising flow gives 0. dev() is the mean absolute deviation from
      the SMA. With K and D smoothing 1, d = k. Long only: the short lines are commented out. The 100 % of
      equity and the commission are sizing and costs. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator agreement entries and exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 1000, commission 0.03 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the money-flow ratio mf (volume x hlc3 sums over 100 bars); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431959_rsi_mfi_cci_stochrsi_agreement_100_long"
FAMILY = "oscillator_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "cci_level": [50, 100],
}
DEFAULT_PARAMS = {"length": 100, "cci_level": 50.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _mean_dev(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        out[n - 1:] = np.abs(w - w.mean(axis=1, keepdims=True)).mean(axis=1)
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["length"])
    src = (h + lo + c) / 3
    ch = src.diff()
    upper = (v * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (v * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    mf = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))      # the formula only, as the source returns
    rsi = _rsi(src, n)
    cci = (src - src.rolling(n).mean()) / (0.015 * _mean_dev(src, n))
    lo_r, hi_r = rsi.rolling(n).min(), rsi.rolling(n).max()
    k = 100 * (rsi - lo_r) / (hi_r - lo_r).where(hi_r != lo_r)
    cl = float(p["cci_level"])
    long_c = ((rsi > 50) & (mf > 50) & (cci > cl) & (k > 50)).to_numpy()
    short_c = ((rsi < 49) & (mf < 49) & (cci < 0) & (k < 50)).to_numpy()
    m = len(long_c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and long_c[i]:
            le[i], pos = True, 1
        elif pos == 1 and short_c[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
