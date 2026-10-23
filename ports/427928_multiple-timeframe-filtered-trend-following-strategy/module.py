"""RSI 2 extremes on the SMA 200's side, hourly bars: RSI 2 at or under 20 above the SMA 200 goes long, at or over 80 under it goes short; RSI 2 reaching 80 closes a long, the low at or under the EMA 20 with RSI 2 at or under 10 closes a short; a 5000-tick stop (about 1.9 % on the source's BTC) from the entry; reversing.
Port of FMZ strategy #427928 "Multiple Timeframe Filtered Trend Following Strategy" (Nostradamus by Wicksell 2.0).

FMZ source id: 427928

Source
    https://www.fmz.com/strategy/427928 (PineScript v4, FMZ last modified 2023-09-26 20:36:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 225-324), RSI 2 (20 / 80, 10); SMA 200; EMA 20 / 80 (as true); TP 100000000 ticks, SL 5000 ticks, trail 1000 ticks with offset 0 (off)
    rsi(2) <= 20 and close >= sma(200) and ema(close, 20) -> entry Compra;  ema(close, 80) and rsi(2) >= 80 -> close Compra;  exit(from Venda, profit 1e8, loss 5000, trail_points 1000, trail_offset na)
    rsi(2) >= 80 and close <= sma(200) and ema(close, 80) -> entry Venda;  low <= ema(20) and rsi(2) <= 10 -> close Venda;  exit(from Compra, same)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ema(close, 20) / ema(close, 80) used as conditions are always true (a non-zero price). The two
      exits are crossed (the long block's exit names the short entry and vice versa), so both sides get
      the same ticks. The stop is 5000 ticks: on the header's BTC_USDT (tick 0.1, near 26000 in Aug-Sep
      2023) about 500 USD, a stop of 0.019 of the fill (stated approximation, as #437390). The target of
      1e8 ticks never acts; the trail has offset 0 (na), so it never trails. The many indicators and
      candle patterns below the entries only feed plots (their volume tests too), so volume does not
      reach the orders: ported as not using volume (check 8). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The 100 % of equity size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; RSI exits and a fixed-fraction stop (approximation stated).
    2 generic: PASS, RSI 2 mean reversion with an SMA 200 side filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_427928_rsi2_extremes_sma200_side_tick_stop_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.019, 0.01],
    "rsi_low": [20.0, 10.0],
}
DEFAULT_PARAMS = {"sl": 0.019, "rsi_low": 20.0, "rsi_high": 80.0, "rsi_exit_short": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    r = _rsi(c, 2)
    sma200 = c.rolling(200).mean()
    ema20 = c.ewm(span=20, adjust=False).mean()
    lc = ((r <= float(p["rsi_low"])) & (c >= sma200)).to_numpy()
    sc = ((r >= float(p["rsi_high"])) & (c <= sma200)).to_numpy()
    lxc = (r >= float(p["rsi_high"])).to_numpy()
    sxc = ((lo <= ema20) & (r <= float(p["rsi_exit_short"]))).to_numpy()
    m = len(lc)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        old = pos
        if lc[i]:
            pos = 1
        if lxc[i] and old == 1 and pos == 1:
            pos = 0
        if sc[i]:
            pos = -1
        if sxc[i] and old == -1 and pos == -1:
            pos = 0
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
