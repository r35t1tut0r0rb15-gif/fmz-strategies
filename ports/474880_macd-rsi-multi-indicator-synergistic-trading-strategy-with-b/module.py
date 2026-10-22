"""Any-of-four entry signals with a max-price exit, 2-hour bars: a Bollinger 20 / 2 re-entry, a close in the bottom 23.6 % of the 50-bar range, a MACD cross up or RSI under 30 goes long; the mirrors go short (the short wins a bar with both); a long closes on a close 2 % under the stored maximum price (never reset, raised by the highs of open trades), and a short closes after one bar, as written; reversing.
Port of FMZ strategy #474880 "多指标协同布林带-斐波那契-MACD-RSI智能交易策略-Multi-Indicator-Synergistic-Trading-Strategy-with-Bollinger-Bands-Fibonacci-MACD-and-RSI" (Demo GPT Bollinger, Fibonacci, MACD & RSI with Max Profit Exit).

FMZ source id: 474880

Source
    https://www.fmz.com/strategy/474880 (PineScript v5, FMZ last modified 2024-12-12 17:20:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-233), BB 20 / 2 (SMA); Fibonacci lookback 50; MACD 12 / 26 / 9; RSI 14, 70 / 30; take profit 5 %, stop 2 % of the max price
    long = cross(close, lowerBB) up or close in [fib0, fib23.6] or crossover(macd, signal) or rsi < 30;  short mirror;  open trade: max := na(max) ? entry_price(0) : max(max, high);  close >= max x 1.05 -> exit Long (limit);  close <= max x 0.98 -> exit Long (stop);  close <= max x 1.05 -> exit Short (limit);  close >= max x 0.98 -> exit Short (stop);  then entries

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are created only when their close test holds and then sit at or through the market, so
      they are read as closes at the next open (a stop that the open gaps past would wait; stated
      approximation). The stored maximum is never reset, so it is the first trade's entry price raised
      by the highs of every later open trade; for a short one of its two tests always holds, so every
      short ends after its first bar, as written. A loop follows the position in the written order (exits,
      then entries; a reversal on the bar supersedes the exit, #437773). REVERSAL INTENDED. No sizing
      code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; conditional exit orders read as next-open closes.
    2 generic: PASS, any-of-four signals with a max-price exit.
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

NAME = "fmz_474880_bb_fib_macd_rsi_any_signal_max_price_exit_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback_fib": [50, 100],
    "sl_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"lookback_fib": 50, "sl_pct": 0.02, "tp_pct": 0.05}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    basis = c.rolling(20).mean()
    dev = 2.0 * c.rolling(20).std(ddof=0)
    up, dn = basis + dev, basis - dev
    n = int(p["lookback_fib"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    f23, f61 = ll + 0.236 * (hh - ll), ll + 0.618 * (hh - ll)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    lc = (((c > dn) & (c.shift(1) <= dn.shift(1))) | ((c <= f23) & (c >= ll))
          | ((macd > sig) & (macd.shift(1) <= sig.shift(1))) | (r < 30)).to_numpy()
    sc = (((c < up) & (c.shift(1) >= up.shift(1))) | ((c >= f61) & (c <= hh))
          | ((macd < sig) & (macd.shift(1) >= sig.shift(1))) | (r > 70)).to_numpy()
    ov, hv, cv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), c.to_numpy(dtype=float)
    kt, ks = 1 + float(p["tp_pct"]), 1 - float(p["sl_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, entry, mx = 0, 0, np.nan, np.nan
    for i in range(m):
        if nxt != pos:
            entry = ov[i] if nxt != 0 else np.nan   # the fill price of the new trade
        pos = nxt
        if pos != 0:
            mx = entry if np.isnan(mx) else max(mx, hv[i])
        tp, sl = mx * kt, mx * ks
        want_lx = pos == 1 and (cv[i] >= tp or cv[i] <= sl)
        want_sx = pos == -1 and (cv[i] <= tp or cv[i] >= sl)
        if sc[i]:
            if pos != -1:
                se[i], nxt = True, -1
        elif lc[i]:
            if pos != 1:
                le[i], nxt = True, 1
        if want_lx and nxt == 1:
            lx[i], nxt = True, 0
        if want_sx and nxt == -1:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
