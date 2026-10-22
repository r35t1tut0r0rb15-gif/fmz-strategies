"""SuperTrend 3 / 10 direction, the close against the Parabolic SAR 0.02 / 0.2 and the MACD 12 / 26 / 9 side, 2-minute bars: all three bullish goes long, all three bearish goes short; the MACD and SAR both turning against the position closes; reversing.
Port of FMZ strategy #488129 "多指标协同确认交易策略MACD抛物线SAR与超级趋势三重验证系统-Multi-Indicator-Confirmation-Trading-System-MACD-Parabolic-SAR-and-Supertrend-Triple-Verification-Framework" (Vinay Strategy).

FMZ source id: 488129

Source
    https://www.fmz.com/strategy/488129 (PineScript v6, FMZ last modified 2025-03-25 11:51:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 206-285), SuperTrend 3 / 10; SAR 0.02 / 0.02 / 0.2; MACD 12 / 26 / 9; 100 % of equity, no commission
    macd > signal and close > sar and supertrend up -> entry Long;  macd < signal and close < sar and supertrend down -> entry Short
    macd < signal and close < sar -> close Long;  macd > signal and close > sar -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states. A short entry also meets the long exit, so it reverses (REVERSAL
      INTENDED). ta.supertrend and ta.sar follow Pine's reference implementations. FREQ = "2min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend / SAR / MACD agreement.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, no commission or slippage, stored, not ported.
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

NAME = "fmz_488129_supertrend3_10_sar_macd_agreement_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atrFactor": [3.0, 2.0],
    "atrPeriod": [10, 20],
}
DEFAULT_PARAMS = {"atrFactor": 3.0, "atrPeriod": 10, "fastLength": 12, "slowLength": 26, "sigLength": 9,
                  "sarStep": 0.02, "sarMax": 0.2}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    _, d = _supertrend(bars_df, float(p["atrFactor"]), int(p["atrPeriod"]))
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sarStep"]), float(p["sarStep"]), float(p["sarMax"])), index=c.index)

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["fastLength"]) - ema(c, p["slowLength"])
    sig = ema(macd, p["sigLength"])
    le = (macd > sig) & (c > sar) & (d < 0)
    se = (macd < sig) & (c < sar) & (d > 0)
    lx = (macd < sig) & (c < sar) & ~se
    sx = (macd > sig) & (c > sar) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
