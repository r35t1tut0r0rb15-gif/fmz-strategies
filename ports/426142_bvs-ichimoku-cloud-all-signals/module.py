"""BV's Ichimoku signal tester (default signal Tenkan / Kijun): Tenkan crossing above Kijun goes long,
below goes short; each trade carries an ATR stop (1.5 ATR) and target (1 ATR).
Port of FMZ strategy #426142 "BV's ICHIMOKU CLOUD SIGNAL TESTER".

Source
    https://www.fmz.com/strategy/426142 (PineScript v4, FMZ last modified 2023-09-08 16:18:04).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 71-170), signal "Tenkan/Kijun", 9 / 26 / 52 / 26,
SL 1.5 ATR, TP 1.0 ATR
    crossover(tenkan, kijun) -> entry long;  crossunder -> entry short
    exit(profit = TP, loss = SL), TP / SL = atr(14) * 100000 * multiplier ticks (forex pip adjuster)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick distances are ATR x 100000 x multiplier, i.e. multiplier x ATR on a
      5-digit forex pair (the evident meaning; on BTC's 0.01 tick they would be 1000s of ATR).
      Ported as sl_atr / tp_atr x ATR(14) at the signal bar, sl_stop / tp_stop shifted one bar.
    * The exit is re-issued every bar with the current ATR (moving levels): rule 2, mark
      trailing_stop_pending; the port fixes the signal bar's ATR.
    * The year filter (year > 2017) is a backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426142_tenkan_kijun_atr_bracket"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # the source's atr(14)

GRID = {
    "sl_atr": [1.0, 1.5, 2.0],
    "tp_atr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "sl_atr": 1.5, "tp_atr": 1.0}


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


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def _signals(bars_df, p):
    h, l = bars_df["high"], bars_df["low"]
    mid = lambda n: (h.rolling(int(n)).max() + l.rolling(int(n)).min()) / 2
    t, k = mid(p["conv"]), mid(p["base"])
    up = ((t > k) & (t.shift(1) <= k.shift(1))).to_numpy()
    dn = ((t < k) & (t.shift(1) >= k.shift(1))).to_numpy()
    return up, dn


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    return _always_in(up, dn, bars_df.index)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    sig = pd.Series(up | dn, index=bars_df.index)
    frac = (_atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(sig)
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
