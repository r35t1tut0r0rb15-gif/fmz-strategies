"""Band-extreme fades against the EMA 50 / 200 trend with RSI 14, ADX 14 under 35 and ATR over half its SMA, inside 09:20-15:15 UTC, hourly bars: a close at or over the upper Bollinger 20 / 1.8 band with RSI over 65 in a downtrend goes short, the mirror at the lower band with RSI under 35 in an uptrend goes long; reversing (the per-bar ATR bracket is pending).
Port of FMZ strategy #484098 "Multi Indicator Trend Reversal Volatility Conditional Selective Options Selling Strategy" (Nifty BankNifty Option Selling Strategy).

FMZ source id: 484098

Source
    https://www.fmz.com/strategy/484098 (PineScript v5, FMZ last modified 2025-02-28 10:04:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-242), EMA 50 / 200; DMI 14 / 14, ADX under 35; Bollinger 20 x 1.8; RSI 14 / 65 / 35; ATR 14 over 0.5 x SMA 10; hours 09:20-15:15; SuperTrend (unused)
    ema50 < ema200 and rsi > 65 and close >= upper and adx <= 35 and atr > 0.5 sma(atr, 10) and in hours -> entry Sell Call (short)
    ema50 > ema200 and rsi < 35 and close <= lower and the same filters -> entry Sell Put (long)
    every bar: exit Short (stop = close + 2 atr, limit = close - 3.5 atr);  exit Long (stop = close - 2 atr, limit = close + 3.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * timestamp(year, month, day, 9, 20) reads the chart exchange's zone, UTC for the header's Binance
      pair (the title's Indian session is not applied): bars opening 09:20-15:15 UTC qualify (fixed UTC,
      no DST). ta.dmi is Wilder's DMI; the SuperTrend feeds nothing.
    * The bracket is re-sent on every bar from that bar's close, so its levels follow the price: not
      ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite entry is the exit. An
      entry on the other side reverses (REVERSAL INTENDED). The 100 % of equity size is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent close bracket pending.
    2 generic: PASS, Bollinger / RSI extremes against the EMA trend with ADX / ATR filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: clock window 09:20-15:15 UTC on the bar's open time (fixed UTC, no DST; the header exchange's time zone).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484098_bb_rsi_extreme_fade_against_ema_trend_adx_atr_utc_window_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
SESSION_TZ = "UTC"  # timestamp() reads the chart exchange's zone: UTC for the header's Binance pair

GRID = {
    "bb_mult": [1.8, 2.5],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"bb_mult": 1.8, "rsi_length": 14, "dmi_length": 14, "adx_max": 35.0, "start_minute": 560,
                  "end_minute": 915}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    n = int(p["dmi_length"])
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    trs = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / trs, 100 * _rma(mdm, n) / trs
    ssum = pdi + mdi
    adx = _rma(100 * (pdi - mdi).abs() / ssum.where(ssum > 0), n)
    basis, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    k = float(p["bb_mult"])
    bu, bl = basis + k * sd, basis - k * sd
    r = _rsi(c, int(p["rsi_length"]))
    atr = _rma(tr, 14)
    loc = bars_df.index.tz_convert(SESSION_TZ)
    mod = np.asarray(loc.hour * 60 + loc.minute)
    t_ok = pd.Series((mod >= int(p["start_minute"])) & (mod <= int(p["end_minute"])), index=c.index)
    calm = ~(adx > float(p["adx_max"])) & (atr > atr.rolling(10).mean() * 0.5) & t_ok
    se = (e50 < e200) & (r > 65) & (c >= bu) & calm
    le = (e50 > e200) & (r < 35) & (c <= bl) & calm
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
