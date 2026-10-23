"""Three long setups on broker days (a rising stochastic RSI under 55 after two closes above the EMA 20 with a rising volume-weighted MACD histogram; a sharp stochastic RSI hook between 35 and 80; or the EMA 20 of the low 5 % above a rising SMA 10 with the histogram rising) go long; two closes in a row under the EMA 20 of the low, or a close under 99 % of the SMA 10, close; long only.
Port of FMZ strategy #432808 "VRSI-EMA交叉与VMACD融合的波浪寻找者策略VSTOCHASTIC-RSI-EMA-CROSSOVER-COMBINED-WITH-VMACD-WAVEFINDER-STRATEGY" (Wavefinder+).

FMZ source id: 432808

Source
    https://www.fmz.com/strategy/432808 (PineScript v3, FMZ last modified 2023-11-21 17:12:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 171-215), VWMACD 12 / 26 / 9; stochastic RSI 14 / 14 / 3 / 3; EMA 20 of the low; EMA 20, SMA 10; confirmBars 2
    dm = (ema(v c, 12) / ema(v, 12) - ema(v c, 26) / ema(v, 26)) - signal 9;  k = sma(stoch(rsi(close, 14), 14), 3), d = sma(k, 3)
    (lcount > 1 and change(k) > 3 and k > d and k < 55 and rising(dm, 1)) or (k[1] - k[2] < -2 and k - k[1] > 5 and 35 < k < 80) or (ma - sma > 0.05 sma and rising(sma, 3) and rising(dm, 2)) -> entry Long
    bcount == 2 -> close Long;  close < 0.99 sma -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * lcount / bcount count consecutive closes above the EMA 20 / under the EMA 20 of the low; the close
      fires on the bar the second one completes (bcount == 2, not >= 2), as written. ta.rising(x, n) is
      read as above every one of the previous n values (as earlier ports). The k1 / d1 / delta lines feed
      nothing. A close acts only on a position the bar's entries leave unchanged (call order): from flat an
      entry on a close bar still opens. Long only. qty = 10000 / close is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic RSI and volume-weighted MACD long setups.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 10000 / close, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume-weighted MACD histogram dm; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432808_stoch_rsi_vwmacd_wavefinder_long"
FAMILY = "stochastic_rsi"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "confirm_bars": [2, 3],
}
DEFAULT_PARAMS = {"length": 20, "confirm_bars": 2, "vw_slow": 12, "vw_fast": 26, "signal": 9,
                  "rsi_len": 14, "stoch_len": 14, "smooth_k": 3, "smooth_d": 3}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


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


def _run_count(cond):
    out = np.zeros(len(cond), dtype=int)
    n = 0
    for i, x in enumerate(cond):
        n = n + 1 if x else 0
        out[i] = n
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c, v = bars_df["low"], bars_df["close"], bars_df["volume"]

    def vw(n):
        ev = _ema(v, n)
        return _ema(v * c, n) / ev.where(ev != 0)

    da = vw(int(p["vw_slow"])) - vw(int(p["vw_fast"]))
    dm = da - _ema(da, int(p["signal"]))
    r = _rsi(c, int(p["rsi_len"]))
    ns = int(p["stoch_len"])
    rl, rh = r.rolling(ns).min(), r.rolling(ns).max()
    k = (100 * (r - rl) / (rh - rl).where(rh != rl)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    n = int(p["length"])
    ma = _ema(lo, n)
    e20 = _ema(c, 20)
    sma = c.rolling(10).mean()
    bcount = _run_count((c < ma).to_numpy())
    lcount = _run_count((c > e20).to_numpy())
    k1, k2 = k.shift(1), k.shift(2)
    s1 = (pd.Series(lcount > 1, index=c.index) & (k - k1 > 3) & (k > d) & (k < 55) & (dm > dm.shift(1)))
    s2 = (k1 - k2 < -2) & (k - k1 > 5) & (k > 35) & (k < 80)
    s3 = (ma - sma > 0.05 * sma) & (sma > sma.shift(1)) & (sma > sma.shift(2)) & (sma > sma.shift(3)) \
        & (dm > dm.shift(1)) & (dm > dm.shift(2))
    ent = (s1 | s2 | s3).to_numpy()
    ext = ((bcount == int(p["confirm_bars"])) | (c < 0.99 * sma).to_numpy())
    m = len(ent)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            le[i], pos = True, 1
        elif pos == 1 and ext[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
