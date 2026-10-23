"""Regular and hidden divergences of an SMA-based MACD histogram (12 / 26 / 9) at 5-bar fractals, confirmed by Murrey's Math oscillator (100-bar Donchian) over its second quadrant, hourly bars: bullish divergences with the oscillator over 0.25 a bar earlier go long, bearish ones under -0.25 go short; the oscillator crossing to the other side of 0 closes; reversing.
Port of FMZ strategy #366935 "Price Divergence Strategy v10" ([STRATEGY][UL]Price Divergence Strategy v1.1).

FMZ source id: 366935

Source
    https://www.fmz.com/strategy/366935 (PineScript v4, FMZ last modified 2022-05-31 18:31:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 85-253), method 1 (MACD: SMA 12 / 26, EMA 9 signal, histogram); MMLO 100, quadrant 2; trailing 100 points without an offset; pyramiding 0; 10 % of equity
    fractal_top = top fractal of hist ? hist[2] : na;  regular bear = fractal_top and high[2] > valuewhen(fractal_top, high[2], 1) and hist[2] < valuewhen(fractal_top, hist[2], 1);  hidden bear mirror;  bull divergences at bottom fractals
    osc = (close - midline) / (range / 2) of the 100-bar Donchian;  bull div and osc[1] > 0.25 -> entry Buy;  osc <= 0 -> close Buy;  bear div and osc[1] < -0.25 -> entry Sell;  osc >= 0 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The method input takes its default, 1 (MACD), so the volume and acc / dist branches (computed every
      bar) feed nothing: volume is not used. The fractal value of 0 counts as false, as Pine. The trailing
      stop has trail_points 100 and no offset, which places no trail (as #441084). The calls run in source
      order (entry Buy, close Buy, entry Sell, close Sell): a close acts only on a position held into the bar
      and not reversed on it (as #441963): a loop. REVERSAL INTENDED. The 10 % of equity size is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD-histogram divergences with a Donchian oscillator filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital 10000 stored, not ported.
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

NAME = "fmz_366935_macd_hist_fractal_divergence_mmlo_quadrant_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "quad": [2, 1],
}
DEFAULT_PARAMS = {"length": 100, "quad": 2, "macd_fast": 12, "macd_slow": 26, "macd_smooth": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.rolling(int(p["macd_fast"])).mean() - c.rolling(int(p["macd_slow"])).mean()
    hist = macd - macd.ewm(span=int(p["macd_smooth"]), adjust=False).mean()
    s1, s2, s3, s4 = (hist.shift(k) for k in (1, 2, 3, 4))
    top = ((s4 < s2) & (s3 < s2) & (s2 > s1) & (s2 > hist) & (s2 != 0)).to_numpy()
    bot = ((s4 > s2) & (s3 > s2) & (s2 < s1) & (s2 < hist) & (s2 != 0)).to_numpy() & ~top   # top wins in f_fractalize
    h2, l2, s2v = h.shift(2).to_numpy(dtype=float), lo.shift(2).to_numpy(dtype=float), s2.to_numpy(dtype=float)
    hp, hpr = _valuewhen(top, s2v, 1), _valuewhen(top, h2, 1)
    lp, lpr = _valuewhen(bot, s2v, 1), _valuewhen(bot, l2, 1)
    reg_bear = top & (h2 > hpr) & (s2v < hp)
    hid_bear = top & (h2 < hpr) & (s2v > hp)
    reg_bull = bot & (l2 < lpr) & (s2v > lp)
    hid_bull = bot & (l2 > lpr) & (s2v < lp)
    n = int(p["length"])
    hi, lw = h.rolling(n).max(), lo.rolling(n).min()
    rng = hi - lw
    osc = (c - (lw + rng * 0.5)) / (rng / 2)
    q = int(p["quad"])
    o1 = osc.shift(1)
    up_q = (o1 > 0) & (o1 > 0.125 * 2 * (q - 1)) if q > 1 else (o1 > 0)
    dn_q = (o1 < 0) & (o1 < -0.125 * 2 * (q - 1)) if q > 1 else (o1 < 0)
    le_c = (reg_bull | hid_bull) & up_q.to_numpy()
    se_c = (reg_bear | hid_bear) & dn_q.to_numpy()
    lx_c, sx_c = (osc <= 0).to_numpy(), (osc >= 0).to_numpy()
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
