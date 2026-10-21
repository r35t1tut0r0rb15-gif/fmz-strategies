"""Three-inside-down candle pattern, 1-hour bars, long only as written: the bearish pattern (an up candle, a smaller inside down candle, then a down candle closing under both) stores its close and the state goes
long; a high reaching the stored close plus a target distance, or a low reaching it minus a stop distance, clears it, and the next bar's state closes the long.
Port of FMZ strategy #436992 "Three Inside Down Reversal Strategy" (Three Inside Down Backtest).

FMZ source id: 436992

Source
    https://www.fmz.com/strategy/436992 (PineScript v3, FMZ last modified 2023-12-29 11:09:56).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 181-194), take profit 40, stop loss 20 ("pip", price units)
    pattern = close[2] > open[2] and open[1] > close[1] and open[1] <= close[2] and open[2] <= close[1] and open[1] - close[1] < close[2] - open[2] and close < open and close < close[1] and open < open[1] and close < open[2]
    posprice := pattern ? close : posprice[1];  pos = posprice > 0 ? 1 : 0;  pos == 0 -> close_all, pos == 1 -> entry Long;  then posprice := 0 if high >= posprice + 40 or low <= posprice - 20

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script trades the BEARISH pattern LONG, as written (an intended short version is owed).
      Criterion 2: the 40 / 20 price-unit distances are re-expressed as ATR(14) multiples of the bar
      (k_sl x ATR, target 2 x k_sl x ATR); 0.13 is the reading (about 20 on BTC against a 1-hour ATR near
      150), 1.0 one ATR. The touch is tested on the bar's high / low at its close and the state then
      closes the long on the NEXT bar's close (one bar after the touch), as written; no stop order. Long
      only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; levels tested at bar closes.
    2 generic: ADAPT, price-unit distances -> ATR multiples.
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

NAME = "fmz_436992_three_inside_down_long_state"
FAMILY = "candle_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_sl": [0.13, 1.0],
    "atr_len": [14, 28],
}
DEFAULT_PARAMS = {"k_sl": 0.13, "atr_len": 14, "tp_ratio": 2.0}


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
    o1, o2, c1, c2 = o.shift(1), o.shift(2), c.shift(1), c.shift(2)
    pat = ((c2 > o2) & (o1 > c1) & (o1 <= c2) & (o2 <= c1) & (o1 - c1 < c2 - o2) & (c < o) & (c < c1)
           & (o < o1) & (c < o2)).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    sld = float(p["k_sl"]) * atr
    tpd = float(p["tp_ratio"]) * sld
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    state = np.zeros(m, dtype=bool)
    pp = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pat[i]:
                pp = cv[i]
            state[i] = pp > 0
            if pp > 0 and hv[i] >= pp + tpd[i]:
                pp = 0.0
            if pp > 0 and lv[i] <= pp - sld[i]:
                pp = 0.0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(state, index=ix), pd.Series(~state, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
