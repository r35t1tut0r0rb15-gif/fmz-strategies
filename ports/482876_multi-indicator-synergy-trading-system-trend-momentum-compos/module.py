"""SMA 50 / 200 crosses on the same bar as a MACD cross with RSI off its extreme, with a 2 % stop, a 4 % target and a
1 % trail from the entry, 1-hour bars: both crossing up (RSI below 70) goes long; both down (RSI above 30) goes short.
Port of FMZ strategy #482876 "多重指标协同交易系统-基于趋势动量复合信号策略-Multi-Indicator-Synergy-Trading-System-Trend-Momentum-Composite-Signal-Strategy" (Optimal Multi-Indicator Strategy).

FMZ source id: 482876

Source
    https://www.fmz.com/strategy/482876 (PineScript v5, FMZ last modified 2025-02-20 16:10:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 112-156), SMA 50 / 200, RSI 14 (70 / 30), MACD 12 / 26 / 9, SL 2 %, TP 4 %,
trail 1 %
    long = crossover(sma50, sma200) and rsi < 70 and crossover(macd, signal) (short mirrored)
    entry + exit(stop = avg_price x 0.98, limit = avg_price x 1.04, trail_price = avg_price x 0.99,
    trail_offset = 1 % of close) on the signal bar; exitLong / exitShort are computed but never used

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is issued only on signal bars from strategy.position_avg_price, na while flat: from flat no stop, target
      or trail is placed, as written. The port applies them from the fill (the evident intent), as #489289. Decision
      owed: keep this, or port the literal behaviour.
    * The trail (activation at avg x 0.99, offset 1 % of the close) is the house trail {"type": "percent", "pct": 0.01,
      "anchor": "high_low"} with no activation (for a long the activation price is already passed at entry; for a short
      the same avg x 0.99 would mean a 1 % profit first: stated approximation). Mark trailing_stop.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket and trail from the fill (decision owed).
    2 generic: PASS, moving averages, RSI, MACD and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the exits ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482876_sma_macd_joint_cross_bracket_trail"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [1.0, 2.0],
    "tp_pct": [4.0, 6.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sl_pct": 2.0, "tp_pct": 4.0, "trail_pct": 1.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(50).mean(), c.rolling(200).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi < 70) & (macd > sig) & (macd.shift(1) <= sig.shift(1)))
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi > 30) & (macd < sig) & (macd.shift(1) >= sig.shift(1)))
    false = pd.Series(False, index=bars_df.index)
    return long_e.astype(bool), false, short_e.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100,
            "trail": {"type": "percent", "pct": float(p["trail_pct"]) / 100, "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
