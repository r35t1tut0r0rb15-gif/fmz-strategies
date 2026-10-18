"""123 reversal state with a multi-length confluence state, 1-hour bars: both long opens a long, both short opens a short, any other combination closes (the "Trade reverse"
input flips the side). The confluence score sums an error-phase, a momentum and a trend-cycle classification over four simple averages (10, 19, 37, 73 bars).
Port of FMZ strategy #436148 "Moment Reversal Strategy Based on Multi factor Model" (Combo Backtest 123 Reversal & Confluence).

FMZ source id: 436148

Source
    https://www.fmz.com/strategy/436148 (PineScript v4, FMZ last modified 2023-12-21 16:26:10).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 189-325), stoch 14 (K smoothing 1, D 3, level 50); harmonic 10, bands +9 / -9
    STL = round(2 Harmonic - 1.5), ITL = round(2 STL - 1.5), LTL = round(2 ITL - 1.5);  momentum, derivative-corrected averages, sine-cosine phase sums, three classifications (-3 .. 3) added to value42
    Confluence = value42 (both agree on sign with xvalue70) or value42 / 10 (mixed);  pos = Res2 >= -9 and Res2 != 0 ? -1 : Res1 <= 9 and Res1 != 0 ? 1 : Res3 != 0 ? 2 : last
    combined with the 123 state: both 1 -> 1, both -1 -> -1, else 0; reverse flips; close_all when 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The formulas are written out as in the script (round half up; the sine and cosine take the angle
      x 2 x 3.14 / 360 as radians; the offsets HOFF, SOFF and IOFF are 5, 9 and 18 for harmonic 10). The
      neutral state 2 never agrees with the 123 state, so it closes. Two persistent states combined; a flip from
      one agreed side to the other on one bar is a reversal (REVERSAL INTENDED). FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pattern state and a smoothed-average score.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND433002 (2 members, best partner #433002, Jaccard 0.783); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436148_reversal_123_confluence"
FAMILY = "reversal_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "harmonic": [10, 8],
}
DEFAULT_PARAMS = {"reverse": False, "harmonic": 10, "buy_band": 9, "sell_band": -9, "length": 14, "k_smooth": 1,
                  "d_len": 3, "level": 50}


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


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    q = 0
    for i in range(len(up)):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def _rnd(v):
    return int(np.floor(v + 0.5))


def _cls(x, x1, sg):
    pos, neg = x > 0, x < 0
    dn, up, lo, hi = x < x1, x > x1, x < sg, x > sg
    r = np.zeros(len(x))
    r = np.where(pos & dn & lo, 1, r)
    r = np.where(pos & dn & hi, 2, r)
    r = np.where(pos & up & lo, 2, r)
    r = np.where(pos & up & hi, 3, r)
    r = np.where(neg & up & hi, -1, r)
    r = np.where(neg & dn & hi, -2, r)
    r = np.where(neg & up & lo, -2, r)
    r = np.where(neg & dn & lo, -3, r)
    return r


def _confluence_state(bars_df, harmonic, buy_band, sell_band):
    c = bars_df["close"]
    ohlc4 = (bars_df["open"] + bars_df["high"] + bars_df["low"] + c) / 4
    H = int(harmonic)
    STL = _rnd(H * 2 - 1 - 0.5)
    ITL = _rnd(STL * 2 - 1 - 0.5)
    LTL = _rnd(ITL * 2 - 1 - 0.5)
    HOFF = _rnd(H / 2 - 0.5)
    SOFF = _rnd(STL / 2 - 0.5)
    IOFF = _rnd(ITL / 2 - 0.5)
    xH, xS, xI, xL = (c.rolling(n).mean() for n in (H, STL, ITL, LTL))
    xmomsig = (xS - xH.shift(HOFF)) + (xI - xS.shift(SOFF)) + (xL - xI.shift(IOFF))
    xLo = ohlc4.rolling(LTL - 1).mean()
    xH2, xS2, xI2, xL2 = (c.rolling(n - 1).mean() for n in (H, STL, ITL, LTL))
    deriv = lambda x: x * 2 - x.shift(1)                        # noqa: E731
    DH, DS, DI, DL = deriv(xH), deriv(xS), deriv(xI), deriv(xL)
    DRH, DRS, DRI, DRL = (H * DH - xH2 * (H - 1), STL * DS - xS2 * (STL - 1), ITL * DI - xI2 * (ITL - 1),
                          LTL * DL - xL2 * (LTL - 1))
    SumH, SumS, SumI, SumL = xH2 * (H - 1), xS2 * (STL - 1), xI2 * (ITL - 1), xLo * (LTL - 1)
    x5, x6, x7, x13 = (SumH + DRH) / H, (SumS + DRS) / STL, (SumI + DRI) / ITL, (SumL + DRL) / LTL
    value9, value10, value14 = x6 - x5.shift(HOFF), x7 - x6.shift(SOFF), x13 - x7.shift(IOFF)
    xmom = value9 + value10 + value14
    w = 2 * 3.14 / 360
    trig = lambda s: np.sin(s * w) + np.cos(s * w)              # noqa: E731
    xSum = trig(x5) + trig(x6) + trig(x7)
    xErr = trig(xH) + trig(xS) + trig(xI)
    cond2 = ((xSum > xSum.shift(SOFF)) & (xH < xH.shift(SOFF))) | ((xSum < xSum.shift(SOFF)) & (xH > xH.shift(SOFF)))
    phase = np.where(cond2, -1, 1)
    xErrSum = (xSum - xErr) * phase
    xErrSig = xErrSum.rolling(SOFF).mean()
    x70 = x5 - x13
    x71 = x70.rolling(H).mean()
    err_num = _cls(xErrSum.to_numpy(), xErrSum.shift(1).to_numpy(), xErrSig.to_numpy())
    mom_num = _cls(xmom.to_numpy(), xmom.shift(1).to_numpy(), xmomsig.to_numpy())
    tc_num = _cls(x70.to_numpy(), x70.shift(1).to_numpy(), x71.to_numpy())
    v42 = err_num + mom_num + tc_num
    x70v = x70.to_numpy()
    conf = np.where((v42 > 0) & (x70v > 0), v42, np.where((v42 < 0) & (x70v < 0), v42,
                    np.where(((v42 > 0) & (x70v < 0)) | ((v42 < 0) & (x70v > 0)), v42 / 10, 0.0)))
    res1 = np.where(conf >= 1, conf, 0.0)
    res2 = np.where(conf <= -1, conf, 0.0)
    res3 = np.where(conf == 0, 0.0, np.where((conf > -1) & (conf < 1), 10 * conf, 0.0))
    out = np.zeros(len(conf), dtype=np.int8)
    q = 0
    for i in range(len(conf)):
        if res2[i] >= sell_band and res2[i] != 0:
            q = -1
        elif res1[i] <= buy_band and res1[i] != 0:
            q = 1
        elif res3[i] != 0:
            q = 2
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
        vf = raw.rolling(int(p["k_smooth"])).mean()
        vs = vf.rolling(int(p["d_len"])).mean()
        c1, c2 = c.shift(1), c.shift(2)
        lv = float(p["level"])
        a = _state(((c2 < c1) & (c > c1) & (vf < vs) & (vf > lv)).to_numpy(),
                   ((c2 > c1) & (c < c1) & (vf > vs) & (vf < lv)).to_numpy())
        b = _confluence_state(bars_df, p["harmonic"], float(p["buy_band"]), float(p["sell_band"]))
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        pos = -pos
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
