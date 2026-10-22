"""MACD-V (5-minute EMA 12 / 26 over ATR 26) momentum against 30-minute Fibonacci levels, 1-hour bars, from flat: retracing or reversing MACD-V under its signal below the 38.2 / 61.8 % level goes short,
rebounding or rallying above it goes long; a 20000-tick stop (13.33 ATR) closes; the 1000 / 30000-tick trailing stop is not ported.
Port of FMZ strategy #449508 "MACD-V和斐波那契多时间框架动态止盈策略-MACD-V-and-Fibonacci-Multi-Timeframe-Dynamic-Take-Profit-Strategy" (Advanced MACD-V and Fibonacci Strategy with EMA Trailing TP).

FMZ source id: 449508

Source
    https://www.fmz.com/strategy/449508 (PineScript v5, FMZ last modified 2024-06-25 11:28:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-280), MACD-V 12 / 26 / 9, ATR 26 on the 5-minute time frame; Fibonacci 9 bars on the 30-minute time frame; trail 1000 / 30000 ticks; loss 20000 ticks; 1000 % of equity, margin 5 x
    macd = (ema12_5m - ema26_5m) / atr26_5m x 100;  signal = ema(macd, 9);  hist;  fib levels from the 30-minute 9-bar high / low (direction by highestbars / lowestbars)
    sell_retracing / sell_reversing (macd < signal, hist falling, close < fib 38.2 / 61.8) -> entry short;  buy_rebound / buy_rallying (macd > signal, hist rising, close vs fib) -> entry long  (only with no open trade)
    exit(trail_points = 1000, trail_offset = 30000, loss = 20000) for every id

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 5- and 30-minute requests on a 1-hour chart return the hour's LAST 5- and 30-minute bars (a
      lower time frame returns its last bar inside the chart bar, as #436765), built left-labelled from
      the minutes. highestbars / lowestbars give the offset of the newest extreme. Entries only with no
      open trade; the buy calls come after the sells (later call wins, as #437773). Criterion 2: the
      20000-tick loss (mintick 0.1 = 2000 price units) is sl_stop = 13.33 x ATR(14) / close of the
      signal bar against a 1-hour BTC ATR near 150, shifted one bar inside stops() and re-based on the
      fill; the port follows that stop in its own state so the from-flat entries line up. The trailing
      exit (activation 1000 ticks, offset 30000 ticks) is not expressible as written (mark
      trailing_stop_pending). Entries only from flat, so positions never reverse. Stop module:
      portfolio_kwargs {} (driver D4). The 1000 % of equity, margins and commission are sizing / costs.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 5- and 30-minute values end with the hourly bar; the trailing exit not ported (mark).
    2 generic: PASS, MACD-V momentum against Fibonacci levels with a tick stop as an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1000 % of equity size and margins stored; the commission is a cost, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_449508_macdv_5m_fib_30m_from_flat_atr_stop"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [13.33, 5.0],
    "fib_lookback": [9, 20],
}
DEFAULT_PARAMS = {"k_atr": 13.33, "fib_lookback": 9, "fast": 12, "slow": 26, "signal": 9, "atr_len": 26, "stop_atr_len": 14}


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


def _atr(df, n):
    h, lo, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    m5 = _resample(raw_1m_df, "5min")
    c5 = m5["close"]
    k5 = m5.index.floor("1h")
    for name, s in (("atr5", _atr(m5, p["atr_len"])),
                    ("ef5", c5.ewm(span=int(p["fast"]), adjust=False).mean()),
                    ("es5", c5.ewm(span=int(p["slow"]), adjust=False).mean())):
        bars[name] = s.groupby(k5).last().reindex(bars.index).to_numpy()      # the hour's last 5-minute bar
    m30 = _resample(raw_1m_df, "30min")
    n = int(p["fib_lookback"])
    hb = -m30["high"].rolling(n).apply(lambda a: np.argmax(a[::-1]), raw=True)   # highestbars: offset of the newest high
    lb = -m30["low"].rolling(n).apply(lambda a: np.argmin(a[::-1]), raw=True)
    k30 = m30.index.floor("1h")
    for name, s in (("h30", m30["high"].rolling(n).max()), ("l30", m30["low"].rolling(n).min()),
                    ("hbars", -hb), ("lbars", -lb)):
        bars[name] = s.groupby(k30).last().reindex(bars.index).to_numpy()     # the hour's last 30-minute bar
    return bars


def _signals(bars_df, p):
    c = bars_df["close"]
    macd = (bars_df["ef5"] - bars_df["es5"]) / bars_df["atr5"] * 100
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    hist = macd - sig
    hp = hist.shift(1)
    h1, l1 = bars_df["h30"], bars_df["l30"]
    fark = h1 - l1
    up = bars_df["hbars"] > bars_df["lbars"]
    f382 = (l1 + fark * 0.382).where(up, h1 - fark * 0.382)
    f618 = (l1 + fark * 0.618).where(up, h1 - fark * 0.618)
    sell = (((sig > -20) & (macd > -50) & (macd < 150) & (macd < sig) & (hist < hp) & (c < f382))
            | ((macd > -150) & (macd < -50) & (macd < sig) & (hist < hp) & (c < f618)))
    buy = (((sig < 20) & (macd > -150) & (macd < 50) & (macd > sig) & (hist > hp)
            & ((f618 < c) | ((f618 > c) & (c > f382))))
           | ((macd > 50) & (macd < 150) & (macd > sig) & (hist > hp) & (c > f618)))
    frac = float(p["k_atr"]) * _atr(bars_df, p["stop_atr_len"]) / c
    return buy.to_numpy(), sell.to_numpy(), frac


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, frac = _signals(bars_df, p)
    fr = frac.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill_i, lvl = 0, -1, np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pos != 0 and i >= fill_i:              # the stop, followed so the from-flat entries line up
                if (pos == 1 and lv[i] <= lvl) or (pos == -1 and hv[i] >= lvl):
                    pos = 0
            if pos == 0 and i + 1 < m:
                d = 1 if buy[i] else (-1 if sell[i] else 0)   # the buys are called after the sells
                if d != 0:
                    le[i], se[i] = d == 1, d == -1
                    pos, fill_i = d, i + 1
                    lvl = ov[i + 1] * (1 - d * fr[i]) if not np.isnan(fr[i]) else np.nan
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, frac = _signals(bars_df, p)
    return {"sl_stop": frac.shift(1)}


def portfolio_kwargs(**params):
    return {}
