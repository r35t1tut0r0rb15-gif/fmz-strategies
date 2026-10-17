"""Triple cross confirmation in the SMA 50 trend with a 1.5 % / 3 % bracket and a tick trail, long only, hourly bars:
RSI 14 crossing above its SMA 14, the MACD crossing above its signal and the stochastic 14 crossing above its SMA 14 on
the same bar, with the close above SMA 50, goes long; a 1.5 % stop, a 3 % target and a trail a few ticks behind the
best price close it.
Port of FMZ strategy #490042 "多重背离综合指标交易策略-Multi-Indicator-Divergence-Trading-System-with-Advanced-Risk-Management" (Multi-Divergence Strategy - Verbeterd).

FMZ source id: 490042

Source
    https://www.fmz.com/strategy/490042 (PineScript v5, FMZ last modified 2025-04-11 09:22:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 214-262), RSI 14 / SMA 14, MACD 12 / 26 / 9, stochastic 14 / SMA 14, SMA 50, SL 1.5 %, TP 3 %, trail 10 / 5
    buy = crossover(rsi, sma(rsi)) and crossover(macd, signal) and crossover(stoch, sma(stoch)) and close > sma50
    every bar: exit(stop = avg price x 0.985, limit = avg price x 1.03, trail_points = 10, trail_offset = 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is relative to the position's average price (the fill): sl_stop 1.5 %, tp_stop 3 % of the fill
      (scalars, exact).
    * trail_points / trail_offset are ticks: ported natively (mark trailing_stop): {"type": "volatility", "atr_n": 14,
      "k": 0.002, "anchor": "high_low", "activate_after": 0.000033}. Stated approximation: on the author's hourly
      ETH_USDT (tick 0.01, price about 3000) 5 ticks are about 0.002 hourly ATR and 10 ticks a 0.0033 % gain
      (judgement before any backtest), as #428795: as written the trail exits on the first small retrace.
    * Long only (no short entry is coded; the sell condition is unused). Stop module: portfolio_kwargs {} (D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill; the trail a house trail (approximation stated).
    2 generic: ADAPT, tick trail -> ATR multiple / fraction; percentage bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the exits ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_490042_triple_cross_sma50_bracket_trail_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_k": [0.002, 0.5],
    "ma_len": [50, 100],
}
DEFAULT_PARAMS = {"ma_len": 50, "sl_pct": 1.5, "tp_pct": 3.0, "trail_k": 0.002, "trail_activate": 0.000033,
                  "atr_len": 14}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _xup(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rsi = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    ll, hh = lo.rolling(14).min(), h.rolling(14).max()
    stoch = (100 * (c - ll) / (hh - ll)).where(hh != ll)
    buy = (_xup(rsi, rsi.rolling(14).mean()) & _xup(macd, sig) & _xup(stoch, stoch.rolling(14).mean())
           & (c > c.rolling(int(p["ma_len"])).mean())).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100,
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
