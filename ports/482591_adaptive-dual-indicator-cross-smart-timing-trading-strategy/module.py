"""RSI 14 at or below 31 with CCI 20 at or below -120 for two bars goes long; RSI 14 at or above 69 with CCI at or
above 120 goes short at once; trades close when RSI 30 moves 12 points for or 8 points against the entry or CCI falls
100 points against it, hourly bars.
Port of FMZ strategy #482591 "自适应双重指标交叉智能择时交易策略-Adaptive-Dual-Indicator-Cross-Smart-Timing-Trading-Strategy" (RSI & CCI Strategy with Alerts).

FMZ source id: 482591

Source
    https://www.fmz.com/strategy/482591 (PineScript v6, FMZ last modified 2025-02-19 10:56:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-239), on the 60-minute chart: RSI 30, RSI 14, CCI 20, stay 2
    buyOver: rsi14 <= 31 and cci <= -120 has held since bar t0, bar_index - t0 >= 2
    sellOver: rsi14 >= 69 and cci >= 120 has held since t0, bar_index - t0 <= 2 (true from its first bar)
    buyOver and not isLongOpen -> entry long, entry RSI30 / CCI stored; sellOver mirrored
    long open and (rsi30 >= entry + 12 or rsi30 <= entry - 8 or cci <= entry cci - 100) -> close long (short
    mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The per-timeframe input tables resolve, on the 60-minute chart, to RSI 30, CCI 20 and 2 bars. The
      "stayed below -100" conditions are computed but feed no order.
    * The long needs two more bars in the zone ("bar_index - t0 >= 2"), the short none ("<= 2"): as written.
    * isLongOpen / isShortOpen follow the position (entries reverse and set them; closes clear them); a close cannot
      fire on the entry's own bar (the stored values are the bar's own). Exits are emitted only on going flat.
    * CCI = (close - SMA) / (0.015 x mean absolute deviation). Signal module, no stops. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and CCI levels and changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482591_rsi_cci_extreme_dwell_rsi_cci_exit"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stay": [2, 1],
    "cci_level": [120.0, 100.0],
}
DEFAULT_PARAMS = {"rsi_len": 30, "rsi_fast": 14, "cci_len": 20, "stay": 2, "cci_level": 120.0}


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


def _cci(c, n):
    sma = c.rolling(n).mean()
    mad = c.rolling(n).apply(lambda w: np.abs(w - w.mean()).mean(), raw=True)
    return (c - sma) / (0.015 * mad)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    rsi_f = _rsi(c, int(p["rsi_fast"])).to_numpy()
    cci = _cci(c, int(p["cci_len"])).to_numpy()
    lvl, stay = p["cci_level"], int(p["stay"])
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    t_buy = t_sell = None
    is_long = is_short = False
    e_rsi = e_cci = np.nan
    for i in range(m):
        if rsi_f[i] <= 31 and cci[i] <= -lvl:
            t_buy = i if t_buy is None else t_buy
        else:
            t_buy = None
        if rsi_f[i] >= 69 and cci[i] >= lvl:
            t_sell = i if t_sell is None else t_sell
        else:
            t_sell = None
        buy_over = t_buy is not None and i - t_buy >= stay
        sell_over = t_sell is not None and i - t_sell <= stay
        if buy_over and not is_long:
            le[i], is_long, is_short, e_rsi, e_cci = True, True, False, rsi[i], cci[i]
        if sell_over and not is_short:
            se[i], is_short, is_long, e_rsi, e_cci = True, True, False, rsi[i], cci[i]
        if is_long and not le[i] and (rsi[i] >= e_rsi + 12 or rsi[i] <= e_rsi - 8 or cci[i] <= e_cci - 100):
            lx[i], is_long = True, False
        if is_short and not se[i] and (rsi[i] <= e_rsi - 12 or rsi[i] >= e_rsi + 8 or cci[i] >= e_cci + 100):
            sx[i], is_short = True, False
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
