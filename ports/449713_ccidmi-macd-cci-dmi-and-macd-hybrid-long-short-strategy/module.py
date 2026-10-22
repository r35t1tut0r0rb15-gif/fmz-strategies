"""CCI (14) crossings of +-100 confirmed by the DMI and MACD (24, 52, 9), 1-hour bars: the CCI crossing over -100 with DI+ above DI- and the MACD over its signal goes long, the mirror at +100 goes short;
the CCI crossing over +100 closes a long, under -100 closes a short; reversing.
Port of FMZ strategy #449713 "CCIDMI和MACD混合多空策略-CCI-DMI-and-MACD-Hybrid-Long-Short-Strategy" (CCI, DMI, and MACD Strategy).

FMZ source id: 449713

Source
    https://www.fmz.com/strategy/449713 (PineScript v5, FMZ last modified 2024-04-28 13:52:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-143), CCI 14, levels 100 / -100; DMI 14 / 14; MACD 24 / 52 / 9
    crossover(cci, -100) and di+ > di- and macd > signal -> entry Buy;  crossover(cci, 100) -> close Buy;  crossunder(cci, 100) and di- > di+ and macd < signal -> entry Sell;  crossunder(cci, -100) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in the script's order: a close acts only on a position held into the bar and not
      reversed by that bar's entry. ta.cci uses the mean absolute deviation; ta.dmi uses Wilder
      smoothing. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI crossings with DMI and MACD confirmation, CCI exits.
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

NAME = "fmz_449713_cci_cross_dmi_macd_confirm_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_len": [14, 20],
    "level": [100.0, 150.0],
}
DEFAULT_PARAMS = {"cci_len": 14, "level": 100.0, "dmi_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    cci = (c - ma) / (0.015 * md)
    up, dn = h - h.shift(1), lo.shift(1) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    k = int(p["dmi_len"])
    atr = _rma(tr, k)
    dip, dim = 100 * _rma(pdm, k) / atr, 100 * _rma(mdm, k) / atr
    macd = c.ewm(span=24, adjust=False).mean() - c.ewm(span=52, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lv = float(p["level"])
    c1 = cci.shift(1)
    with np.errstate(invalid="ignore"):
        buy = ((cci > -lv) & (c1 <= -lv) & (dip > dim) & (macd > sig)).to_numpy()
        bx = ((cci > lv) & (c1 <= lv)).to_numpy()
        sell = ((cci < lv) & (c1 >= lv) & (dim > dip) & (macd < sig)).to_numpy()
        sxc = ((cci < -lv) & (c1 >= -lv)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            le[i], new = True, 1
        if bx[i] and pos == 1 and new == 1:          # a close acts only on a held, non-reversed long
            lx[i], new = True, 0
        if sell[i] and new != -1:
            se[i], le[i], lx[i], new = True, False, False, -1
        if sxc[i] and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
