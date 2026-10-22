"""EMA 9 / 21 crossings with RSI 14 under 70 / over 30 and the close beyond the fast EMA by 1.5 ATR 14, 1-minute bars: the up-cross goes long, the down-cross goes short; the opposite cross or a close 1 % against the signal close closes; reversing.
Port of FMZ strategy #483054 "Dynamic Volatility Adjusted EMA Trend Trading Strategy with Smart Stop Loss System" (Enhanced Scalping Strategy with Stop Loss).

FMZ source id: 483054

Source
    https://www.fmz.com/strategy/483054 (PineScript v6, FMZ last modified 2025-02-21 11:11:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-207), EMA 9 / 21 (forced on a 1-minute chart); RSI 14 / 70 / 30; ATR 14 x 1.5; stop 1 % on closes; MPL 2.0 notice (DBate)
    crossover(ema9, ema21) and rsi < 70 and close > ema9 + 1.5 atr -> close Short, entry Long, stop := close x 0.99, inLong
    crossunder(ema9, ema21) and rsi > 30 and close < ema9 - 1.5 atr -> close Long, entry Short, stop := close x 1.01, inShort
    inLong and (crossunder or close <= stop) -> close Long;  inShort and (crossover or close >= stop) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On a 1-minute chart the script forces the EMA and RSI lengths to 9 / 21 / 14 whatever the inputs say
      (timeframe.period == "1"), so those lengths are fixed here. The stop is checked on bar closes and
      sent as a close (an exit signal, no stop module). The in-trade flags are followed in a loop, as
      written. An entry on the other side reverses (REVERSAL INTENDED). No sizing code. The MPL 2.0 notice
      is kept with the verbatim copy (ported, stated). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based percent stop.
    2 generic: PASS, EMA crossings with RSI and an ATR distance filter.
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

NAME = "fmz_483054_ema9_21_cross_rsi_atr1_5_filter_close_stop1pct_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_multiplier": [1.5, 1.0],
    "stop_loss_percent": [1.0, 0.5],
}
DEFAULT_PARAMS = {"atr_multiplier": 1.5, "stop_loss_percent": 1.0, "fast": 9, "slow": 21, "rsi_length": 14,
                  "rsi_ob": 70, "rsi_os": 30, "atr_length": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_length"]))
    k = float(p["atr_multiplier"])
    xu = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    xd = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    lc = (xu & (r < float(p["rsi_ob"])) & (c > f + k * atr)).to_numpy()
    sc = (xd & (r > float(p["rsi_os"])) & (c < f - k * atr)).to_numpy()
    cv = c.to_numpy(dtype=float)
    q = float(p["stop_loss_percent"]) / 100
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    in_l = in_s = False
    stop = np.nan
    for i in range(m):
        if lc[i]:
            le[i], in_l, in_s, stop = True, True, False, cv[i] * (1 - q)
        if sc[i]:
            se[i], in_s, in_l, stop = True, True, False, cv[i] * (1 + q)
        if in_l and (xd[i] or cv[i] <= stop):
            lx[i], in_l, in_s = True, False, False
        if in_s and (xu[i] or cv[i] >= stop):
            sx[i], in_s, in_l = True, False, False
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~le & ~se), S(se), S(sx & ~se & ~le)


def portfolio_kwargs(**params):
    return {}
