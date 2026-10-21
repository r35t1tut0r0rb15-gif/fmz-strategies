"""RSI breakouts outside an EMA high / low channel with a range target, 1-hour bars: a close above the EMA 5 of highs as the RSI 6 crosses over 70 goes long, a close under the EMA 5 of lows as it crosses under
30 goes short; each trade's target is one signal-bar extension (close minus the previous low, or the previous high minus close) away; reversing.
Port of FMZ strategy #436786 "RSI与EMA通道日内交易策略RSI-and-EMA-Channel-Intraday-Trading-Strategy" (RSI and EMA Channel Daily Strategy).

FMZ source id: 436786

Source
    https://www.fmz.com/strategy/436786 (PineScript v5, FMZ last modified 2023-12-27 16:57:09).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 141-166), EMA 5 of high / low, RSI 6, levels 70 / 30; two targets 1x and 2x the extension
    buy = close > ema(high, 5) and crossover(rsi(close, 6), 70) -> entry Buy, exit TP1 limit = close + (close - low[1]), exit TP2 limit = close + 2 (close - low[1])
    sell = close < ema(low, 5) and crossunder(rsi, 30) -> entry Sell, exit TP1 limit = close - (high[1] - close), TP2 limit = close - 2 (high[1] - close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits are full-position limit orders, so the nearer one (TP1) closes the trade and TP2 is never
      reached: the port has one target, tp_stop = (close - low[1]) / close (long) or (high[1] - close) /
      close (short) of the signal bar, shifted one bar inside stops() and re-based on the fill. A target at
      or beyond the close (the previous low above the close) is left out. There is no stop; trades end at
      the target or by the opposite entry. A later same-side signal re-places the targets of an open trade
      in the script; not ported. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: PASS, range-based target.
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

NAME = "fmz_436786_rsi_ema_channel_range_target"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [6, 9],
    "ema_len": [5, 10],
}
DEFAULT_PARAMS = {"rsi_len": 6, "ema_len": 5, "up": 70.0, "dn": 30.0}


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


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ema_len"])
    eh = h.ewm(span=n, adjust=False).mean()
    el = lo.ewm(span=n, adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    r1 = r.shift(1)
    up, dn = float(p["up"]), float(p["dn"])
    buy = (c > eh) & (r > up) & (r1 <= up)
    sell = (c < el) & (r < dn) & (r1 >= dn)
    tp_l = (c - lo.shift(1)) / c
    tp_s = (h.shift(1) - c) / c
    tp = pd.Series(np.where(buy, tp_l, np.where(sell, tp_s, np.nan)), index=c.index)
    return buy, sell, tp.where(tp > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = _setup(bars_df, p)[2]
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
