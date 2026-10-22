"""Fresh Ichimoku alignments with an ADX filter, 1-hour bars: a close at or above the cloud (spans 26 bars back), Tenkan above Kijun, span A above span B, ADX(14) above 20 and the close above its value 26
bars back, newly true, goes long; the mirror goes short; the close crossing back through the Kijun closes; reversing.
Port of FMZ strategy #439705 "Quantitative Trading Strategy Based on Ichimoku and ADX Indicators" (Ichimoku + ADX).

FMZ source id: 439705

Source
    https://www.fmz.com/strategy/439705 (PineScript v4, FMZ last modified 2024-01-23 11:14:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-299), Ichimoku 9 / 26 / 52 / 26; ADX 14 / DI 14, key level 23 (its tests unused); window() true
    Buy5 = close >= max(SSA[26], SSB[26]) and Tenkan - Kijun >= 0.001 and SSA > SSB and adx > 20 and close - close[26] >= 0.001 and not (the first three on the previous bar);  Sell5 mirror (close <= close[26])
    entry Buy on Buy5;  close Buy on crossunder(close, Kijun);  entry Sell on Sell5;  close Sell on crossover(close, Kijun)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 0.001 price-unit margins become fractions of the close; 2.4e-8 reads them on BTC
      near 42000 (in effect "greater than"). The closes act on the position held at the bar close: a
      close of the side just reversed out of meets no position and the reversal stands (as #438020).
      The ADX key-level tests (ABuy1 / ASell1) feed nothing. strategy.entry reverses: REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit margins -> fractions of the close.
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

NAME = "fmz_439705_ichimoku_fresh_alignment_adx20"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [20, 25],
    "base": [26, 30],
}
DEFAULT_PARAMS = {"adx_min": 20, "base": 26, "conversion": 9, "span_b": 52, "displacement": 26, "adxlen": 14,
                  "dilen": 14, "margin_frac": 2.4e-8}


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


def _fixnan(x):
    """Pine's fixnan: an undefined value takes the last defined one (leading values stay undefined)."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), -1)
    idx = np.maximum.accumulate(idx)
    out = np.where(idx >= 0, v[np.clip(idx, 0, None)], np.nan)
    return pd.Series(out, index=x.index)


def _adx(bars_df, dilen, adxlen):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where(up.isna(), np.where((up > dn) & (up > 0), up, 0.0))
    mdm = dn.where(dn.isna(), np.where((dn > up) & (dn > 0), dn, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, dilen)
    with np.errstate(divide="ignore", invalid="ignore"):
        pl = _fixnan(100 * _rma(pdm, dilen) / trr)
        mi = _fixnan(100 * _rma(mdm, dilen) / trr)
    s = pl + mi
    return 100 * _rma((pl - mi).abs() / s.where(s != 0, 1.0), adxlen)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def donch(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    tk, kj = donch(p["conversion"]), donch(p["base"])
    ssa, ssb = (tk + kj) / 2, donch(p["span_b"])
    d = int(p["displacement"])
    sad, sbd = ssa.shift(d), ssb.shift(d)
    top = pd.concat([sad, sbd], axis=1).max(axis=1, skipna=False)
    bot = pd.concat([sad, sbd], axis=1).min(axis=1, skipna=False)
    mg = float(p["margin_frac"]) * c
    sig = _adx(bars_df, int(p["dilen"]), int(p["adxlen"]))
    b1, b2, b3 = c >= top, (tk - kj) >= mg, ssa > ssb
    s1, s2, s3 = c <= bot, (kj - tk) >= mg, ssa < ssb
    strong = sig > float(p["adx_min"])
    b5 = b1 & b2 & b3 & strong & ((c - c.shift(d)) >= mg) & ~(b1.shift(1, fill_value=False) & b2.shift(1, fill_value=False) & b3.shift(1, fill_value=False))
    s5 = s1 & s2 & s3 & strong & (c <= c.shift(d)) & ~(s1.shift(1, fill_value=False) & s2.shift(1, fill_value=False) & s3.shift(1, fill_value=False))
    xl = ((c < kj) & (c.shift(1) >= kj.shift(1))).to_numpy()
    xs = ((c > kj) & (c.shift(1) <= kj.shift(1))).to_numpy()
    b5, s5 = b5.to_numpy(), s5.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if b5[i] and pos != 1:
            new = 1
        if pos == 1 and xl[i] and new == 1:
            new = 0
        if s5[i] and new != -1:
            new = -1
        if pos == -1 and xs[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
