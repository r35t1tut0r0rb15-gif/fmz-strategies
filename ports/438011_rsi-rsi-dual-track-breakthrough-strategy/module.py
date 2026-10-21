"""RSI 14 / 10 dip buys with a close-tested ATR trail, 1-minute bars, long only: from flat, the RSI 14 at or under 40 with the RSI 10 under it buys; a close at or under the trail (the highest close since entry
minus 2 ATR(26) of the signal bar) closes, and so does an RSI 14 at or over 70 with the RSI 10 above it while the low is more than 3 x that distance above the signal close.
Port of FMZ strategy #438011 "基于RSI指标的双轨突破策略RSI-Dual-track-Breakthrough-Strategy" ([KL] RSI 14 + 10 Strategy).

FMZ source id: 438011

Source
    https://www.fmz.com/strategy/438011 (PineScript v4, FMZ last modified 2024-01-08 10:28:26).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 130-196), RSI 14 / 10, entry 40, exit 70; ATR 26 x 2; trailing stop on; risk:reward mode off (ratio 3)
    flat and rsi14 <= 40 and rsi10 < rsi14 -> entry Long, entry_price := close, buffer := 2 ATR(26), stop := close - buffer;  each bar: stop := max(stop, close - buffer); flat: stop := close - buffer
    long and close <= stop -> close (take profit or stop loss);  long and rsi14 >= 70 and rsi10 > rsi14 and low > entry_price + 3 x (2 ATR(26)) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is a close test, not an order: the stop line is the highest close - buffer since the
      signal bar, and a close at or under it closes at the next open. bar_count is at least 1 on every bar
      inside a trade (it is raised before the test), so the stop-loss branch always applies. The RSI
      exit's distance uses the current ATR and the signal close (entry_price), as written. The
      risk:reward mode is off. Closes act on the position held at the bar close; the entry only from
      flat. Long only. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested exits.
    2 generic: PASS, RSI levels and ATR distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438011_rsi14_10_atr_close_trail_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_multi": [2.0, 3.0],
    "rsi_low": [40, 30],
}
DEFAULT_PARAMS = {"atr_multi": 2.0, "rsi_low": 40.0, "rsi_high": 70.0, "atr_len": 26, "reward_ratio": 3.0}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    r14, r10 = _rsi(c, 14), _rsi(c, 10)
    buy = ((r14 <= float(p["rsi_low"])) & (r10 < r14)).to_numpy()
    ex_c = ((r14 >= float(p["rsi_high"])) & (r10 > r14)).to_numpy()
    ab = (float(p["atr_multi"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    rr = ab * float(p["reward_ratio"])
    cv, lv = c.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_e, pend_x = 0, False, False
    ep, buf, sl = 0.0, 0.0, 0.0
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, pend_e = 1, False
        sl = _nmax(sl, cv[i] - buf)
        if pos == 0:
            sl = cv[i] - buf
            if buy[i] and i + 1 < m:
                ep, buf = cv[i], ab[i]
                sl = cv[i] - ab[i]
                le[i], pend_e = True, True
        elif pos == 1:
            if cv[i] <= sl:
                lx[i], pend_x = True, True
                sl = 0.0
            elif ex_c[i] and lv[i] > ep + rr[i]:
                lx[i], pend_x = True, True
                sl = 0.0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
