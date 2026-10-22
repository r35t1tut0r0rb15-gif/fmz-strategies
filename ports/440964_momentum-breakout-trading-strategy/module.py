"""UT Bot trail crossings with a zero-lag LSMA and ADX filter, 5-minute bars: from flat, the EMA 2 crossing over the ATR trail (3 x ATR 10) with the close above the trail and the ZLSMA 50 and ADX 20 above
14 goes long, the mirror short; a 0.4 % close stop and a profit-protecting close once 1.5 % up; as written the short profit tracking uses the long threshold.
Port of FMZ strategy #440964 "Momentum Breakout Trading Strategy" (UT Bot Strategy).

FMZ source id: 440964

Source
    https://www.fmz.com/strategy/440964 (PineScript v4, FMZ last modified 2024-02-04 10:55:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 181-406), EMA 2; key value 3, ATR 10; Heikin-Ashi off; ADX 20 > 14; ZLSMA 50; minimum profit 1.5 %, give-back 1/10, stop 0.4 %
    trail = UT Bot ATR trail of close;  buy = close > trail and crossover(ema2, trail) and close > zlsma and adx > 14 and flat -> entry long;  sell mirrored -> entry short
    profit_price: 0 when flat; long: the highest close once close >= avg x 1.015; short: the lowest close while avg x 1.015 >= close (the long threshold, as written);  close long when close <= profit_price x (1 - 0.0015) and close >= avg x 1.015, or close <= avg x 0.996;  short mirrored (avg x 0.985, avg x 1.004)

Interpretation choices (Pine rules in SURVEY_README.md)
    * All exits are bar-close tests against the fill price, sent at the next open (not orders). The
      short side's profit price is updated with the long threshold as written, so it tracks the lowest
      close from the fill. The commented-out filters are not ported. Entries only from flat. Opposite
      entries cannot occur (entries only from flat). No sizing code. FREQ = "5min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested exits.
    2 generic: PASS, ATR trail, ZLSMA and ADX.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440964_ut_bot_zlsma_adx_profit_guard"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [3.0, 2.0],
    "adx_min": [14, 20],
}
DEFAULT_PARAMS = {"a": 3.0, "adx_min": 14, "c": 10, "ema_len": 2, "adx_len": 20, "zl_len": 50, "profit": 0.015,
                  "give_back": 10, "loss": 0.004}


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


def _linreg(y, n):
    """Pine linreg(y, n, 0): the least-squares line over the last n bars, valued at the current bar."""
    g = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sgy = (g * y).rolling(n).sum()
    sg = g.rolling(n).sum()
    sgg = (g * g).rolling(n).sum()
    slope = (n * sgy - sg * sy) / (n * sgg - sg * sg)
    return (sy - slope * sg) / n + slope * g


def _ut_trail(src, nloss):
    s, nl = src.to_numpy(dtype=float), nloss.to_numpy(dtype=float)
    out = np.full(len(s), np.nan)
    prev = 0.0
    for i in range(len(s)):
        p = prev
        s1 = s[i - 1] if i > 0 else np.nan
        if np.isnan(nl[i]):
            t = np.nan                                   # Pine max / min with na give na
        elif s[i] > p and s1 > p:
            t = max(p, s[i] - nl[i])
        elif s[i] < p and s1 < p:
            t = min(p, s[i] + nl[i])
        else:
            t = s[i] - nl[i] if s[i] > p else s[i] + nl[i]
        out[i] = t
        prev = 0.0 if np.isnan(t) else t
    return pd.Series(out, index=src.index)


def _adx(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    trr = _rma(tr, n)
    plus, minus = 100 * _rma(pdm, n) / trr, 100 * _rma(mdm, n) / trr
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    trail = _ut_trail(c, float(p["a"]) * _rma(tr, int(p["c"])))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    n = int(p["zl_len"])
    ls1 = _linreg(c, n)
    zl = 2 * ls1 - _linreg(ls1, n)
    adx = _adx(bars_df, int(p["adx_len"]))
    am = float(p["adx_min"])
    above = (e > trail) & (e.shift(1) <= trail.shift(1))
    below = (trail > e) & (trail.shift(1) <= e.shift(1))
    buy = ((c > trail) & above & (c > zl) & (adx > am)).to_numpy()
    sell = ((c < trail) & below & (c < zl) & (adx > am)).to_numpy()
    pr, gb, ls = float(p["profit"]), float(p["profit"]) / float(p["give_back"]), float(p["loss"])
    ov, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, x, pp = 0, np.nan, 0.0
    for i in range(m):
        new = pos
        if pos == 0 and buy[i]:
            new = 1
        elif pos == 0 and sell[i]:
            new = -1
        if pos == 0:
            pp = 0.0
        elif pos == 1 and x * (1 + pr) <= cv[i] and (pp == 0 or pp < cv[i]):
            pp = cv[i]
        elif pos == -1 and x * (1 + pr) >= cv[i] and (pp == 0 or pp > cv[i]):
            pp = cv[i]
        if pos == 1 and ((pp > 0 and pp * (1 - gb) >= cv[i] and x * (1 + pr) <= cv[i]) or x * (1 - ls) >= cv[i]):
            new = 0
        if pos == -1 and ((pp > 0 and pp * (1 + gb) <= cv[i] and x * (1 - pr) >= cv[i]) or x * (1 + ls) <= cv[i]):
            new = 0
        if new != 0 and new != pos and i + 1 < m:
            x = ov[i + 1]                                # the fill of the new position
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
