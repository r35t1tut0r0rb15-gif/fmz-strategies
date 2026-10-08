"""Bullish harami, long only: a green bar whose body sits inside the previous red body stores its
close as the trade price and holds long; the stored price is cleared (and the long closed on
the next bar) once a bar's low reaches price - stop or its high price + target.
Port of FMZ strategy #426376 "Bullish Harami Reversal Strategy".

Source
    https://www.fmz.com/strategy/426376 (PineScript v3, FMZ last modified 2023-09-11 16:26:57).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 91-105), TP 60, SL 18, min body 1 ("pip" = price unit)
    harami = |close - open| >= minbody and open[1] > close[1] and close > open
             and close <= open[1] and close[1] <= open and close - open < open[1] - close[1]
    posprice = harami ? close : nz(posprice[1])
    posprice > 0 -> entry long, else close_all
    then posprice = 0 if low <= posprice - SL;  then posprice = 0 if high >= posprice + TP

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop / target reset posprice on the bar close; the long is closed by close_all on the
      next bar, so both are close-based exit signals (no sl_stop / tp_stop). They are tested on
      the signal bar itself too, as written.
    * Criterion 2: SL / TP / min body are price units (BTC: 18 / 60 / 1 USDT, a small fraction
      of a daily ATR). SL and TP become sl_atr / tp_atr x ATR(14) at the harami bar, TP kept at
      the source's 60 / 18 of SL; the minimum body is min_body_atr x ATR(14) on the bar (0 by
      default: 1 USDT is under 0.01 ATR).
    * Long only (no short entry). Daily bars are broker days (session ending 17:00 New York),
      stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426376_bullish_harami"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)
TP_RATIO = 60 / 18  # the source's target / stop

GRID = {
    "sl_atr": [0.25, 0.5, 1.0],
}
DEFAULT_PARAMS = {"sl_atr": 0.25, "min_body_atr": 0.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    atr = _atr_pine(bars_df, ATR_LEN)
    o1, c1 = o.shift(1), c.shift(1)
    harami = (((c - o).abs() >= p["min_body_atr"] * atr) & (o1 > c1) & (c > o) & (c <= o1)
              & (c1 <= o) & ((c - o) < (o1 - c1))).to_numpy()
    av, hv, lv, cv = atr.to_numpy(), h.to_numpy(dtype=float), l.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    target = np.zeros(m, dtype=int)
    price, risk = 0.0, np.nan
    for i in range(m):
        if harami[i]:
            price, risk = cv[i], p["sl_atr"] * av[i]
        target[i] = 1 if price > 0 else 0
        if price > 0 and lv[i] <= price - risk:
            price = 0.0
        if price > 0 and hv[i] >= price + TP_RATIO * risk:
            price = 0.0
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
