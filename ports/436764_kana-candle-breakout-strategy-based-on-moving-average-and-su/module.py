"""SMA trend with ATR bands, Heikin-Ashi colour, a slow MACD and a 4-hour range position, 1-hour bars: a rising SMA 20 above the EMA 200, a green previous Heikin-Ashi candle, the close under the first upper band, a
positive MACD histogram and the close more than 100 ranges above the 4-hour range of 240 bars ago go long; the mirror goes short; exits at the outer or second opposite band, reversing.
Port of FMZ strategy #436764 "Kana Candle Breakout Strategy Based on Moving Average and Support Resistance" (KANA with S/R).

FMZ source id: 436764

Source
    https://www.fmz.com/strategy/436764 (PineScript v2, FMZ last modified 2023-12-27 15:27:45).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 135-198), length 20, band multipliers 1 / 2 / 3 x atr(200), S/R time frame 240, S/R on, take profit off
    mid = sma(close, 20), trend = ema(close, 200), bands mid +- k atr(200);  hisline = (ema 120 - ema 260) - ema(that, 90);  rsPos = (close - support[240]) / (resistance[240] - support[240]) with resistance / support = security(tickerid, "240", high / low)
    long = mid > trend and haOpen[1] < haClose[1] and mid > mid[1] and close < upper1 and hisline > 0 and rsPos > 100;  short mirror with rsPos < 0;  close Long when close > upper3 or close < lower2;  close Short when close < lower3 or close > upper2

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 4-hour high / low come from security() in a version-2 script, which reads the whole 4-hour bar
      (lookahead); the script reads them 240 chart bars back, so the 4-hour bar used (the one holding bar
      t - 240, 4-hour bars on UTC multiples of 4 hours) closed long before bar t. rsPos > 100 (more than 100
      ranges above that old range) is written so and kept: longs need an extreme rally. The Heikin-Ashi
      candle is built on the chart's own bars (open seeded with (open + close) / 2). Orders follow the
      script's call order: an entry while flat or opposite, a close only of a position open at the bar's
      close, so an entry and an opposite close on one bar leave the new side. The take profit is off and
      not ported. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 4-hour values are 240 bars old.
    2 generic: PASS, ATR bands and a range position.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the take-profit tick formula (off) stored.
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

NAME = "fmz_436764_kana_bands_ha_range_position"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "use_sr": [True, False],
}
DEFAULT_PARAMS = {"length": 20, "use_sr": True, "mult1": 1.0, "mult2": 2.0, "mult3": 3.0, "atr_len": 200,
                  "trend_len": 200, "sr_tf": 240}  # sr_tf: the 4-hour frame in minutes and the bars-back count


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    mid = c.rolling(int(p["length"])).mean()
    trend = c.ewm(span=int(p["trend_len"]), adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    up1, up2, up3 = (mid + atr * float(p[k]) for k in ("mult1", "mult2", "mult3"))
    lo1, lo2, lo3 = (mid - atr * float(p[k]) for k in ("mult1", "mult2", "mult3"))
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ha_c = ((o + h + lo + c) / 4).to_numpy()
    m = len(cv)
    ha_o = np.full(m, np.nan)
    for i in range(m):
        ha_o[i] = (ov[i] + cv[i]) / 2 if i == 0 or np.isnan(ha_o[i - 1]) else (ha_o[i - 1] + ha_c[i - 1]) / 2
    ha_o_s, ha_c_s = pd.Series(ha_o, index=c.index), pd.Series(ha_c, index=c.index)
    green1 = ha_o_s.shift(1) < ha_c_s.shift(1)
    red1 = ha_o_s.shift(1) > ha_c_s.shift(1)
    macd = c.ewm(span=120, adjust=False).mean() - c.ewm(span=260, adjust=False).mean()
    hist = macd - macd.ewm(span=90, adjust=False).mean()
    k = int(p["sr_tf"])
    bucket = bars_df.index.floor(f"{k}min")
    res4 = h.groupby(bucket).transform("max")          # the whole 4-hour bar (version-2 security)
    sup4 = lo.groupby(bucket).transform("min")
    res_k, sup_k = res4.shift(k), sup4.shift(k)          # read 240 chart bars back
    with np.errstate(divide="ignore", invalid="ignore"):
        rs_pos = (c - sup_k) / (res_k - sup_k)
    sr_l = (rs_pos > 100) if p["use_sr"] else pd.Series(True, index=c.index)
    sr_s = (rs_pos < 0) if p["use_sr"] else pd.Series(True, index=c.index)
    lc = ((mid > trend) & green1 & (mid > mid.shift(1)) & (c < up1) & (hist > 0) & sr_l).to_numpy()
    sc = ((mid < trend) & red1 & (mid < mid.shift(1)) & (c > lo1) & (hist < 0) & sr_s).to_numpy()
    lxc = ((c > up3) | (c < lo2)).to_numpy()
    sxc = ((c < lo3) | (c > up2)).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lc[i] and pos <= 0:
            new = 1
        elif sc[i] and pos >= 0:
            new = -1
        elif (lxc[i] and pos == 1) or (sxc[i] and pos == -1):
            new = 0
        if new == 1 and pos != 1:
            le[i] = True
        elif new == -1 and pos != -1:
            se[i] = True
        elif new == 0 and pos == 1:
            lx[i] = True
        elif new == 0 and pos == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
