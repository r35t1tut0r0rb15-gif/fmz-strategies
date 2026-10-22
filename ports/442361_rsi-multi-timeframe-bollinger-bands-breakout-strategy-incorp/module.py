"""Three closes outside a Bollinger band with vortex and RSI extremes, 1-hour bars: three closes above the upper band (20, 2) with VI+ over 1.25, VI- under 0.7 and the RSI over 70 go short, the mirror
goes long; a long closes when the close is above the upper band, a short when it is under the lower band; reversing.
Port of FMZ strategy #442361 "基于布林带突破和RSI指标的多时间框架趋势策略Multi-timeframe-Bollinger-Bands-Breakout-Strategy-Incorporating-RSI" (truongphuthinh).

FMZ source id: 442361

Source
    https://www.fmz.com/strategy/442361 (PineScript v5, FMZ last modified 2024-02-21 13:59:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-212), BB 20 / 2; vortex 14; RSI 14 (70 / 30); 15-minute bar check
    isClosedBar = change(time("15"));  if isClosedBar[1..3]: close[1..3] > upper[1..3] and VIP > 1.25 and VIM < 0.7 and rsi > 70 -> entry Short;  close[1..3] < lower[1..3] and VIP < 0.7 and VIM > 1.25 and rsi < 30 -> entry Long
    long and close > upper -> close Long;  short and close < lower -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * change(time("15")) is non-zero on every 1-hour bar (each starts a new 15-minute period), so the bar
      check always passes. atr(1) is the bar's true range. A close acts only on the held position. Pine's
      stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three-bar band excursions with vortex and RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG442361 (2 members, best partner #443138, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442361_three_close_band_excursion_vortex_rsi_fade"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "period": [14, 21],
}
DEFAULT_PARAMS = {"length": 20, "period": 14, "mult": 2.0, "rsi_len": 14, "ob": 70, "os": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    k = int(p["period"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    strv = tr.rolling(k).sum()
    vip = (h - lo.shift(1)).abs().rolling(k).sum() / strv
    vim = (lo - h.shift(1)).abs().rolling(k).sum() / strv
    r = _rsi(c, int(p["rsi_len"]))
    above3 = (c.shift(1) > up.shift(1)) & (c.shift(2) > up.shift(2)) & (c.shift(3) > up.shift(3))
    below3 = (c.shift(1) < dn.shift(1)) & (c.shift(2) < dn.shift(2)) & (c.shift(3) < dn.shift(3))
    es = (above3 & (vip > 1.25) & (vim < 0.7) & (r > float(p["ob"]))).to_numpy()
    el = (below3 & (vip < 0.7) & (vim > 1.25) & (r < float(p["os"]))).to_numpy()
    xl, xs = (c > up).to_numpy(), (c < dn).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if es[i] and new != -1:
            new = -1
        if el[i] and new != 1:
            new = 1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
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
