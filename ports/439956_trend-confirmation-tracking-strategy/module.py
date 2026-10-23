"""Hourly bars: the supertrend (3 x ATR 10) in its DOWN state (direction > 0, as written) with the MACD 12 / 26 above its signal and the close above the session VWAP goes long; the UP state with the MACD below its signal and the close under the VWAP goes short; the MACD crossing back closes each; reversing.
Port of FMZ strategy #439956 "Trend Confirmation Tracking Strategy" (Trend Confirmation Strategy).

FMZ source id: 439956

Source
    https://www.fmz.com/strategy/439956 (PineScript v5, FMZ last modified 2024-01-25 11:57:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 164-220), supertrend factor 3, ATR 10; MACD 12 / 26 / 9 (EMA); vwap(hlc3); stop-loss range 2 and trail offset 0.5 unused
    confirm_up_trend = direction > 0 and macd > signal;  close > vwap -> entry Buy;  confirm_down_trend = direction < 0 and macd < signal;  close < vwap -> entry Sell
    macd crossing under signal -> close Buy;  crossing over -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's ta.supertrend direction is -1 in an up-trend and +1 in a down-trend, so "direction > 0"
      buys in the supertrend's down state, as written (weird case). vwap(hlc3) is the session VWAP,
      anchored at the broker-day start (as earlier ports). A close acts only on a position the bar's
      entries leave unchanged. The stop-loss range and trail offset feed nothing. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, supertrend state with MACD and VWAP confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session VWAP's weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439956_supertrend_state_inverted_macd_vwap_1h_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_period": 10, "fast": 12, "slow": 26, "signal": 9}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    direc = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))[1]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    day = broker_day(c.index)
    hlc3 = (h + lo + c) / 3
    cv = v.groupby(day).cumsum()
    vwap = (hlc3 * v).groupby(day).cumsum() / cv.where(cv != 0)
    buy = ((direc > 0) & (macd > sig) & (c > vwap)).to_numpy()
    sell = ((direc < 0) & (macd < sig) & (c < vwap)).to_numpy()
    x_dn = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    x_up = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and x_dn[i]:
                new = 0
            elif pos == -1 and x_up[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
