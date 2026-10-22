"""HARSI, SSL channel and Coral trend flips together, 1-hour bars: a Heikin-Ashi RSI candle turning green within 6 bars, an SSL cross up within 2 bars and a Coral trend turning up within 4 bars go long; the
mirrored three flips go short; the script alternates long and short.
Port of FMZ strategy #439760 "Multi Indicator Trend Reversal Trading Strategy" (GT 5.1 Strategy).

FMZ source id: 439760

Source
    https://www.fmz.com/strategy/439760 (PineScript v5, FMZ last modified 2024-01-23 15:33:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 165-870), HARSI on (lookback 6, RSI 14, open smoothing 7); SSL on (lookback 1, period 10); CORAL on (lookback 4, smoothing 9, constant 0.4); MACD DEMA and WAVE TREND off
    HARSI: RSI-50 Heikin-Ashi candles (open = smoothed);  checker_11 = a green candle after a red one with a higher close in the last 6 bars;  checker_21 = a red after a green
    SSL: Hlv = close > sma(high, 10) ? 1 : close < sma(low, 10) ? -1 : previous;  checker_31 / 41 = an SSL up / down cross on this or the previous bar
    CORAL: six chained smoothers into bfr;  checker_51 / 61 = a colour flip green / red in the last 4 bars;  (buy == false and sell == true): all three buy checks -> entry long;  (buy and not sell): all three sell checks -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the three default options on, only the HARSI + SSL + CORAL branch can fire. The buy / sell
      flags start as "sell" and alternate, so the first trade is a long and then each side waits for the
      other; when a long entry and the short tests both pass on one bar the later short wins (as
      #437773). The HARSI open uses the simple mean until 7 bars of open values exist, as written.
      strategy.entry reverses: REVERSAL INTENDED. The cash quantity is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI candles, SSL channel and Coral trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash quantity stored.
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

NAME = "fmz_439760_gt51_harsi_ssl_coral_flips"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "harsi_back": [6, 3],
    "coral_back": [4, 2],
}
DEFAULT_PARAMS = {"harsi_back": 6, "coral_back": 4, "ssl_back": 1, "len_harsi": 14, "smoothing": 7,
                  "ssl_len": 10, "sm": 9.0, "cd": 0.4}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _any_back(f, k):
    """True when f(j) holds for some j in 0 .. k - 1 (f builds the test shifted j bars back)."""
    out = pd.Series(False, index=f(0).index)
    for j in range(k):
        out |= f(j).fillna(False).astype(bool)
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ix = bars_df.index
    n = int(p["len_harsi"])
    cr = _rsi(c, n) - 50
    hr, lr = _rsi(h, n) - 50, _rsi(lo, n) - 50
    orsi = cr.shift(1).where(cr.shift(1).notna(), cr)
    hh, ll = np.fmax(hr, lr), np.fmin(hr, lr)
    hc = ((orsi + hh + ll + cr) / 4).to_numpy()
    ov, cv0 = orsi.to_numpy(), cr.to_numpy()
    sm = int(p["smoothing"])
    m = len(c)
    ho = np.full(m, np.nan)
    for i in range(m):
        if i < sm or np.isnan(ho[i - sm]):
            ho[i] = (ov[i] + cv0[i]) / 2
        else:
            ho[i] = (ho[i - 1] * sm + hc[i - 1]) / (sm + 1)
    C, O = pd.Series(hc, index=ix), pd.Series(ho, index=ix)
    hb = int(p["harsi_back"])
    h_up = _any_back(lambda j: (C.shift(j) > O.shift(j)) & (C.shift(j + 1) < O.shift(j + 1)) & (C.shift(j) > C.shift(j + 1)), hb)
    h_dn = _any_back(lambda j: (C.shift(j) < O.shift(j)) & (C.shift(j + 1) > O.shift(j + 1)), hb)
    k = int(p["ssl_len"])
    sh, sl = h.rolling(k).mean().to_numpy(), lo.rolling(k).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    hlv = np.full(m, np.nan)
    for i in range(m):
        prev = hlv[i - 1] if i > 0 else np.nan
        hlv[i] = 1 if cv[i] > sh[i] else (-1 if cv[i] < sl[i] else prev)
    neg = hlv < 0
    s_dn = pd.Series(np.where(neg, sh, sl), index=ix)
    s_up = pd.Series(np.where(neg, sl, sh), index=ix)
    sb = int(p["ssl_back"]) + 1
    ssl_up = _any_back(lambda j: (s_up.shift(j) > s_dn.shift(j)) & (s_up.shift(j + 1) < s_dn.shift(j + 1)), sb)
    ssl_dn = _any_back(lambda j: (s_up.shift(j) < s_dn.shift(j)) & (s_up.shift(j + 1) > s_dn.shift(j + 1)), sb)
    di = float(p["sm"]) / 2.0 + 1.0
    c1 = 2 / (di + 1.0)
    c2 = 1 - c1
    cd = float(p["cd"])
    c3 = 3.0 * (cd * cd + cd * cd * cd)
    c4 = -3.0 * (2.0 * cd * cd + cd + cd * cd * cd)
    c5 = 3.0 * cd + 1.0 + cd * cd * cd + 3.0 * cd * cd
    st = np.zeros(6)
    bfr = np.full(m, np.nan)
    for i in range(m):
        x = cv[i]
        for q in range(6):
            st[q] = c1 * x + c2 * st[q]
            x = st[q]
        bfr[i] = -cd * cd * cd * st[5] + c3 * st[4] + c4 * st[3] + c5 * st[2]
    bp = np.concatenate(([0.0], bfr[:-1]))
    col = pd.Series(np.where(bfr > bp, 1, np.where(bfr < bp, -1, 0)), index=ix)
    cb = int(p["coral_back"])
    co_up = _any_back(lambda j: (col.shift(j) == 1) & (col.shift(j + 1) == -1), cb)
    co_dn = _any_back(lambda j: (col.shift(j) == -1) & (col.shift(j + 1) == 1), cb)
    buy = (h_up & ssl_up & co_up).to_numpy()
    sell = (h_dn & ssl_dn & co_dn).to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    side, pos = -1, 0
    for i in range(m):
        if side == -1 and buy[i]:
            side, pos = 1, 1
        if side == 1 and sell[i]:
            side, pos = -1, -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
