"""Six entry ids in call order, 1-hour bars: close / SMA 50 crossings, RSI 14 levels (over 70 short, under 30 long) and MACD (12, 26, 9) crossings; because the "short" signal is the same crossing as the
buy, a close crossing over the SMA 50 ends short; reversing.
Port of FMZ strategy #446232 "Trend Momentum Based Multi Indicator Moving Average Crossover Strategy" (Enhanced Moving Average Crossover Strategy).

FMZ source id: 446232

Source
    https://www.fmz.com/strategy/446232 (PineScript v4, FMZ last modified 2024-03-26 17:17:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-197), SMA 20 (plot) / 50; RSI 14, levels 70 / 30; MACD 12 / 26 / 9
    crossover(close, sma50) -> entry Long;  crossunder(close, sma50) -> close Long;  crossunder(sma50, close) (the same crossing as the buy) -> entry Short;  buy -> close Short
    rsi > 70 -> entry RSI Short;  rsi < 30 -> entry RSI Long;  crossover(macd, signal) -> entry MACD Buy;  crossunder -> entry MACD Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossunder(slowMA, close) is crossover(close, slowMA), so the Short entry fires on every buy bar
      and, called after the Long entry, wins it (later call wins, as #437773). The calls run in the
      script's order with one position (pyramiding 1): an entry on the side already held or ordered
      that bar is ignored; a close acts only on the id held into the bar and not reversed by that bar's
      entries. When a close and a new entry on the same side meet on one bar the position is kept
      under the new id (vbt cannot close and reopen at one open). The RSI entries are levels, re-sent
      every bar. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA, RSI and MACD entries in call order.
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

NAME = "fmz_446232_sma50_rsi_macd_six_ids_call_order_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [50, 100],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"slow": 50, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = c.rolling(int(p["slow"])).mean()
    c1, s1 = c.shift(1), s.shift(1)
    buy = ((c > s) & (c1 <= s1)).to_numpy()
    sell = ((c < s) & (c1 >= s1)).to_numpy()
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    mxo = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    mxu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    ob, os_ = float(p["ob"]), float(p["os"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    hd, hid = 0, None                                  # the position held into the bar: side and id
    with np.errstate(invalid="ignore"):
        for i in range(m):
            cd, cid = hd, hid

            def entry(name, d):
                nonlocal cd, cid
                if cd != d:
                    cd, cid = d, name

            def close(name):
                nonlocal cd, cid
                if hid == name and cd == hd and cid == hid:
                    cd, cid = 0, None

            if buy[i]:
                entry("Long", 1)
            if sell[i]:
                close("Long")
            if buy[i]:                                 # crossunder(slowMA, close) is the same crossing
                entry("Short", -1)
                close("Short")
            if r[i] > ob:
                entry("RSI Short", -1)
            if r[i] < os_:
                entry("RSI Long", 1)
            if mxo[i]:
                entry("MACD Buy", 1)
            if mxu[i]:
                entry("MACD Sell", -1)
            if cd != hd:
                if cd == 1:
                    le[i] = True
                elif cd == -1:
                    se[i] = True
                elif hd == 1:
                    lx[i] = True
                else:
                    sx[i] = True
            hd, hid = cd, cid
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
