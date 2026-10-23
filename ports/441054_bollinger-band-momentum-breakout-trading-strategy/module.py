"""Hourly bars: buying volume (volume x the close's place in the range) above selling volume and above the 50-bar average volume, with the close above the 1 and 1.5 sd Bollinger lines, the high above the 2 sd band and RSI 14 under 80, goes long; the long closes at +2 %, on a 5 % loss, or in profit on several pullback tests; the low under the SMA 20 and the 1 sd lower line with the close under the 1.5 sd line on an SMA 60 / 120 cross-down goes short, closed at +2 % or RSI under 20; reversing.
Port of FMZ strategy #441054 "Bollinger Band Momentum Breakout Trading Strategy" (prototype (KAIST291)).

FMZ source id: 441054

Source
    https://www.fmz.com/strategy/441054 (PineScript v4, FMZ last modified 2024-02-05 10:53:46).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 153-241), SMA 1 .. 120; RSI 14; Bollinger 20 with 1 / 1.5 / 2 / 2.5 sd; daily-volume SMA 50
    bull = BV > SV and BV > sma(volume, 50);  bull and close > upper1 and close > Supper and high > upper and rsi < 80 -> entry Long
    close Long when avg x 1.02 < close, or low < ma9 / ma20 > close / rsi > 80 / high < upper while in profit, or openprofit < avg x 0.9 - close;  entry Short when low < ma20 and low < lower1 and close < Slower and crossunder(ma60, ma120);  close Short when close < avg x 0.98 or rsi < 20

Interpretation choices (Pine rules in SURVEY_README.md)
    * openprofit with the default 1-unit order is close - avg, so "openprofit < avg x 0.9 - close" is
      close < 0.95 x avg: a 5 % close-based stop (weird case: a cash amount compared with a price). The
      average price is the fill. All closes are bar-close tests (next open). A close acts only on a
      position the bar's entries leave unchanged. The weekly-volume SMA and 'con' feed nothing. Pine's
      stdev is the population deviation. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based exits in the signals.
    2 generic: PASS, buying-volume Bollinger breakouts with profit-protecting exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) split into buying / selling volume by the close's place in the range and compared with its SMA 50; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441054_buying_volume_bollinger_breakout_profit_exits_1h_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "daily_len": [50, 20],
}
DEFAULT_PARAMS = {"length": 20, "daily_len": 50}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    rng = h - lo
    bv = (v * (c - lo) / rng.where(rng != 0)).where(rng != 0, 0.0)
    sv = (v * (h - c) / rng.where(rng != 0)).where(rng != 0, 0.0)
    davg = v.rolling(int(p["daily_len"])).mean()
    n = int(p["length"])
    basis = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    upper, upper1, s_up = basis + 2 * sd, basis + sd, basis + 1.5 * sd
    lower1, s_lo = basis - sd, basis - 1.5 * sd
    ma9, ma20 = c.rolling(9).mean(), c.rolling(20).mean()
    ma60, ma120 = c.rolling(60).mean(), c.rolling(120).mean()
    rsi = _rsi(c, 14)
    lg = ((bv > sv) & (bv > davg) & (c > upper1) & (c > s_up) & (h > upper) & (rsi < 80)).to_numpy()
    sh = ((lo < ma20) & (lo < lower1) & (c < s_lo) & (ma60 < ma120) & (ma60.shift(1) >= ma120.shift(1))).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    ma9v, ma20v, rsv, upv = ma9.to_numpy(), ma20.to_numpy(), rsi.to_numpy(), upper.to_numpy()
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, px = 0, np.nan
    for i in range(m):
        if i > 0 and (le[i - 1] or se[i - 1]):
            px = ov[i]                                   # the fill = the average price
        held = tgt
        new = tgt
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if new == held:
            if held == 1:
                inp = px < cv[i]
                if (px * 1.02 < cv[i] or (lv[i] < ma9v[i] and inp) or (ma20v[i] > cv[i] and inp)
                        or (rsv[i] > 80 and inp) or cv[i] < 0.95 * px or (hv[i] < upv[i] and inp)):
                    new = 0
            elif held == -1:
                if cv[i] < px * 0.98 or rsv[i] < 20:
                    new = 0
        if new != tgt and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif tgt == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
