"""Breakouts of a Nadaraya-Watson envelope with trend and momentum confirmation, 1-hour bars: the close crossing over the upper envelope with DI+ over DI-, ADX 14 over 25 and RSI 14 over 70 goes long; the mirror goes short; a close 15 % under the highest close since the signal (over the lowest, for a short) closes; reversing.
Port of FMZ strategy #452361 "Nadaraya Watson Envelope Multi Confirmation Dynamic Stop Loss Strategy" (Nadaraya-Watson Envelope with Multi-Confirmation and Dynamic Stop-Loss).

FMZ source id: 452361

Source
    https://www.fmz.com/strategy/452361 (PineScript v5, FMZ last modified 2024-05-24 17:58:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-198), Gaussian kernel bandwidth 7.2 over 101 bars; envelope 2.1 x SMA 100 of |src - estimate|, both lines SMA 10; DMI 14 / 14, ADX 25; RSI 14; stop max(0.85 x highest close, 0.90 x close)
    crossover(close, upper) and DI+ > DI- and adx > 25 and rsi > 70 -> entry Buy, highest = close;  mirror -> entry Sell
    long: highest = max(highest, close), stop = max(0.85 x highest, 0.90 x close), close < stop -> close Buy;  short: lowest, min(1.15 x lowest, 1.10 x close), close > stop -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel estimate uses only the current and past 100 closes (the endpoint form, no repaint).
      The stop is a bar-close test, followed in a loop: since 0.90 x close is always under the
      close, the long closes on the first close under 0.85 x the highest close since the last signal
      bar (the tracker restarts at the signal bar's close on every signal, also inside a trade); the
      short mirrored at 1.15 x the lowest close. The two entries cannot meet on one bar. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the close-based trailing exit in a loop.
    2 generic: PASS, kernel-envelope breakouts with DMI / RSI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452361_nadaraya_watson_breakout_dmi_rsi_trail_close_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bandwidth": [7.2, 4.0],
    "mult": [2.1, 3.0],
    "adx_min": [25, 20],
}
DEFAULT_PARAMS = {"bandwidth": 7.2, "mult": 2.1, "adx_min": 25.0, "adx_len": 14, "adx_smooth": 14,
                  "rsi_len": 14, "give": 0.85}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h - h.shift(1), lo.shift(1) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    k = int(p["adx_len"])
    atr = _rma(tr, k)
    dip, dim = 100 * _rma(pdm, k) / atr, 100 * _rma(mdm, k) / atr
    s = dip + dim
    adx = 100 * _rma((dip - dim).abs() / s.where(s != 0, 1.0), int(p["adx_smooth"]))
    bw = float(p["bandwidth"])
    w = np.exp(-(np.arange(101, dtype=float) ** 2) / (bw * bw * 2))
    est = sum(c.shift(i) * w[i] for i in range(101)) / w.sum()
    mae = (c - est).abs().rolling(100).mean() * float(p["mult"])
    upper = (est + mae).rolling(10).mean()
    lower = (est - mae).rolling(10).mean()
    r = _rsi(c, int(p["rsi_len"]))
    a = float(p["adx_min"])
    buy = ((c > upper) & (c.shift(1) <= upper.shift(1)) & (dip > dim) & (adx > a) & (r > 70)).to_numpy()
    sell = ((c < lower) & (c.shift(1) >= lower.shift(1)) & (dim > dip) & (adx > a) & (r < 30)).to_numpy()
    cv = c.to_numpy(dtype=float)
    g = float(p["give"])
    m = len(cv)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, ext = 0, 0, np.nan
    for i in range(m):
        if pend != 0:
            pos, pend = (0 if pend == 2 else pend), 0
        cur = pos
        if buy[i]:
            ext = cv[i]
            cur = 1
        if sell[i]:
            ext = cv[i]
            cur = -1
        if pos > 0:
            ext = max(ext, cv[i])
            if cv[i] < max(ext * g, cv[i] * 0.90) and cur == 1:
                lx[i], cur = True, 0
        elif pos < 0:
            ext = min(ext, cv[i])
            if cv[i] > min(ext * (2 - g), cv[i] * 1.10) and cur == -1:
                sx[i], cur = True, 0
        if cur != pos:
            pend = 2 if cur == 0 else cur
    ix = bars_df.index
    return (pd.Series(buy, index=ix), pd.Series(lx, index=ix),
            pd.Series(sell, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
