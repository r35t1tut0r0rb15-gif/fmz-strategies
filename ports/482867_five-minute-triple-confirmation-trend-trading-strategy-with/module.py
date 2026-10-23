"""1-minute bars: the EMA 9 crossing over the EMA 21 on the same bar as a MACD bullish crossing with RSI 14 over 50, volume over 1.8 x its 20-bar average and a rising OBV (EMA 5 over EMA 13) goes long; the mirror goes short; a stop 1.5 ATR 14 beyond each bar's low / high and a target 3 ATR from its close, re-sent every bar, are followed in the signals; reversing.
Port of FMZ strategy #482867 "Five Minute Triple Confirmation Trend Trading Strategy with Risk Management System" (5min Triple Confirmation Crypto Strategy).

FMZ source id: 482867

Source
    https://www.fmz.com/strategy/482867 (PineScript v5, FMZ last modified 2025-02-20 15:53:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 104-166), EMA 9 / 21; RSI 14; MACD 12 / 26 / 9; volume SMA 20 x 1.8; OBV EMA 5 / 13; ATR 14; RR 2
    long_condition = crossover(ema9, ema21) and rsi > 50 and crossover(macd, signal) and volume > 1.8 x volume_ma and ema(obv, 5) > ema(obv, 13) -> entry Long  (short mirrored, not obv_trend)
    every bar: exit("Long Exit", stop = low - 1.5 atr, limit = close + 3 atr);  exit("Short Exit", stop = high + 1.5 atr, limit = close - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent every bar from that bar's low / high, close and ATR (including the signal
      bar, for the pending entry), so the levels move both ways; the house engine cannot move a bracket
      that way, so the signals follow it: a bar that reaches the previous bar's stop or target closes the
      trade at the next open (mark trailing_stop_pending). The two crossings must happen on the same bar.
      ta.obv is the cumulative signed volume. Titled 5-minute; the header is 1 minute. REVERSAL INTENDED.
      No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent bracket followed in the signals.
    2 generic: PASS, same-bar EMA and MACD crossings with RSI, volume and OBV confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only (SOL_USDT)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) against 1.8 x its SMA 20 and in the OBV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482867_triple_confirmation_ema_macd_volume_obv_rolling_bracket_1m_reversal"
FAMILY = "trend_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl_atr": [1.5, 2.5],
    "rr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"sl_atr": 1.5, "rr": 2.0, "vol_mult": 1.8}


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
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    f, s = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    spike = v > v.rolling(20).mean() * float(p["vol_mult"])
    obv = (np.sign(c.diff()) * v).fillna(0.0).cumsum()
    obv_up = obv.ewm(span=5, adjust=False).mean() > obv.ewm(span=13, adjust=False).mean()
    buy = (_xo(f, s) & (r > 50) & _xo(macd, sig) & spike & obv_up).to_numpy()
    sell = (_xo(s, f) & (r < 50) & _xo(sig, macd) & spike & ~obv_up).to_numpy()
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    d = float(p["sl_atr"]) * atr
    l_st, l_tg = (lo - d).to_numpy(dtype=float), (c + d * float(p["rr"])).to_numpy(dtype=float)
    s_st, s_tg = (h + d).to_numpy(dtype=float), (c - d * float(p["rr"])).to_numpy(dtype=float)
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine = 0, 0
    for i in range(m):
        held = pine
        if i > 0 and held == 1 and (ln[i] <= l_st[i - 1] or hn[i] >= l_tg[i - 1]):
            held = 0                       # the exit sent at the previous close is touched
        elif i > 0 and held == -1 and (hn[i] >= s_st[i - 1] or ln[i] <= s_tg[i - 1]):
            held = 0
        new = held
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
