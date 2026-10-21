"""RSI 14 crossings of 60 / 40 with a point bracket, 45-minute bars: the RSI crossing over 60 goes long with a stop 50 and a target 100 price units from the fill (re-expressed as fractions); crossing under
40 goes short; reversing; the short's exit uses the long target, which sits on the wrong side, so a short closes at the open after its first bar.
Port of FMZ strategy #439050 "RSI指标追踪止盈止损策略RSI-Target-and-Stop-Loss-Tracking-Strategy" (RSI TARGET & STOPLOSS).

FMZ source id: 439050

Source
    https://www.fmz.com/strategy/439050 (PineScript v5, FMZ last modified 2024-01-17 11:52:23).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 136-170), RSI 14; long stop 50, target 100; short stop 50, target 100 (price units)
    crossover(rsi, 60) -> entry long;  long: exit(limit = avg + 100, stop = avg - 50);  crossunder(rsi, 40) -> entry short;  short: exit(limit = longtarget = avg + 100, stop = avg + 50)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the point bracket is price units; the port uses fractions of the fill: 0.00114 / 0.00227
      are the reading (50 / 100 on BTC near 44000), 0.01 / 0.02 a wider pair, set on the long fills only.
      The short's exit names the LONG target (avg + 100), a buy limit above the market, so the short is
      closed at the open after its first bar (as written; owed: shorttarget): the port closes it with an
      exit signal on the fill bar. The bracket is sent from the first bar close inside the trade; the port
      starts it at the fill. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; the short's immediate exit as a signal.
    2 generic: ADAPT, price-unit bracket -> fractions of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point inputs stored.
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

NAME = "fmz_439050_rsi_60_40_point_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [0.00114, 0.01],
    "rsi_len": [14, 21],
}
DEFAULT_PARAMS = {"stop_frac": 0.00114, "rsi_len": 14, "target_ratio": 2.0}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _signals(bars_df, p):
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    buy = ((r > 60) & (r.shift(1) <= 60)).to_numpy()
    short = ((r < 40) & (r.shift(1) >= 40)).to_numpy()
    return buy, short


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, short = _signals(bars_df, p)
    m = len(buy)
    le, se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    for i in range(m):
        if pend:                                         # the entry of the last bar fills at this open
            pos, pend = pend, 0
        if pos == -1 and not buy[i]:
            sx[i], pos = True, 0                         # the wrong-side target closes it at the next open
        if buy[i] and pos != 1 and i + 1 < m:
            le[i], pend = True, 1
        elif short[i] and pos != -1 and i + 1 < m:
            se[i], pend = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, _ = _signals(bars_df, p)
    sf = float(p["stop_frac"])
    sl = pd.Series(np.where(buy, sf, np.nan), index=bars_df.index)
    tp = pd.Series(np.where(buy, sf * float(p["target_ratio"]), np.nan), index=bars_df.index)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
