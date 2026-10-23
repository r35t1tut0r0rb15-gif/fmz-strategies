"""One-minute bars: WaveTrend (channel 10, average 21) under -60 with the Chaikin money flow 20 under -0.20 goes long, WaveTrend over 60 with it over 0.20 goes short; the money flow over 0.18 closes a long, under -0.18 closes a short; reversing.
Port of FMZ strategy #432343 "WaveTrend and CMF Based Trend Following Strategy" (CMF - WaveTrend).

FMZ source id: 432343

Source
    https://www.fmz.com/strategy/432343 (PineScript v3, FMZ last modified 2023-11-16 16:38:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 141-198), CMF 20, SUM, volume exponent 10 (= volume), no price factor; WaveTrend 10 / 21; levels -60 / 60, CMF 0.20 entry, 0.18 exit
    cmf = sum(ad, 20) / sum(wv, 20), ad = (2 close - (trh + trl)) / tr(true) x volume (0 when trh == trl);  wt1 = ema((hlc3 - esa) / (0.015 d), 21)
    wt1 < -60 and cmf < -0.20 -> entry long;  wt1 > 60 and cmf > 0.20 -> entry short;  cmf > 0.18 -> close long;  cmf < -0.18 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume exponent 10 / 10 = 1 leaves the volume as it is, and the price factor is off. trl / trh are
      the low / high widened to the previous close, and tr(true) is the true range with the first bar's
      high - low. "Show in Percentage" is off, so cmf_p = cmf. A close acts only on a position the bar's
      entries leave unchanged (call order); the entry conditions cannot both hold. REVERSAL INTENDED.
      100 % of equity is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WaveTrend extremes with a money-flow confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, pyramiding 0, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Chaikin money flow (volume-weighted close location over 20 bars); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432343_wavetrend_extreme_cmf20_confirm_cmf_exit_reversal"
FAMILY = "wavetrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wt_level": [60.0, 53.0],
    "cmf_len": [20, 40],
}
DEFAULT_PARAMS = {"wt_level": 60.0, "cmf_len": 20, "n1": 10, "n2": 21, "cmf_entry": 0.20, "cmf_exit": 0.18}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    pc = c.shift(1)
    trl = pd.concat([lo, pc], axis=1).min(axis=1, skipna=False)
    trh = pd.concat([h, pc], axis=1).max(axis=1, skipna=False)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # tr(true): first bar high - low
    ad = pd.Series(np.where(trh == trl, 0.0, (2 * c - (trh + trl)) / tr.where(tr != 0)), index=c.index) * v
    ad = ad.where(trh.notna())
    n = int(p["cmf_len"])
    sv = v.rolling(n).sum()
    cmf = ad.rolling(n).sum() / sv.where(sv != 0)
    ap = (h + lo + c) / 3
    n1 = int(p["n1"])
    esa = _ema(ap, n1)
    d = _ema((ap - esa).abs(), n1)
    wt1 = _ema((ap - esa) / (0.015 * d.where(d != 0)), int(p["n2"]))
    lv, ce, cx = float(p["wt_level"]), float(p["cmf_entry"]), float(p["cmf_exit"])
    long_c = ((wt1 < -lv) & (cmf < -ce)).to_numpy()
    short_c = ((wt1 > lv) & (cmf > ce)).to_numpy()
    close_l = (cmf > cx).to_numpy()
    close_s = (cmf < -cx).to_numpy()
    m = len(long_c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        tgt = 1 if long_c[i] else (-1 if short_c[i] else 0)
        if tgt != 0 and tgt != pos:
            if tgt == 1:
                le[i] = True
            else:
                se[i] = True
            pos = tgt
        elif pos == 1 and close_l[i]:
            lx[i], pos = True, 0
        elif pos == -1 and close_s[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
