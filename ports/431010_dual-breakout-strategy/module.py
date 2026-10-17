"""Bollinger re-entries in a quiet market (tweakerID), 1-minute bars: the close crossing back above the lower band (20, 2)
with ADX 14 / DI 20 under 30 goes long, crossing back below the upper band goes short; ADX above 30 closes everything.
Port of FMZ strategy #431010 "Dual Breakout Strategy" (BB + ADX Strategy).

FMZ source id: 431010

Source
    https://www.fmz.com/strategy/431010 (PineScript v4, FMZ last modified 2023-11-03 17:16:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 146-214), BB 20 / 2, ADX smoothing 14, DI 20, level 30
    BUY = crossover(close, lower) and adx < 30 -> entry long;  SELL = crossunder(close, upper) and adx < 30 -> entry short
    adx > 30 -> close_all  (ADX Close on);  swing stop / target off (i_SL false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ADX as written (rma of +DM / -DM and the true range, fixnan). The swing-low / high stop option
      is off by default and not ported. "Reverse Trades" defaults to false and is fixed.
    * An entry and the close_all cannot meet on one bar (ADX under / over 30). strategy.entry
      reverses: REVERSAL INTENDED. stdev is the population deviation. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and an ADX level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
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

NAME = "fmz_431010_bb_reentry_low_adx"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "adx_level": [30, 20],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "adx_len": 14, "di_len": 20, "adx_level": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
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
    """Pine fixnan: an indicator value that is na keeps the last valid value (no bars are filled)."""
    v = x.to_numpy(dtype=float).copy()
    for i in range(1, len(v)):
        if np.isnan(v[i]):
            v[i] = v[i - 1]
    return pd.Series(v, index=x.index)


def _adx(bars, dilen, adxlen):
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=h.index).where(down.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    trr = _rma(tr, dilen)
    plus = _fixnan(100 * _rma(plus_dm, dilen) / trr)
    minus = _fixnan(100 * _rma(minus_dm, dilen) / trr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adxlen)


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
    c = bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + p["mult"] * sd, basis - p["mult"] * sd
    sig = _adx(bars_df, int(p["di_len"]), int(p["adx_len"]))
    lvl = float(p["adx_level"])
    buy = ((c > lower) & (c.shift(1) <= lower.shift(1)) & (sig < lvl)).to_numpy()
    sell = ((c < upper) & (c.shift(1) >= upper.shift(1)) & (sig < lvl)).to_numpy()
    out = (sig > lvl).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif sell[i]:
            pos = -1
        elif out[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
