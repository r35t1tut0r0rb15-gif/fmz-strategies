"""Many-signal swing entries, 2-hour bars: SMA 50 / 200 trend crossings with RSI and MACD, level breakouts, ATR-band breakouts, pin / engulfing candles and any close change beyond a tiny step each send
an entry; the last one written on a bar wins; reversing.
Port of FMZ strategy #440540 "Multi Timeframe Gold Reversal Tracking Strategy" (PratikMoney_Gold_Swing_v2.0).

FMZ source id: 440540

Source
    https://www.fmz.com/strategy/440540 (PineScript v5, FMZ last modified 2024-01-31 15:01:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 158-231), resistance 1500, support 1400 (price constants); Fibonacci 0.618 (unused); ATR x 1.5; scalp step 0.1 (price units)
    entries in order: TrendLong / TrendShort (sma 50 x 200 cross, rsi, macd), BreakoutLong / Short (close crossing 1500 / 1400), VolatilityLong / Short (close beyond sma20 +/- 1.5 atr20),
    PriceActionLong (pin bar or engulfing and close > open) / PriceActionShort, ScalpLong (change(close) > 0.1) / ScalpShort (< -0.1)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels are prices (gold levels); the port uses fractions of the close at the BTC
      reading near 42000 (1500 -> 0.0357, 1400 -> 0.0333, 0.1 -> 2.4e-6): as written for BTC the level
      breakouts never fire and the scalp entries fire on almost every bar. All entries share one
      position (pyramiding 1); on a bar with several, the last written wins (as #437773). The Fibonacci
      tests and plots are unused. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "2h" from the backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price levels and step -> fractions of the close.
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

NAME = "fmz_440540_gold_swing_many_signals_last_wins"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_level": [1.5, 3.0],
    "scalp_frac": [2.4e-6, 0.002],
}
DEFAULT_PARAMS = {"atr_level": 1.5, "scalp_frac": 2.4e-6, "res_frac": 0.0357, "sup_frac": 0.0333}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    f50, s200 = c.rolling(50).mean(), c.rolling(200).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    div = macd - macd.ewm(span=9, adjust=False).mean()
    t_up = (f50 > s200) & (f50.shift(1) <= s200.shift(1)) & (r > 50) & (macd > 0) & (div > 0)
    t_dn = (f50 < s200) & (f50.shift(1) >= s200.shift(1)) & (r < 50) & (macd < 0) & (div < 0)
    res, sup = float(p["res_frac"]) * c, float(p["sup_frac"]) * c.shift(1)
    b_up = (c > res) & (c.shift(1) <= float(p["res_frac"]) * c.shift(1))
    b_dn = (c < float(p["sup_frac"]) * c) & (c.shift(1) >= sup)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr20 = _rma(tr, 20)
    m20 = c.rolling(20).mean()
    v_up = c > m20 + float(p["atr_level"]) * atr20
    v_dn = c < m20 - float(p["atr_level"]) * atr20
    pin = (c < o) & (lo < c.shift(1)) & (c > o.shift(1))
    eng = (c < o) & (c.shift(1) > o) & (c.shift(2) > o.shift(1)) & (c > o.shift(2))
    pa_l = pin | (eng & (c > o))
    pa_s = pin | (eng & (c < o))
    step = float(p["scalp_frac"]) * c
    sc_l = (c - pc) > step
    sc_s = (c - pc) < -step
    order = [(t_up, 1), (t_dn, -1), (b_up, 1), (b_dn, -1), (v_up, 1), (v_dn, -1), (pa_l, 1), (pa_s, -1),
             (sc_l, 1), (sc_s, -1)]
    last = np.zeros(len(c), dtype=np.int8)
    for cond, d in order:
        last = np.where(cond.to_numpy(), d, last)          # the last entry written wins
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(last == 1, index=ix), false, pd.Series(last == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
