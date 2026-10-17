"""Three-line strike candles with ADX 14 above 25 and a 1 ATR stop / 2 ATR target, 1-hour bars: three red bars then a
larger green bar engulfing the previous body goes long; three green bars then a larger red bar goes short.
Port of FMZ strategy #482921 "三线突破动量趋势跟踪策略结合ADX过滤器-Three-Line-Strike-Momentum-Trend-Following-Strategy-with-ADX-Filter" (3 Line Strike [TTF] - Strategy with ATR and ADX Filter).

FMZ source id: 482921

Source
    https://www.fmz.com/strategy/482921 (PineScript v5, FMZ last modified 2025-02-20 17:46:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 111-195), ATR 14, ADX 14 > 25, 3LS on both sides
    +DM = change(high) if it exceeds change(low) and is positive; -DM = change(low) if it exceeds change(high) and is
    positive (the source's own definition); DI = rma(DM) / rma(tr(true)) x 100; adx = rma(dx, 14)
    3LS bull and adx > 25 -> entry long + exit(limit = close + 2 ATR, stop = close - 1 ATR) (bear mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is the source's own (its -DM uses the RISE of the low, not the fall), as written.
    * The bracket is fixed at the signal bar: 1 ATR / close and 2 ATR / close, shifted one bar inside stops() and
      re-based on the fill (house rule). A same-side signal while held re-places it: mark trailing_stop_pending.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, candle colours and bodies, ADX and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG482921 (2 members, best partner #483019, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482921_three_line_strike_adx_atr_bracket"
FAMILY = "candlestick"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [25.0, 20.0],
    "tp_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "adx_len": 14, "adx_threshold": 25.0, "sl_mult": 1.0, "tp_mult": 2.0}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # ta.tr(true): high - low when the previous close is na
    return tr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["adx_len"])
    ch, cl = h.diff(), lo.diff()
    pdm = ch.where((ch > cl) & (ch > 0), 0.0).where(ch.notna())
    mdm = cl.where((cl > ch) & (cl > 0), 0.0).where(cl.notna())
    str_ = _rma(_tr(bars_df), n)
    pdi, mdi = _rma(pdm, n) / str_ * 100, _rma(mdm, n) / str_ * 100
    adx = _rma((pdi - mdi).abs() / (pdi + mdi) * 100, n)
    body = c - o
    col = np.sign(body)
    larger = body.abs() > body.shift(1).abs()
    bull = larger & (col > 0) & (col.shift(1) < 0) & (col.shift(1) < 0) & (col.shift(2) < 0) & (col.shift(3) < 0)
    bear = larger & (col < 0) & (col.shift(1) > 0) & (col.shift(2) > 0) & (col.shift(3) > 0)
    strong = adx > p["adx_threshold"]
    long_e = (bull & strong).astype(bool)
    short_e = (bear & strong).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def _atr(bars_df, n):
    return _rma(_tr(bars_df), n)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
