"""ABCD harmonic pattern, 45-minute bars: a zigzag of 5-bar fractal pivots; when the last legs form an
ABCD (BC 0.382-0.886 of AB, CD 1.13-2.618 of BC) ending below C go long, ending above C go short.
Each side has a take-profit and a stop-loss a fixed distance from the signal close.
Port of FMZ strategy #427727 "Momentum ABCD Pattern Strategy" (Daveatt).

FMZ source id: 427727

Source
    https://www.fmz.com/strategy/427727 (PineScript v4, FMZ last modified 2023-09-24 13:08:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 168-298), filterBW false, TP 100 / SL 20 USD
    top / bottom fractal confirmed 2 bars after the pivot (isBWFractal, as the source's switch reads)
    zigzag = pivot high[2] on a top after a bottom, pivot low[2] on a bottom after a top
    a, b, c, d = the last four zigzag values; abc = |b - c| / |a - b|; bcd = |c - d| / |b - c|
    bull = abc in [0.382, 0.886] and bcd in [1.13, 2.618] and d < c (first bar) -> entry long; bear d > c -> short
    exit(limit = signal close +- 100, stop = signal close -+ 20) for the side in trend

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fractals use bars up to the current one (the pivot two bars back): no look-ahead. The
      unused lookahead_on variable in f_abcd() never reaches a security() call.
    * Criterion 2: the USD distances (fx factor 1 for crypto) become `tp_atr` / `sl_atr` x Wilder
      ATR(14) of the signal bar (as fractions of its close, shifted one bar inside stops(), re-based
      on the fill). On the source's 45-minute BTC bars 100 / 20 USD is about 0.7 / 0.15 ATR
      (judgement before any backtest).
    * Pine's exits need buy_trend / sell_trend, which are na until both a long and a short signal
      have occurred; the port's bracket applies from the first trade (stated approximation).
    * The strategy() line is commented out: Pine defaults (one position).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, USD distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() sizing stored; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_427727_abcd_fractal_zigzag"
FAMILY = "harmonic_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.7, 2.0],
    "sl_atr": [0.15, 1.0],
}
DEFAULT_PARAMS = {"tp_atr": 0.7, "sl_atr": 0.15, "atr_length": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    h, lo = bars_df["high"], bars_df["low"]
    H = lambda k: h.shift(k)
    L = lambda k: lo.shift(k)
    # isBWFractal (selected when filterBW is false, as written)
    top = ((H(4) < H(2)) & (H(3) <= H(2)) & (H(2) >= H(1)) & (H(2) > h)).to_numpy()
    bot = ((L(4) > L(2)) & (L(3) >= L(2)) & (L(2) <= L(1)) & (L(2) < lo)).to_numpy()
    tc, bc = _barssince(top), _barssince(bot)
    tc1, bc1 = np.concatenate(([np.nan], tc[:-1])), np.concatenate(([np.nan], bc[:-1]))
    h2, l2 = H(2).to_numpy(), L(2).to_numpy()
    m = len(top)
    with np.errstate(invalid="ignore"):
        zz = np.where(top & (tc1 > bc1), h2, np.where(bot & (tc1 < bc1), l2, np.nan))
    bull_c = np.zeros(m, dtype=bool)
    bear_c = np.zeros(m, dtype=bool)
    pts = []
    for i in range(m):
        if not np.isnan(zz[i]) and zz[i] != 0:
            pts.append(zz[i])
        if len(pts) >= 4:
            a, b, c, d = pts[-4], pts[-3], pts[-2], pts[-1]
            with np.errstate(divide="ignore", invalid="ignore"):
                abc = abs(b - c) / abs(a - b)
                bcd = abs(c - d) / abs(b - c)
            ok = (0.382 <= abc <= 0.886) and (1.13 <= bcd <= 2.618)
            bull_c[i] = ok and d < c
            bear_c[i] = ok and d > c
    prev_b = np.concatenate(([False], bull_c[:-1]))
    prev_s = np.concatenate(([False], bear_c[:-1]))
    idx = bars_df.index
    le = pd.Series(bull_c & ~prev_b, index=idx)
    se = pd.Series(bear_c & ~prev_s, index=idx)
    false = pd.Series(False, index=idx)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    pc = bars_df["close"].shift(1)
    tr = pd.concat([bars_df["high"] - bars_df["low"], (bars_df["high"] - pc).abs(),
                    (bars_df["low"] - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
