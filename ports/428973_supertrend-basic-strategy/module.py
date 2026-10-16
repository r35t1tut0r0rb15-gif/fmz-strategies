"""SuperTrend pullback with a 1 % bracket, 2-hour bars: in a SuperTrend up-trend, the previous low dipping
under the line and a higher high, above the EMA 200 with RSI 14 >= 50, goes long from flat (mirror for
shorts); each trade has a 1 % stop and a 1 % target.
Port of FMZ strategy #428973 "SuperTrend Basic Strategy".

FMZ source id: 428973

Source
    https://www.fmz.com/strategy/428973 (PineScript v5, FMZ last modified 2023-10-11 15:14:54).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 266-357), SuperTrend 10 / 3, EMA 200, RSI 14 vs 50, stop / target 1 %, type Pullback
    long = direction < 0 ? supertrend : na; short = direction < 0 ? na : supertrend
    pullbuy = crossunder(low[1], long) and long and high > high[1]; pullsell = crossover(high[1], short) and short and low < low[1]
    flat and pullbuy and close > ema200 and rsi >= 50 -> entry long; flat and pullsell and close < ema200 and rsi <= 50 -> entry short
    exit(stop = avg x (1 -/+ 1 %), limit = avg x (1 +/- 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as Pine defines it (hl2, Wilder ATR, bands ratcheted on close[1], direction -1 =
      up-trend). "Type Of Strategy" defaults to Pullback (Simple is an option).
    * The strategy() line (process_orders_on_close = false) is commented out: bar-close orders.
    * The bracket is 1 % of the average entry price (the fill): sl_stop / tp_stop 0.01.
    * "Flat" follows the house bracket: the loop marks the position closed once a bar's high / low
      reaches the stop or target from the fill price (next open). Opposite entries cannot occur.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop.
      FREQ = "2h" from the backtest header. The date inputs are dropped (time_cond is true).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, an ATR multiple, RSI levels and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_428973_supertrend_pullback_bracket"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "bracket_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"atr_period": 10, "factor": 3.0, "ema_length": 200, "rsi_length": 14, "rsi_buy": 50,
                  "rsi_sell": 50, "bracket_pct": 1.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    st, d = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))
    lng = st.where(d < 0)
    sht = st.where(d >= 0)
    l1, h1 = lo.shift(1), h.shift(1)
    pull_buy = (l1 < lng) & (l1.shift(1) >= lng.shift(1)) & lng.notna() & (h > h1)
    pull_sell = (h1 > sht) & (h1.shift(1) <= sht.shift(1)) & sht.notna() & (lo < lo.shift(1))
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    buy = (pull_buy & (r >= p["rsi_buy"]) & (c > ema)).to_numpy()
    sell = (pull_sell & (r <= p["rsi_sell"]) & (c < ema)).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    b = p["bracket_pct"] / 100
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - b) or hv[i] >= e * (1 + b)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + b) or lv[i] <= e * (1 - b)):
                pos = 0
        if pos == 0 and buy[i]:
            le[i], pos, entry_i = True, 1, i + 1
        elif pos == 0 and sell[i]:
            se[i], pos, entry_i = True, -1, i + 1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    b = float(p["bracket_pct"]) / 100
    return {"sl_stop": b, "tp_stop": b}


def portfolio_kwargs(**params):
    return {}
