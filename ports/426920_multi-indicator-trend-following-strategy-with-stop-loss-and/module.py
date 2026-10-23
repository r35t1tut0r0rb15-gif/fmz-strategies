"""An SMA-based MACD 12 / 25 / 9 histogram turning through zero with the close on the EMA 200's side, the SAR 0.1 / 0.05 / 0.3 trend and a volume oscillator (EMA 1 against EMA 8 of volume), hourly bars: a turn up in an up-trend with volume under its average goes long, a turn down in a down-trend with volume above it goes short; a long closes on a short signal or when the close / high crosses its target (close + the SAR distance) or the close / low crosses under its stop (the SAR), the short mirror.
Port of FMZ strategy #426920 "Multi indicator Trend Following Strategy with Stop Loss and Take Profit" (Scalping FOrex full strategy with risk management).

FMZ source id: 426920

Source
    https://www.fmz.com/strategy/426920 (PineScript v4, FMZ last modified 2023-09-15 15:39:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 143-347), OBV osc EMA 1 / 8 of volume; SAR 0.1 / 0.05 / 0.3 (in-script reference); EMA 200; MACD SMA 12 / 25, signal SMA 9; entry counters
    long = hist[1] < 0 and hist > 0 and close > ema(200) and uptrend and osc < 0;  short = hist[1] > 0 and hist < 0 and close < ema(200) and not uptrend and osc > 0
    long and not longOpened and entrys < 100 -> entry long, tp = close + (close - SAR), sl = SAR;  exit = crossover(close or high, tp) or crossunder(close or low, sl) or short -> close long;  short mirror (counter "entry")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters start at na, so a long needs a short signal first (it sets entrys := 0) and a short
      needs a long signal first, as written. The targets / stops are close-based tests (crossings of the
      close, high or low over the level set at the signal close), filled at the next open. The SAR is the
      script's own copy of Pine's reference sar. REVERSAL INTENDED (a signal closes the other side and
      opens its own). The 100 % of equity size and per-contract commission are sizing / costs. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based SAR target / stop.
    2 generic: PASS, MACD histogram turns with EMA 200, SAR and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 10000, commission 0.00005 per contract stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the oscillator 100 x (ema(volume, 1) - ema(volume, 8)) / ema(volume, 8); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426920_sma_macd_hist_zero_turn_ema200_sar_volume_osc_sar_bracket_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lena": [200, 100],
    "longlen": [8, 20],
}
DEFAULT_PARAMS = {"lena": 200, "longlen": 8, "shortlen": 1, "start": 0.1, "increment": 0.05, "maximum": 0.3,
                  "fast": 12, "slow": 25, "signal": 9}


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
    """Pine's reference sar (the script's copy): the SAR of each bar and its up-trend state."""
    m = len(cv)
    out = np.full(m, np.nan)
    up = np.zeros(m, dtype=bool)
    res = mm = acc = np.nan
    below = False
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
        out[i], up[i] = res, below
    return out, up


def _cross_up(a, b, i):
    return i > 0 and a[i] > b[i] and a[i - 1] <= b[i - 1]


def _cross_dn(a, b, i):
    return i > 0 and a[i] < b[i] and a[i - 1] >= b[i - 1]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    sa = v.ewm(span=int(p["shortlen"]), adjust=False).mean()
    la = v.ewm(span=int(p["longlen"]), adjust=False).mean()
    osc = 100 * (sa - la) / la
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sar, up = _sar(hv, lv, cv, float(p["start"]), float(p["increment"]), float(p["maximum"]))
    out = c.ewm(span=int(p["lena"]), adjust=False).mean()
    macd = c.rolling(int(p["fast"])).mean() - c.rolling(int(p["slow"])).mean()
    hist = macd - macd.rolling(int(p["signal"])).mean()
    long_ = ((hist.shift(1) < 0) & (hist > 0) & (c > out) & pd.Series(up, index=c.index) & (osc < 0)).to_numpy()
    short_ = ((hist.shift(1) > 0) & (hist < 0) & (c < out) & pd.Series(~up, index=c.index) & (osc > 0)).to_numpy()
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    tpl, sll, tps, sls = (np.full(m, np.nan) for _ in range(4))
    lop = sop = False
    entrys = entry = np.nan
    tl = sl_ = ts = ss = np.nan
    for i in range(m):
        lop_p, sop_p = lop, sop
        if long_[i] and not lop and entrys < 100:          # na < 100 is false
            lop, tl, sl_ = True, cv[i] + (cv[i] - sar[i]), sar[i]
            entrys += 1
            le[i] = True
        tpl[i], sll[i] = tl, sl_
        if lop_p and (_cross_up(cv, tpl, i) or _cross_up(hv, tpl, i) or _cross_dn(cv, sll, i)
                      or _cross_dn(lv, sll, i) or short_[i]):
            lop, tl, sl_ = False, np.nan, np.nan
            lx[i] = True
        tpl[i], sll[i] = tl, sl_
        if short_[i]:
            entrys = 0
        if short_[i] and not sop and entry < 100:
            sop, ts, ss = True, cv[i] - (sar[i] - cv[i]), sar[i]
            entry = 1
            se[i] = True
        tps[i], sls[i] = ts, ss
        if sop_p and (_cross_dn(cv, tps, i) or _cross_dn(lv, tps, i) or _cross_up(cv, sls, i)
                      or _cross_up(hv, sls, i) or long_[i]):
            sop, ts, ss = False, np.nan, np.nan
            sx[i] = True
        tps[i], sls[i] = ts, ss
        if long_[i]:
            entry = 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
