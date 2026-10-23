"""WaveTrend (9 / 12 / 3 of hlc3) line order, 2-hour bars: WT1 over WT2 holds a long, WT2 over WT1 a short; a long also closes on an overbought down-cross or a bearish WT divergence, a short on an oversold up-cross or a bullish divergence; reversing.
Port of FMZ strategy #363822 "VuManChu Cipher B Divergences Strategy" (VuManChu Cipher B Divergences Strategy).

FMZ source id: 363822

Source
    https://www.fmz.com/strategy/363822 (PineScript v4, FMZ last modified 2022-05-17 15:24:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 121-756), WT channel 9, average 12, MA 3 of hlc3; OB / OS 53 / -53; divergences at WT fractals (45 / -65 and 15 / -40)
    long_entry = wt2 < wt1;  long_exit = wt2 - wt1 > 0 or (wtCross and wtCrossDown and wt2 >= 53) or wtBearDiv or wtBearDiv_add
    short_entry = wt2 > wt1;  short_exit = wt2 - wt1 <= 0 or (wtCross and wtCrossUp and wt2 <= -53) or wtBullDiv or wtBullDiv_add

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "MFI" area of this script is an SMA of the candle body / range (no volume) and the
      volume-accelerated energy part feeds only commented-out conditions, so volume is not used. The
      divergences are the source's 5-bar fractals of WT2 (top when WT2[2] beats the two bars on each side)
      with the price and WT values at the previous fractal (valuewhen(..., 0)[2]); the RSI and stochastic
      divergences are switched off. The calls run in source order (entry long, close long, entry short,
      close short): a close acts only on a position held into the bar and not reversed on it (as #441963):
      a loop. The strategy() line is commented out; FMZ runs it with its defaults. REVERSAL INTENDED. No
      sizing code. The source carries the Mozilla Public License 2.0 notice. FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WaveTrend line order with cross and divergence exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the commented strategy() line: cash 10000).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG363822 (2 members, best partner #438943, Jaccard 0.981); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363822_wavetrend_line_order_divergence_exit_reversal"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wt_channel_len": [9, 14],
    "wt_average_len": [12, 21],
}
DEFAULT_PARAMS = {"wt_channel_len": 9, "wt_average_len": 12, "wt_ma_len": 3, "ob_level": 53, "os_level": -53}


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


def _valuewhen(cond, val, k):
    """Pine valuewhen(cond, val, k): val at the k-th most recent bar where cond held (k = 0 latest)."""
    cond = np.asarray(cond, dtype=bool)
    val = np.asarray(val, dtype=float)
    out = np.full(len(cond), np.nan)
    hits = []
    for i in range(len(cond)):
        if cond[i]:
            hits.append(val[i])
        if len(hits) > k:
            out[i] = hits[-1 - k]
    return out


def _lag(a, k):
    out = np.full(len(a), np.nan)
    out[k:] = a[:-k] if k else a
    return out


def _divs(src, hi, lo, top_lim, bot_lim):
    """The source's f_findDivs(src, top, bot, true): regular bear / bull divergences at 5-bar fractals."""
    s2, s3, s4, s1 = src.shift(2), src.shift(3), src.shift(4), src.shift(1)
    top = (s4 < s2) & (s3 < s2) & (s2 > s1) & (s2 > src) & (s2 >= top_lim) & (s2 != 0)
    bot = (s4 > s2) & (s3 > s2) & (s2 < s1) & (s2 < src) & (s2 <= bot_lim) & (s2 != 0)
    s2v, h2, l2 = s2.to_numpy(dtype=float), hi.shift(2).to_numpy(dtype=float), lo.shift(2).to_numpy(dtype=float)
    t, b = top.to_numpy(), bot.to_numpy()
    high_prev, high_price = _lag(_valuewhen(t, s2v, 0), 2), _lag(_valuewhen(t, h2, 0), 2)
    low_prev, low_price = _lag(_valuewhen(b, s2v, 0), 2), _lag(_valuewhen(b, l2, 0), 2)
    bear = t & (h2 > high_price) & (s2v < high_prev)
    bull = b & (l2 < low_price) & (s2v > low_prev)
    return bear, bull


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo + c) / 3
    n = int(p["wt_channel_len"])
    esa = src.ewm(span=n, adjust=False).mean()
    de = (src - esa).abs().ewm(span=n, adjust=False).mean()
    ci = (src - esa) / (0.015 * de)
    wt1 = ci.ewm(span=int(p["wt_average_len"]), adjust=False).mean()
    wt2 = wt1.rolling(int(p["wt_ma_len"])).mean()
    cross = ((wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))) | ((wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1)))
    buy = (cross & (wt2 - wt1 <= 0) & (wt2 <= float(p["os_level"]))).to_numpy()
    sell = (cross & (wt2 - wt1 >= 0) & (wt2 >= float(p["ob_level"]))).to_numpy()
    bear1, bull1 = _divs(wt2, h, lo, 45, -65)
    bear2, bull2 = _divs(wt2, h, lo, 15, -40)
    le_c = (wt2 < wt1).to_numpy()
    se_c = (wt2 > wt1).to_numpy()
    lx_c = (wt2 - wt1 > 0).to_numpy() | sell | bear1 | bear2
    sx_c = (wt2 - wt1 <= 0).to_numpy() | buy | bull1 | bull2
    m = len(le_c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if le_c[i] and cur != 1:
            cur = 1
        if lx_c[i] and pos == 1 and cur == 1:
            cur = 0
        if se_c[i] and cur != -1:
            cur = -1
        if sx_c[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
