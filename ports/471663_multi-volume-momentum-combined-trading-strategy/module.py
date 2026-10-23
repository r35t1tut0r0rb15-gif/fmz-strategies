"""Broker days, long only: when more than 4 of 7 volume readings are bullish (OBV up, A/D up, CMF 20 > 0, a 14-bar MFI < 40, close under the daily VWAP, volume SMA 5 over SMA 10, RSI 14 of volume < 40) it goes long; more than 4 bearish readings close the long.
Port of FMZ strategy #471663 "Multi Volume Momentum Combined Trading Strategy" (Combined Volume Indicators Strategy).

FMZ source id: 471663

Source
    https://www.fmz.com/strategy/471663 (PineScript v5, FMZ last modified 2024-11-12 10:52:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 109-193), OBV; manual A/D; CMF 20; manual MFI 14; daily VWAP; volume SMA 5 / 10; RSI 14 of volume; count > 4
    buySignals = (obv > obv[1]) + (ad > ad[1]) + (cmf > 0) + (mfi < 40) + (close < vwap) + (volumeOscillator > 0) + (vrsi < 40);  buySignals > 4 -> entry Buy
    sellSignals = the mirrored seven (mfi > 60, close > vwap, vrsi > 60);  sellSignals > 4 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the header's daily bars ta.vwap(close) is the bar's own close (one bar per session), so the VWAP
      item is never true for either side and the entry needs 5 of the 6 others (weird case). The A/D line
      starts at 0 and restarts at 0 on the bar after a bar with high = low (its division by zero is na).
      The MFI sums the 14 typical-price money flows of up / down closes; its division by zero is na. The
      buy and sell items are exclusive pairs, so both counts can never exceed 4 together. An entry while
      long adds nothing. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a vote of seven volume indicators.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) in OBV, A/D, CMF, MFI, the volume oscillator and the volume RSI; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471663_seven_volume_indicator_vote_long_only"
FAMILY = "volume_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "need": [4, 3],
    "cmf_len": [20, 40],
}
DEFAULT_PARAMS = {"need": 4, "cmf_len": 20, "mfi_len": 14, "rsi_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    pc = c.shift(1)
    obv = (v.where(c > pc, 0.0) - v.where(c < pc, 0.0)).cumsum()
    mfm = ((c - lo) - (h - c)) / (h - lo).where(h != lo)          # division by zero is na
    step = (mfm * v).to_numpy(dtype=float)
    ad = np.full(len(c), np.nan)
    for i in range(len(c)):
        ad[i] = 0.0 if i == 0 or np.isnan(ad[i - 1]) else ad[i - 1] + step[i]
    ad = pd.Series(ad, index=c.index)
    nc = int(p["cmf_len"])
    cmf = (mfm * v).rolling(nc).mean() / v.rolling(nc).mean()
    mf = (h + lo + c) / 3 * v
    nm = int(p["mfi_len"])
    pos_f = mf.where(c > pc, 0.0).rolling(nm, min_periods=1).sum()   # the loop adds 0 where close[i + 1] is na
    neg_f = mf.where(c < pc, 0.0).rolling(nm, min_periods=1).sum()
    mfi = 100 - 100 / (1 + pos_f / neg_f.where(neg_f != 0))
    vo = v.rolling(5).mean() - v.rolling(10).mean()
    vr = _rsi(v, int(p["rsi_len"]))
    zero = pd.Series(0, index=c.index)
    buy_n = ((obv > obv.shift(1)).astype(int) + (ad > ad.shift(1)).astype(int) + (cmf > 0).astype(int)
             + (mfi < 40).astype(int) + zero + (vo > 0).astype(int) + (vr < 40).astype(int))
    sell_n = ((obv < obv.shift(1)).astype(int) + (ad < ad.shift(1)).astype(int) + (cmf < 0).astype(int)
              + (mfi > 60).astype(int) + zero + (vo < 0).astype(int) + (vr > 60).astype(int))
    need = int(p["need"])                 # zero: close vs the daily VWAP (= the close) never counts
    entry = buy_n > need
    ex = sell_n > need
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), ex.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
