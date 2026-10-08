"""ATR parabolic SAR (QuantNomad, always in): a SAR whose step is af x ATR(14) instead of a share of
the distance to the extreme point; on the first bar of a new SAR trend go with it.
Port of FMZ strategy #426598 "ATR Parabolic SAR Trailing Stop Strategy Based on ATR Indicator".

Source
    https://www.fmz.com/strategy/426598 (PineScript v4, FMZ last modified 2023-09-13 15:53:00).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 68-126), ATR 14, 0.02 / 0.02 / 0.2, entry bar 1
    atr = na(atr(14)) ? tr : atr(14)
    long_to_short = dir[1] == 1 and close <= psar[1];  short_to_long mirrors
    change = isfirst[1] or a flip;  dir = second bar: close[1] > open[1] ? 1 : -1; flips set it
    trend_bars = flip ? +-1 : dir == 1 ? trend_bars[1] + 1 : dir == -1 ? trend_bars[1] - 1 : same
    af = change ? start : (dir == 1 and high > ep[1]) or (dir == -1 and low < ep[1])
         ? min(max, af[1] + inc) : af[1]
    ep = change ? (dir == 1 ? high : low) : dir == 1 ? max(ep[1], high) : min(ep[1], low)
    psar = second bar: low[1] / high[1]; change ? ep[1] : psar[1] +- af * atr
    trend_bars == 1 -> entry long;  trend_bars == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first bar's values are na; the SAR starts on the second bar. On that bar trend_bars
      counts from nz(0) to +-1, so it can enter (as in Pine).
    * tr is na on the first bar (no previous close), then fills the ATR warm-up.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426598_atr_parabolic_sar"
FAMILY = "parabolic_sar"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "start": [0.01, 0.02],
    "increment": [0.01, 0.02],
    "entry_bars": [1, 2],
}
DEFAULT_PARAMS = {"atr_length": 14, "start": 0.02, "increment": 0.02, "maximum": 0.2, "entry_bars": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _atr_pine(bars_df, int(p["atr_length"])).fillna(tr).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, l, c))
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    nan = np.nan
    psar_p, af_p, dir_p, ep_p, tb_p = nan, nan, nan, nan, nan
    nb = int(p["entry_bars"])
    for i in range(m):
        first_prev = i == 1
        l2s = dir_p == 1 and cv[i] <= psar_p
        s2l = dir_p == -1 and cv[i] >= psar_p
        change = first_prev or l2s or s2l
        if first_prev:
            d = 1 if cv[i - 1] > ov[i - 1] else -1
        elif l2s:
            d = -1
        elif s2l:
            d = 1
        else:
            d = 0 if np.isnan(dir_p) else dir_p
        tb0 = 0 if np.isnan(tb_p) else tb_p
        tb = -1 if l2s else 1 if s2l else tb0 + 1 if d == 1 else tb0 - 1 if d == -1 else tb0
        if change:
            af = p["start"]
        elif (d == 1 and hv[i] > ep_p) or (d == -1 and lv[i] < ep_p):
            af = min(p["maximum"], af_p + p["increment"])
        else:
            af = af_p
        if change and d == 1:
            ep = hv[i]
        elif change and d == -1:
            ep = lv[i]
        elif d == 1:
            ep = max(ep_p, hv[i]) if not np.isnan(ep_p) else nan
        else:
            ep = min(ep_p, lv[i]) if not np.isnan(ep_p) else nan
        if first_prev:
            ps = lv[i - 1] if cv[i - 1] > ov[i - 1] else hv[i - 1]
        elif change:
            ps = ep_p
        elif d == 1:
            ps = psar_p + af * atr[i]
        else:
            ps = psar_p - af * atr[i]
        le[i], se[i] = tb == nb, tb == -nb
        psar_p, af_p, dir_p, ep_p, tb_p = ps, af, d, ep, tb
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
