"""Hull 377 swing direction with SonicR channel entries, 1-minute bars: in a rising Hull, a close back above the EMA 89 after
being under the EMA 34 high channel, with the regression line under that channel and the price above the Hull, goes
long; the mirror goes short in a falling Hull. A regression line far beyond the channel on the other side closes each
side.
Port of FMZ strategy #433948 "基于频道和线性回归的Hull-MA摆荡策略Hull-MA-Channel-and-Linear-Regression-Swing-Trading-Strategy" (Swing Hull/SonicR/EMA/Linear Regression Strategy).

FMZ source id: 433948

Source
    https://www.fmz.com/strategy/433948 (PineScript v2, FMZ last modified 2023-12-01 16:47:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 170-220), Hull 377; EMA signal 89; high / low channel 34; linear regression 89 and 34
    n1 = wma(2 wma(close, 189) - wma(close, 377), 19);  n2 = the same on close[1];  longCondition = n1 > n2
    long: close > ema89 and close[1] < pacH[1] and linreg89 < pacH and close > n1 and pacH > n1 -> entry long;  closeLong = linreg34 - pacH > 2 (pacH - pacL) and close < linreg34 and linreg89 > ema89
    short mirrors with pacL;  closeShort = pacL - linreg34 > 2 (pacH - pacL) and close > linreg34 and linreg89 < ema89

Interpretation choices (Pine rules in SURVEY_README.md)
    * round(377 / 2) = 189 and round(sqrt(377)) = 19 (Pine's round, ties up). pacH / pacL are EMAs 34
      of the highs / lows.
    * Each bar: the closes act on the position held at the start of the bar (a close of the side just
      re-signalled wins, as in the source's order), then a new entry opens or reverses.
      REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average and channel relations (the exit compares two price distances).
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

NAME = "fmz_433948_hull_sonicr_swing"
FAMILY = "hull_ma"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hull_len": [377, 200],
    "ema_sig": [89, 55],
}
DEFAULT_PARAMS = {"hull_len": 377, "ema_sig": 89, "hilo_len": 34, "lr_len": 89}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(v, n):
    w = np.arange(1, n + 1, dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ (w / w.sum())
    return out


def _linreg(v, n):
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return out


def _pround(x):
    return int(np.floor(x + 0.5))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    cv = c.to_numpy(dtype=float)
    n = int(p["hull_len"])
    diff = 2 * _wma(cv, _pround(n / 2)) - _wma(cv, n)
    sq = _pround(np.sqrt(n))
    n1 = np.full(len(cv), np.nan)
    ok = ~np.isnan(diff)
    if ok.sum() >= sq:
        first = int(np.argmax(ok))
        n1[first:] = _wma(diff[first:], sq)
    n2 = np.concatenate(([np.nan], n1[:-1]))
    hl = int(p["hilo_len"])
    pac_h = h.ewm(span=hl, adjust=False).mean().to_numpy()
    pac_l = lo.ewm(span=hl, adjust=False).mean().to_numpy()
    sig = c.ewm(span=int(p["ema_sig"]), adjust=False).mean().to_numpy()
    lr = _linreg(cv, int(p["lr_len"]))
    lrf = _linreg(cv, hl)
    c1 = np.concatenate(([np.nan], cv[:-1]))
    ph1 = np.concatenate(([np.nan], pac_h[:-1]))
    pl1 = np.concatenate(([np.nan], pac_l[:-1]))
    with np.errstate(invalid="ignore"):
        up = n1 > n2
        le = up & (cv > sig) & (c1 < ph1) & (lr < pac_h) & (cv > n1) & (pac_h > n1)
        se = ~up & (cv < sig) & (c1 > pl1) & (lr > pac_l) & (cv < n1) & (pac_l < n1)
        cl = (lrf - pac_h > (pac_h - pac_l) * 2) & (cv < lrf) & (lr > sig)
        cs = (pac_l - lrf > (pac_h - pac_l) * 2) & (cv > lrf) & (lr < sig)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and cl[i]:
            pos = 0
        elif start == -1 and cs[i]:
            pos = 0
        if se[i] and start != -1:
            pos = -1
        if le[i] and start != 1:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
