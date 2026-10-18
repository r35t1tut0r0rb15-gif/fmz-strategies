"""MACD histogram sign in an EMA 200 trend with RSI limits, 1-hour bars: a positive histogram above the EMA 200 with the RSI at most 70 goes
long (once per swing); a negative histogram below it with the RSI at least 30 goes short; a long closes when the histogram turns negative or
the RSI passes 70 (the short mirrors); after an RSI extreme a reversal entry is taken when the histogram agrees.
Port of FMZ strategy #435775 "基于MACD和RSI的趋势追踪反转策略MACD-and-RSI-Based-Trend-Following-Reversal-Strategy" (CHARL MACD EMA RSI).

FMZ source id: 435775

Source
    https://www.fmz.com/strategy/435775 (PineScript v4, FMZ last modified 2023-12-18 17:53:38).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 180-228), MACD 12 / 26 / 9 (SMA signal); EMA 200; RSI 14; limits 70 / 30
    buy_entry = close > ema200 and delta > 0;  if buy_entry and not bought and rsi <= 70: entry Buy, bought = true;  close Buy when delta < 0 or rsi > 70;  if delta < 0 and bought: bought = false;  the short side mirrors with sold and rsi >= 30 / rsi < 30
    if rsi > 70 or rsi < 30: reversal = true;  if reversal: if rsi < 70 and not sold and delta < 0: entry Sell, sold = true, reversal = false; else if rsi > 30 and not bought and delta > 0: entry Buy, bought = true, reversal = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags bought, sold and reversal are followed inside the script, so a long closed by the
      RSI stays "bought" until the histogram turns negative (no re-entry meanwhile), as written. The
      orders of one bar (entry, close, entry, close, reversal entry) are filled in the script's call
      order at the next open; an entry on the id of an open trade adds nothing and an opposite entry
      reverses. REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram, EMA trend and RSI limits.
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

NAME = "fmz_435775_macd_ema_rsi_flags"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [200, 100],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"ema_len": 200, "rsi_len": 14, "fast": 12, "slow": 26, "signal": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = (macd - macd.rolling(int(p["signal"])).mean()).to_numpy()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    n = int(p["rsi_len"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna()).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    bought = sold = reversal = False
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the order the script sent them
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "cL" and pos == 1:
                    pos = 0
                elif op == "eS" and pos >= 0:
                    pos = -1
                elif op == "cS" and pos == -1:
                    pos = 0
        held[i] = pos
        ops = []
        d, r = delta[i], rsi[i]
        buy_entry = cv[i] > ema[i] and d > 0
        sell_entry = cv[i] < ema[i] and d < 0
        if buy_entry and not bought and r <= 70:
            ops.append("eL")
            bought = True
        if d < 0 or r > 70:
            ops.append("cL")
        if d < 0 and bought:
            bought = False
        if sell_entry and not sold and r >= 30:
            ops.append("eS")
            sold = True
        if d > 0 or r < 30:
            ops.append("cS")
        if d > 0 and sold:
            sold = False
        if r > 70 or r < 30:
            reversal = True
        if reversal:
            if r < 70 and not sold and d < 0:
                ops.append("eS")
                sold = True
                reversal = False
            elif r > 30 and not bought and d > 0:
                ops.append("eL")
                bought = True
                reversal = False
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
