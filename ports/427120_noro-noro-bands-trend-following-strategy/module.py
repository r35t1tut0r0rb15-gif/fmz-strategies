"""Noro's Bands v1.2: a channel centre (mid of the 20-bar highest / lowest close) +- the 20-bar mean
distance of the close from it sets a trend state; in an up state a red bar or a close under the
upper band goes long, in a down state a green bar or a close above the lower band goes short; a
"CryptoBottom" bar (red, a body far larger than usual, a new low of the body, fast RSI under 10)
also goes long.
Port of FMZ strategy #427120 "Noro Bands Trend Following Strategy".

FMZ source id: 427120

Source
    https://www.fmz.com/strategy/427120 (PineScript v2, FMZ last modified 2023-09-18 13:57:31).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 174-234), period 20, long and short on, colour on, CryptoBottom on
    center = (highest(close, 20) + lowest(close, 20)) / 2; distsma = sma(abs(close - center), 20)
    hd = center + distsma; ld = center - distsma
    trend = close < ld and high < hd ? -1 : close > hd and low > ld ? 1 : trend[1]
    up = trend == 1 and (close < open or close < hd); dn = trend == -1 and (close > open or close > ld)
    up2 = close < open and abs(close - sma(close, 10)) > 3 x sma(that, 100) and min(open, close) < its
          previous value and fastrsi < 10 (fastrsi = RSI with rma 2 of the close changes)
    up or up2 -> entry long; dn -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (no other exit). On a bar with both a long and a
      short condition, the entry on the side not already held is taken (the held side's entry is
      ignored, as Pine ignores a same-direction entry with pyramiding 0); from flat, long first.
    * trend[1] is na until the first state; "color" true means the colour test is used as written.
    * Highest / lowest include the current bar (Pine). fastrsi: down == 0 ? 100 : up == 0 ? 0 : RSI.
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts and a ratio of averages (no price levels).
    3 crypto-exchange-only: no ("CryptoBottom" is a candle rule; exchange pair in the header only).
    4 signals only: 100 % of equity per trade stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: DG427120 (3 members, best partner #435898, Jaccard 0.892); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427120_noro_bands"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
    "use_cb": [True, False],
}
DEFAULT_PARAMS = {"length": 20, "use_cb": True, "use_color": True}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ch = c.diff()
    fu = _rma(ch.clip(lower=0), 2).to_numpy()
    fd = _rma((-ch).clip(lower=0), 2).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        frsi = np.where(fd == 0, 100.0, np.where(fu == 0, 0.0, 100 - 100 / (1 + fu / fd)))
    frsi[np.isnan(fu) | np.isnan(fd)] = np.nan
    lencb = (c - c.rolling(10).mean()).abs()
    sma_cb = lencb.rolling(100).mean()
    body_min = pd.concat([o, c], axis=1).min(axis=1)
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    distsma = (c - center).abs().rolling(n).mean()
    hd, ld = (center + distsma).to_numpy(), (center - distsma).to_numpy()
    cv, ov, hv, lv = (x.to_numpy(dtype=float) for x in (c, o, h, lo))
    m = len(cv)
    trend = np.zeros(m, dtype=np.int8)   # 0 = na
    for i in range(m):
        if cv[i] < ld[i] and hv[i] < hd[i]:
            trend[i] = -1
        elif cv[i] > hd[i] and lv[i] > ld[i]:
            trend[i] = 1
        else:
            trend[i] = trend[i - 1] if i else 0
    use_color = bool(p["use_color"])
    up = (trend == 1) & ((cv < ov) | (not use_color) | (cv < hd))
    dn = (trend == -1) & ((cv > ov) | (not use_color) | (cv > ld))
    up2 = ((c < o) & (lencb > sma_cb * 3) & (body_min < body_min.shift(1))).to_numpy() & (frsi < 10)
    long_c = up | (up2 & bool(p["use_cb"]))
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif dn[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
