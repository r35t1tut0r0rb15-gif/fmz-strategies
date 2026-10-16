"""Noro VixFix + RSI, 2-day bars: a Williams Vix Fix spike with a fast RSI under 40 on a red candle goes long,
the spike with the RSI over 60 on a green candle goes short; a sizeable candle against the position closes it.
Port of FMZ strategy #428982 "Price Volatility Mean Reversion Strategy" (Noro's VixFix + RSI Strategy v1.0).

FMZ source id: 428982

Source
    https://www.fmz.com/strategy/428982 (PineScript v2, FMZ last modified 2023-10-11 16:03:36).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 193-255), VixFix 22, BB 20 x 2, percentile 50 x 0.85, RSI(7) limit 40
    wvf = (highest(close,22) - low) / highest(close,22) x 100; spike = wvf >= sma(wvf,20) + 2 stdev or wvf >= highest(wvf,50) x 0.85
    up = spike and fastrsi(7) < 40 and close < open -> close a short, entry long
    dn = spike and fastrsi(7) > 60 and close > open -> close a long, entry short
    exit = ((long and close > open) or (short and close < open)) and |close - open| > sma(|close - open|, 10) / 3 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 5 adds and the leverage lot are sizing (stored). stdev is the population deviation.
    * The exit tests the position held at the start of the bar. If an entry and the exit fall on the
      same bar, the entry's position is kept (stated reading of the close_all after the entry).
    * The date window is dropped (1900-2100). One-bar reversals: REVERSAL INTENDED.
    * Multi-day bars are blocks of 2 broker days (17:00 America/New_York) counted from 1970-01-01, each
      stamped with its first minute. FREQ = "2D" from the backtest header (period 2d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percentages, RSI levels and candle-body ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 5, leverage and the lot formula stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428982_noro_vixfix_rsi"
FAMILY = "volatility_spike_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [40, 30],
    "pd": [22, 11],
}
DEFAULT_PARAMS = {"limit": 40, "pd": 22, "bbl": 20, "mult": 2.0, "lb": 50, "ph": 0.85, "rsi_length": 7,
                  "body_length": 10, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
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


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    hc = c.rolling(int(p["pd"])).max()
    wvf = (hc - lo) / hc * 100
    n = int(p["bbl"])
    upper = wvf.rolling(n).mean() + p["mult"] * wvf.rolling(n).std(ddof=0)
    range_high = wvf.rolling(int(p["lb"])).max() * p["ph"]
    spike = (wvf >= upper) | (wvf >= range_high)
    d = c.diff()
    fu, fd = _rma(d.clip(lower=0), int(p["rsi_length"])), _rma((-d).clip(lower=0), int(p["rsi_length"]))
    rsi = pd.Series(np.where(fd == 0, 100.0, np.where(fu == 0, 0.0, 100 - 100 / (1 + fu / fd))), index=c.index)
    rsi = rsi.where(fu.notna() & fd.notna())
    body = (c - o).abs()
    big = (body > body.rolling(int(p["body_length"])).mean() / 3).to_numpy()
    up = (spike & (rsi < p["limit"]) & (c < o)).to_numpy()
    dn = (spike & (rsi > 100 - p["limit"]) & (c > o)).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        p0 = pos
        if up[i]:
            pos = 1
        if dn[i]:
            pos = -1
        if pos == p0 and big[i] and ((p0 > 0 and green[i]) or (p0 < 0 and red[i])):
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=idx)
    lx = pd.Series((prev == 1) & (tgt == 0), index=idx)
    se = pd.Series((tgt == -1) & (prev != -1), index=idx)
    sx = pd.Series((prev == -1) & (tgt == 0), index=idx)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
