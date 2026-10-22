"""SMA 15 / 45 crossings with an ATR stop line from the signal close, 1-hour bars: the SMA 15 crossing over the SMA 45 goes long, crossing under short; the low crossing under the signal close - 2 ATR(14)
closes a long (the high crossing over close + 2 ATR a short); reversing.
Port of FMZ strategy #442369 "最佳ATR停损倍数策略Best-ATR-Stop-Multiple-Strategy" (BEST ATR Stop Multiple Strategy).

FMZ source id: 442369

Source
    https://www.fmz.com/strategy/442369 (PineScript v4, FMZ last modified 2024-02-21 14:24:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-294), SMA 15 / 45; stop loss on, ATR 14 x 2
    entry_price = valuewhen(cross, close, 0);  entry_stop_atr = 2 atr(14) at the cross;  longStop = buy_trend ? entry_price - entry_stop_atr : 0;  shortStop = sell_trend ? entry_price + entry_stop_atr : 999999
    crossover -> entry BEST L;  crossunder(low, longStop[1]) and buy_trend -> close BEST L;  crossunder -> entry BEST S;  crossover(high, shortStop[1]) and sell_trend -> close BEST S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a bar test (the low crossing under the previous bar's level), sent at the next open,
      not a broker stop. buy / sell trend follow the latest crossing. A close acts only on the held
      position. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a bar-tested ATR stop line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the qty constants are unused).
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

NAME = "fmz_442369_sma15_45_cross_atr_stop_line_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [15, 10],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 15, "atr_mult": 2.0, "slow": 45, "atr_len": 14}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    el = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    es = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = np.nan_to_num(_rma(tr, int(p["atr_len"])).to_numpy(), nan=0.0)
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    am = float(p["atr_mult"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    since_b = since_s = None
    ep = est = 0.0
    lsp1 = lsp2 = 0.0
    ssp1 = ssp2 = 999999.0
    for i in range(m):
        if el[i] or es[i]:
            ep, est = cv[i], atr[i] * am
        since_b = 0 if el[i] else (since_b + 1 if since_b is not None else None)
        since_s = 0 if es[i] else (since_s + 1 if since_s is not None else None)
        bt = since_b is not None and since_s is not None and since_s > since_b
        st = since_b is not None and since_s is not None and since_s < since_b
        lsp = ep - est if bt else 0.0
        ssp = ep + est if st else 999999.0
        lo1 = lv[i - 1] if i > 0 else np.nan
        hi1 = hv[i - 1] if i > 0 else np.nan
        x_l = bt and lv[i] < lsp1 and lo1 >= lsp2
        x_s = st and hv[i] > ssp1 and hi1 <= ssp2
        new = held
        if el[i] and new != 1:
            new = 1
        if x_l and held == 1 and new == 1:
            new = 0
        if es[i] and new != -1:
            new = -1
        if x_s and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
        lsp2, lsp1, ssp2, ssp1 = lsp1, lsp, ssp1, ssp
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
