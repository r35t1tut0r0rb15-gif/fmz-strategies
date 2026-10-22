"""Averaged-midline Tenkan / Kijun crossings or a close above both spans with MACD and RSI confirmation, daily bars, long only: either goes long; a Tenkan cross down, or a close under both spans,
closes.
Port of FMZ strategy #449971 "MACD-RSI-一目均衡Ichimoku动量趋势多头策略-MACD-RSI-Ichimoku-Momentum-Trend-Following-Long-Strategy" (MACD RSI Ichimoku Strategy (Julien_Eche)).

FMZ source id: 449971

Source
    https://www.fmz.com/strategy/449971 (PineScript v5, FMZ last modified 2024-04-30 17:42:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 111-167), Tenkan 9, Kijun 26, Span 52 (as SMAs of high + low); Span A shifted 26; MACD 12 / 26 / 9; RSI 14; Buy/Sell off
    tenkan = sma(high + low, 9) / 2;  kijun = sma(high + low, 26) / 2;  spanA = ((tenkan + kijun) / 2)[26];  spanB = sma(high + low, 52) / 2
    crossover(tenkan, kijun) or (close > spanA and close > spanB and macd > signal and rsi < 70) -> entry Buy;  crossunder(tenkan, kijun) or (close < spanA and close < spanB) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are SMAs of high + low (not Donchian midlines); Span A is 26 bars back, Span B is not
      shifted, as written. With Buy/Sell off the exit only closes. A same-bar close only acts on a held
      long. Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; Span A from 26 bars back.
    2 generic: PASS, Ichimoku-style crossings and cloud side with MACD / RSI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449971_sma_ichimoku_cross_or_cloud_macd_rsi_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [9, 20],
    "len2": [26, 50],
}
DEFAULT_PARAMS = {"len1": 9, "len2": 26, "len3": 52, "rsi_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl = h + lo
    l2 = int(p["len2"])
    tenkan = hl.rolling(int(p["len1"])).mean() / 2
    kijun = hl.rolling(l2).mean() / 2
    span_a = ((tenkan + kijun) / 2).shift(l2)
    span_b = hl.rolling(int(p["len3"])).mean() / 2
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    xo = (tenkan > kijun) & (tenkan.shift(1) <= kijun.shift(1))
    xu = (tenkan < kijun) & (tenkan.shift(1) >= kijun.shift(1))
    go = (xo | ((c > span_a) & (c > span_b) & (macd > sig) & (r < 70))).to_numpy()
    out = (xu | ((c < span_a) & (c < span_b))).to_numpy()
    m = len(go)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
