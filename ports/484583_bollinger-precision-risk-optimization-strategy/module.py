"""Bollinger 20 / 2 re-entries with RSI 14 extremes, hourly bars: the close crossing back over the lower band with RSI under 30 goes long (closing a short), back under the upper band with RSI over 70 goes short; each with a 4 % stop and an 8 % target from the signal close; reversing.
Port of FMZ strategy #484583 "Bollinger Precision Risk Optimization Strategy" (Bollinger Precision Strategy).

FMZ source id: 484583

Source
    https://www.fmz.com/strategy/484583 (PineScript v6, FMZ last modified 2025-03-03 10:07:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 184-252), Bollinger 20 x 2.0; RSI 14 / 30 / 70; stop 4 %; target 8 % (both on); 2 % of equity, capital 10000
    crossover(close, lower) and rsi < 30 -> entry Long, close Short + exit(stop = close x 0.96, limit = close x 1.08)
    crossunder(close, upper) and rsi > 70 -> entry Short, close Long + exit(stop = close x 1.04, limit = close x 0.92)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both bracket switches are on by default. The levels are fixed at the signal close and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A repeat signal while held re-sends the bracket; stops() keeps the first, so the repeat
      case is marked trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). The 2 % of equity size and the capital are
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, Bollinger re-entries with RSI extremes.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 2 % of equity and capital stored, not ported.
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

NAME = "fmz_484583_bb20_2_reentry_rsi14_4_8pct_bracket_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_percent": [4.0, 2.0],
    "take_profit_percent": [8.0, 4.0],
}
DEFAULT_PARAMS = {"stop_loss_percent": 4.0, "take_profit_percent": 8.0, "bb_length": 20, "bb_mult": 2.0,
                  "rsi_period": 14}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    n = int(p["bb_length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = basis + float(p["bb_mult"]) * sd, basis - float(p["bb_mult"]) * sd
    r = _rsi(c, int(p["rsi_period"]))
    le = (c > dn) & (c.shift(1) <= dn.shift(1)) & (r < 30)
    se = (c < up) & (c.shift(1) >= up.shift(1)) & (r > 70)
    a, b = float(p["stop_loss_percent"]) / 100, float(p["take_profit_percent"]) / 100
    lvl = {"l_sl": c * (1 - a), "l_tp": c * (1 + b), "s_sl": c * (1 + a), "s_tp": c * (1 - b)}
    return le & ~se, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
