"""Bearish engulfing pattern, 1-hour bars, short only: an up candle with a body of at least a minimum size followed by a down candle opening at or above its close and closing at or under its open with a larger
body stores the close and the state goes short; a low reaching the stored close minus a target distance, or a high reaching it plus a stop distance, clears it, and the next bar's state closes the short.
Port of FMZ strategy #437682 "Bearish Engulfing Reversal Strategy" (Bearish Engulfing Backtest).

FMZ source id: 437682

Source
    https://www.fmz.com/strategy/437682 (PineScript v3, FMZ last modified 2024-01-04 17:35:18).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 140-154), take profit 40, stop loss 20, minimum body 2 ("pip", price units)
    pattern = |close[1] - open[1]| >= 2 and close[1] > open[1] and open > close and open >= close[1] and open[1] >= close and open - close > close[1] - open[1]
    posprice := pattern ? close : posprice[1];  pos = posprice > 0 ? -1 : 0;  pos == 0 -> close_all, pos == -1 -> entry Short;  then posprice := 0 if low <= posprice - 40 or high >= posprice + 20

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 40 / 20 / 2 price-unit distances are re-expressed as ATR(14) multiples of the bar
      (stop k_sl x ATR, target 2 x k_sl x ATR, minimum body 0.1 x k_sl x ATR, the source's 20 : 40 : 2);
      0.13 is the reading (about 20 on BTC against a 1-hour ATR near 150), 1.0 one ATR. The touch is tested
      on the bar's high / low at its close and the state closes the short on the NEXT bar's close, as
      written (as #436992). Short only: Opposite entries cannot occur. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; levels tested at bar closes.
    2 generic: ADAPT, price-unit distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND432977 (2 members, best partner #432977, Jaccard 0.797); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437682_bearish_engulfing_short_state"
FAMILY = "candle_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_sl": [0.13, 1.0],
    "atr_len": [14, 28],
}
DEFAULT_PARAMS = {"k_sl": 0.13, "atr_len": 14, "tp_ratio": 2.0, "body_ratio": 0.1}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    sld = float(p["k_sl"]) * atr
    tpd = float(p["tp_ratio"]) * sld
    minb = float(p["body_ratio"]) * sld
    o1, c1 = o.shift(1), c.shift(1)
    pat = (((c1 - o1).abs() >= minb) & (c1 > o1) & (o > c) & (o >= c1) & (o1 >= c) & (o - c > c1 - o1)).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sv, tv = sld.to_numpy(), tpd.to_numpy()
    m = len(cv)
    state = np.zeros(m, dtype=bool)
    pp = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pat[i]:
                pp = cv[i]
            state[i] = pp > 0
            if pp > 0 and lv[i] <= pp - tv[i]:
                pp = 0.0
            if pp > 0 and hv[i] >= pp + sv[i]:
                pp = 0.0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(state, index=ix), pd.Series(~state, index=ix)


def portfolio_kwargs(**params):
    return {}
