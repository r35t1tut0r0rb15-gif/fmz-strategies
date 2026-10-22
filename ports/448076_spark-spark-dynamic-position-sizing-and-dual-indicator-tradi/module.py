"""Four-SuperTrend agreement and RSI extremes, 2-hour bars, gated by 5 bars since the last all-down bar: all four trends up, or the RSI 14 under 30, goes long; the RSI over 70 goes short (the all-down
short can never pass its own gate); reversing; the brackets re-sent from each signal close are not ported.
Port of FMZ strategy #448076 "SPARK动态仓位与双重指标交易策略-SPARK-Dynamic-Position-Sizing-and-Dual-Indicator-Trading-Strategy" (SPARK).

FMZ source id: 448076

Source
    https://www.fmz.com/strategy/448076 (PineScript v4, FMZ last modified 2024-04-12 17:22:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-233), trend flows ATR 7 x 4, 14 x 3.618, 21 x 3.5, 28 x 3.382; RSI 14 (30 / 70); min bars 5 (on); TP 2 % / SL 1 % of the signal close; 10 % of capital x leverage 1
    barsSince = barssince(shortCondition) (direction Both);  all four up and barsSince >= 5 -> entry Long + exit;  all four down and barsSince >= 5 -> entry Short + exit (never: barsSince is 0 then)
    rsi < 30 and barsSince >= 5 -> entry Long_RSI + exit;  rsi > 70 and barsSince >= 5 -> entry Short_RSI + exit  (exits stop / limit = close -+ 1 % / 2 %, re-sent on every signal bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With direction Both, barssince() is taken of the all-down condition, so the all-down short needs
      that condition to be 5 bars old while true now and never fires; before the first all-down bar the
      gate is na and blocks everything. The trend flows follow the script's nz() seeds. Every signal
      bar re-sends the bracket from its own close, and the level signals repeat while they hold, so the
      levels move after entry: not ported (mark trailing_stop_pending); positions end at the opposite
      entries. Calls run in order with one position; when both sides fire, the later short wins (as
      #437773). REVERSAL INTENDED. The portfolio share and leverage are sizing. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving brackets not ported (mark).
    2 generic: PASS, SuperTrend agreement and RSI extremes with a bars-since gate.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the portfolio share, leverage and percent levels stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_448076_four_trendflow_rsi_extreme_gated_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "min_bars": [5, 10],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"min_bars": 5, "rsi_len": 14, "os": 30.0, "ob": 70.0}
FLOWS = ((7, 4.0), (14, 3.618), (21, 3.5), (28, 3.382))


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
    return 100 - 100 / (1 + up / dn)


def _flow(hl2, cv, atr, mult):
    """trendFlow as written: nz() seeds count the previous lines as 0."""
    m = len(cv)
    tr_ = np.ones(m)
    up_p = dn_p = 0.0
    t = 1.0
    for i in range(m):
        up = hl2[i] - mult * atr[i]
        dn = hl2[i] + mult * atr[i]
        c1 = cv[i - 1] if i > 0 else np.nan
        if cv[i] > up_p and c1 > up_p:
            up = np.nan if np.isnan(up) else max(up, up_p)
        if cv[i] < dn_p and c1 < dn_p:
            dn = np.nan if np.isnan(dn) else min(dn, dn_p)
        if cv[i] > dn_p:
            t = 1.0
        elif cv[i] < up_p:
            t = -1.0
        tr_[i] = t
        up_p = 0.0 if np.isnan(up) else up
        dn_p = 0.0 if np.isnan(dn) else dn
    return tr_


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan                               # v4 tr is na on the first bar
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    trends = [_flow(hl2, cv, _rma(tr, n).to_numpy(), mult) for n, mult in FLOWS]
    allup = np.logical_and.reduce([t == 1 for t in trends])
    alldn = np.logical_and.reduce([t == -1 for t in trends])
    m = len(cv)
    since = np.full(m, np.nan)                        # barssince(all-down), na before the first one
    last = -1
    for i in range(m):
        if alldn[i]:
            last = i
        if last >= 0:
            since[i] = i - last
    with np.errstate(invalid="ignore"):
        gate = since >= int(p["min_bars"])
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    with np.errstate(invalid="ignore"):
        lg = gate & (allup | (r < float(p["os"])))
        sh = gate & (r > float(p["ob"]))             # the all-down short never passes the gate
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lg & ~sh, index=ix), false, pd.Series(sh, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
