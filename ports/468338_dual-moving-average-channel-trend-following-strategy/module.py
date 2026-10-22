"""SMA 55 crossings of the EMA 576 and the SMA 300 with a small offset, 1-hour bars: the SMA 55 (plus the offset) crossing over either line goes long, the SMA 55 (minus it) crossing under either goes short; a long closes on a close 1/70 of the reference close under its fill or 1/140 over it, a short on the mirror; reversing.
Port of FMZ strategy #468338 "Dual Moving Average Channel Trend Following Strategy" (RC BTC Vegas 5min free).

FMZ source id: 468338

Source
    https://www.fmz.com/strategy/468338 (PineScript v5, FMZ last modified 2024-09-26 16:28:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-216), SMA 55 / 300, EMA 576 (EMA 676 unused); offsets +-5 (price units); reference close set on EMA-576 crosses; stop ref / 70, target ref / 140 against the average price (close tests); trailing exits armed 150 points away; qty 1
    crossover(sma55 + 5, ema576) or crossover(sma55 + 5, sma300) -> entry Buy;  long and (close <= avg - ref / 70 or close >= avg + ref / 140) -> close Buy
    crossunder(sma55 - 5, ema576) or crossunder(sma55 - 5, sma300) -> entry Sell;  short and the mirror tests -> close Sell
    close - ref >= 150 -> exit(Buy, trail_price = close + 5, trail_offset = 5);  close - ref <= -150 -> exit(Sell, trail_price = close - 5, trail_offset = 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The +-5 offsets and the 150-point arming distance are price amounts, ported as fractions of 42000
      of the close (0.000119 / 0.00357). The reference close is re-set on each EMA-576 cross (not on the
      SMA-300 crosses), as written, and the stop / target distances are ref / 70 and ref / 140; the
      tests are bar-close tests against the fill price, filled at the next open, followed in a loop in
      the written call order (a close gives way to a reversal on the same bar, #437773). The trailing
      exits are armed only by the 150-point move and then trail from a moving price: not ported
      (pending, mark trailing_stop_pending). The 1-unit quantity is not ported. The title names 5-minute
      bars; the header's 1-hour bars are followed. REVERSAL INTENDED. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop and target are close tests against the fill.
    2 generic: PASS, MA crossings with reference-close exits; armed trails described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only (BTC named in the title)).
    4 signals only: the fixed 1-unit quantity stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_468338_vegas_sma55_cross_ema576_sma300_ref_close_tests_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [55, 34],
    "long_len": [300, 200],
    "ema_len": [576, 288],
}
DEFAULT_PARAMS = {"short_len": 55, "long_len": 300, "ema_len": 576, "offset_frac": 0.000119,
                  "sl_div": 70.0, "tp_div": 140.0}


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


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    s, l = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    off = float(p["offset_frac"]) * c
    up, dn = s + off, s - off
    el, el2 = _xo(up, e), _xo(up, l)
    xl, xl2 = _xo(e, dn), _xo(l, dn)
    buy, sell = (el | el2).to_numpy(), (xl | xl2).to_numpy()
    reset = (el | xl).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sd, td = float(p["sl_div"]), float(p["tp_div"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, avg, ref = 0, 0, np.nan, np.nan
    for i in range(m):
        if nxt != pos:
            pos, avg = nxt, (ov[i] if nxt != 0 else np.nan)
        if reset[i]:
            ref = cv[i]
        slp, tpp = ref / sd, ref / td
        cur = pos
        if buy[i]:
            cur = 1
        if pos == 1 and cur == 1 and (cv[i] <= avg - slp or cv[i] >= avg + tpp):
            cur = 0                              # the close acts only on a long held, not reversed
        if sell[i]:
            cur = -1
        if pos == -1 and cur == -1 and (cv[i] >= avg + slp or cv[i] <= avg - tpp):
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        nxt = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
