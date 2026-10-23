"""A bar entirely below (above) an adaptive SAR, the close above (below) both an EMA 200 and an SMA 50 with the SMA 50 above (below) the EMA 200, a positive (negative) squeeze momentum and the HawkEye volume green (red) test, 3-minute bars: the bullish set goes long when not long, the bearish set goes short when not short; a 100 % target from the entry (the 999 % close stop never acts); reversing.
Port of FMZ strategy #429474 "Trend Tracking Four Elements Strategy" (Strategy Myth-Busting #6 - PSAR+MA+SQZMOM+HVI - [MYN]).

FMZ source id: 429474

Source
    https://www.fmz.com/strategy/429474 (PineScript v5, FMZ last modified 2023-10-17 14:47:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 277-710), SAR 0.02 / 0.02, max 0.005 (adaptive code 1 on 3-minute bars); EMA 200, SMA 50; squeeze BB 20 x 1.5 sd (the KC multiplier), KC 20 x 1.5; HVI 200; TP 100 %, SL 999 %; template of #426563
    PSARLongEntry = high < PSAR;  MALongEntry = close > ma_1 and close > ma_2 and ma_2 > ma_1;  SQZMOM val > 0;  HVI g_enabled
    all long and not in a long -> entry Long;  the short mirror (low > PSAR, HVI r_enabled, val < 0) -> entry Short;  exit(TP 100 %), close tests at 999 %

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long entry needs the whole bar BELOW the SAR (high < SAR), as written (the comment describes a
      flip). The SAR maximum is 0.005 from the 3-minute adaptive code, under its 0.02 start, so the step
      drops to 0.005 after the first new extreme, as Pine's sar does. The Bollinger deviation uses the KC
      multiplier 1.5, as written. The HVI entries use its green / red tests directly (not the bar
      colour, which puts gray first). The 999 % stop cannot be reached by a long and practically never by a short (not ported);
      the four 100 % targets are a scalar 1.0 of the fill. REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). The equity x leverage contracts are sizing. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target from the fill.
    2 generic: PASS, SAR / MA / squeeze / volume-bar agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: contracts = equity / close x leverage, 100 % of equity, capital 20000, commission 0.075 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the HawkEye volume green / red tests (volume against its SMA 200); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429474_sar_ma200_50_squeeze_hawkeye_volume_agreement_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length_hvi": [200, 100],
    "ma_1_val": [200, 100],
}
DEFAULT_PARAMS = {"length_hvi": 200, "ma_1_val": 200, "ma_2_val": 50, "length_bb": 20, "length_kc": 20,
                  "mult_kc": 1.5, "trend_code": 1, "tp": 1.0}


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


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         0.02, 0.02, int(p["trend_code"]) * 0.005), index=c.index)
    psar_l, psar_s = h < sar, lo > sar
    nk = int(p["length_kc"])
    val = _linreg(c - ((h.rolling(nk).max() + lo.rolling(nk).min()) / 2 + c.rolling(nk).mean()) / 2, nk)
    ma1 = c.ewm(span=int(p["ma_1_val"]), adjust=False).mean()
    ma2 = c.rolling(int(p["ma_2_val"])).mean()
    ma_l = (c > ma1) & (c > ma2) & (ma2 > ma1)
    ma_s = (c < ma1) & (c < ma2) & (ma2 < ma1)
    n = int(p["length_hvi"])
    rng = h - lo
    ravg, vavg = rng.rolling(n).mean(), v.rolling(n).mean()
    h1, l1 = h.shift(1), lo.shift(1)
    mid1 = (h1 + l1) / 2
    u1, d1 = mid1 + (h1 - l1), mid1 - (h1 - l1)
    r_en = ((rng > ravg) & (c < d1) & (v > vavg)) | (c < mid1)
    g_en = (c > mid1) | ((rng > ravg) & (c > u1) & (v > vavg)) | ((h > h1) & (rng < ravg / 1.5) & (v < vavg)) \
        | ((lo < l1) & (rng < ravg / 1.5) & (v > vavg))
    lcond = (psar_l & ma_l & g_en & (val > 0)).to_numpy()
    scond = (psar_s & ma_s & r_en & (val < 0)).to_numpy()
    m = len(lcond)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        old = pos
        if lcond[i] and old != 1:
            pos = 1
        if scond[i] and old != -1:
            pos = -1
        le[i] = pos == 1 and old != 1
        se[i] = pos == -1 and old != -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
