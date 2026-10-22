"""RSI 14 crossings of its SMA 10 in Prague day hours, 3-hour bars: RSI crossing over its average while under 45 goes long, crossing under while over 55 goes short, on bars opening 08:00-21:00 Europe/Prague with ATR over 0.5; reversing. Each trade's stop is 5000 ticks beyond the signal bar's low / high and its target 5000 ticks beyond the other extreme, as ATR multiples.
Port of FMZ strategy #474634 "RSI-ATR动量波动组合交易策略-RSI-ATR-Momentum-Volatility-Combined-Trading-Strategy" (Custom RSI + ATR Strategy).

FMZ source id: 474634

Source
    https://www.fmz.com/strategy/474634 (PineScript v5, FMZ last modified 2024-12-11 11:15:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-154), RSI 14, SMA 10 of RSI; ATR 14, threshold 0.5; stop / target 5000 ticks from the signal low / high; 08:00-21:00 Europe/Prague
    crossover(rsi, rsi_ma) and rsi < 45 and in hours and atr > 0.5 -> entry Long, exit(stop = low - 5000 ticks, limit = high + 5000 ticks);  crossunder and rsi > 55 and in hours and atr > 0.5 -> entry Short, exit(stop = high + 5000 ticks, limit = low - 5000 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 5000 ticks are 500 at the 0.1 tick, ported as ATR multiples at an interpolated 3-hour reading
      of about 350 (as #442644): 1.43 ATR 14 of the signal bar, beyond its low / high. The ATR threshold
      0.5 is a price amount, ported as 0.5 / 42000 of the close. The hours test reads the bar's open
      time in Europe/Prague (its daylight time applied by the zone), 08:00 to 21:00 inclusive. The
      levels are sent as fractions of the fill open; a level at or through it is marketable and closed
      one bar late (as #458256). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 3-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples from the signal bar's extremes.
    2 generic: PASS, RSI / RSI-average crossings in day hours with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 08:00-21:00 Europe/Prague bar opens (zone daylight time).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474634_rsi_sma10_cross_prague_hours_atr_bracket_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [1.43, 0.5],
    "rsi_ma_length": [10, 20],
}
DEFAULT_PARAMS = {"k_atr": 1.43, "rsi_ma_length": 10, "atr_frac": 1.19e-05}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, 14)
    rm = r.rolling(int(p["rsi_ma_length"])).mean()
    atr = _atr(bars_df, 14)
    loc = bars_df.index.tz_convert("Europe/Prague")
    mins = loc.hour * 60 + loc.minute
    hours = pd.Series((mins >= 8 * 60) & (mins <= 21 * 60), index=bars_df.index)
    vol = atr / c > float(p["atr_frac"])
    le = (r > rm) & (r.shift(1) <= rm.shift(1)) & (r < 45) & hours & vol
    se = (r < rm) & (r.shift(1) >= rm.shift(1)) & (r > 55) & hours & vol
    k = float(p["k_atr"]) * atr
    lvl = {"l_sl": lo - k, "l_tp": h + k, "s_sl": h + k, "s_tp": lo - k}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
