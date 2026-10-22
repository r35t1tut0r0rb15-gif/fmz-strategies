"""Bollinger 20 / 2 lower-band touches with RSI 14 under 40, hourly bars, long only: such a close buys; a close near the upper band, RSI over 60 or a close 2 % above the entry price closes.
Port of FMZ strategy #477555 "RSI与布林带协同波段交易策略-RSI-and-Bollinger-Bands-Synergistic-Swing-Trading-Strategy" (Demo GPT - Adjusted Swing Trading for SBI).

FMZ source id: 477555

Source
    https://www.fmz.com/strategy/477555 (PineScript v5, FMZ last modified 2025-01-06 13:51:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-183), RSI 14, 60 / 40; BB 20 / 2 (within 1 %); SMA 50 plotted only; commission 0.1 %, slippage 3
    close <= lower x 1.01 and rsi < 40 -> entry Swing Long SBI;  long and (close >= upper x 0.99 or rsi > 60 or close >= avg x 1.02) -> close Swing Long SBI

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are bar-close tests, the last one on the entry price, so a loop tracks it (the fill
      open) and closes at the next open. A buy signal while long is ignored. Long only. The commission and
      slippage settings are costs and are not ported (house cost model). No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band / RSI dips with band, RSI and 2 % profit closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; commission / slippage not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477555_bb20_lower_rsi40_dip_profit2_close_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 50],
    "profit_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"bb_length": 20, "profit_pct": 0.02, "bb_mult": 2.0, "rsi_length": 14}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_length"]))
    buy = ((c <= (basis - dev) * 1.01) & (r < 40)).to_numpy()
    sell = ((c >= (basis + dev) * 0.99) | (r > 60)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = 1 + float(p["profit_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, avg = 0, 0, np.nan
    for i in range(m):
        if nxt == 1 and pos == 0:
            avg = ov[i]
        pos = nxt
        if buy[i] and pos == 0:
            le[i], nxt = True, 1
        if pos == 1 and (sell[i] or cv[i] >= avg * k):
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
