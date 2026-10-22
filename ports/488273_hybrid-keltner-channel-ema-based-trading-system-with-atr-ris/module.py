"""Two entry sets on hourly bars: a close crossing under the lower Keltner band 20 / 1.5 goes long (closed when the close crosses back over the EMA 20 basis), over the upper band goes short; EMA 9 / 21 crossings beside the EMA 50 go long or short (closed on the opposite EMA crossing); one position at a time, reversing (the per-bar ATR bracket is pending).
Port of FMZ strategy #488273 "Hybrid Keltner Channel EMA Based Trading System with ATR Risk Management" (Keltner Channel Strategy).

FMZ source id: 488273

Source
    https://www.fmz.com/strategy/488273 (PineScript v5, FMZ last modified 2025-03-26 14:21:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-228), Keltner EMA 20 / ATR 20 x 1.5; EMA 9 / 21 / 50; bracket 1.5 / 3 ATR; 10 % of equity
    crossunder(close, lowerKC) -> entry Long_KC;  crossover(close, basis) -> close Long_KC;  mirror Short_KC
    crossover(ema9, ema21) and close > ema50 -> entry Long_Trend;  crossunder(ema9, ema21) -> close Long_Trend;  mirror Short_Trend
    every bar: exit(stop = close -/+ 1.5 atr, limit = close +/- 3 atr) for each id

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default pyramiding, an entry under another id on the side already held is refused (as
      #437773), so each position carries one id and only that id's close applies; a loop follows the id.
      From flat a KC entry is placed before the trend entry of its side; when long and short entries meet
      on one bar the short (placed later) wins (as #437773). The brackets are sent on every bar from that
      bar's close: not ported, mark trailing_stop_pending (as the C170-C175 readings). An entry on the
      other side reverses (REVERSAL INTENDED). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, Keltner reversion and EMA trend entries with their own exits.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488273_keltner20_reversion_ema9_21_trend_ids_reversal"
FAMILY = "keltner_channel"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.5, 2.0],
    "length": [20, 30],
}
DEFAULT_PARAMS = {"mult": 1.5, "length": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])

    def ema(x, k):
        return x.ewm(span=k, adjust=False).mean()

    def xo(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()

    basis = ema(c, n)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, n)
    upper, lower = basis + float(p["mult"]) * atr, basis - float(p["mult"]) * atr
    e9, e21, e50 = ema(c, 9), ema(c, 21), ema(c, 50)
    l_kc, s_kc = xo(lower, c), xo(c, upper)
    x_lkc, x_skc = xo(c, basis), xo(basis, c)
    up9, dn9 = xo(e9, e21), xo(e21, e9)
    l_tr = up9 & (c > e50).to_numpy()
    s_tr = dn9 & (c < e50).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    held = None      # the id of the open position, as of this bar's open
    for i in range(m):
        cur = held
        if cur in ("LKC", "LT"):
            if (cur == "LKC" and x_lkc[i]) or (cur == "LT" and dn9[i]):
                lx[i], held = True, None
        elif cur in ("SKC", "ST"):
            if (cur == "SKC" and x_skc[i]) or (cur == "ST" and up9[i]):
                sx[i], held = True, None
        long_id = "LKC" if l_kc[i] else ("LT" if l_tr[i] else None)
        short_id = "SKC" if s_kc[i] else ("ST" if s_tr[i] else None)
        if short_id and cur not in ("SKC", "ST"):
            se[i], held = True, short_id      # a short placed with a long on one bar wins
        elif long_id and cur not in ("LKC", "LT"):
            le[i], held = True, long_id
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~se), S(se), S(sx & ~le)


def portfolio_kwargs(**params):
    return {}
