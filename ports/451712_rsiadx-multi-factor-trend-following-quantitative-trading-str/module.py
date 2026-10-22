"""SMA 14 / 28 crossings with ADX, RSI and cloud filters, daily bars: a cross up with ADX 14 over 20, the RSI 14 not under its SMA 14 and the close over the cloud top of 26 bars back goes long; the mirror goes short; reversing.
Port of FMZ strategy #451712 "基于RSIADX和一目均衡图的多因子趋势跟踪量化交易策略-Multi-factor-Trend-Following-Quantitative-Trading-Strategy-Based-on-RSI-ADX-and-Ichimoku-Cloud" (Stratejim RSI, ADX ve Ichimoku ile).

FMZ source id: 451712

Source
    https://www.fmz.com/strategy/451712 (PineScript v5, FMZ last modified 2024-05-17 13:37:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-123), SMA 14 / 28; DMI 14 / 14, ADX > 20; RSI 14 vs its SMA 14; Tenkan 9, Kijun 26, Span B 52 (SMA of hl2); valuewhen(bar_index, ..., 26)
    crossover(sma14, sma28) and adx > 20 and not (rsi < sma(rsi, 14)) and close > valuewhen(bar_index, max(spanA, spanB), 26) -> entry My Long Entry Id
    crossunder(sma14, sma28) and adx > 20 and not (rsi > sma(rsi, 14)) and close < valuewhen(bar_index, min(spanA, spanB), 26) -> entry My Short Entry Id

Interpretation choices (Pine rules in SURVEY_README.md)
    * valuewhen with bar_index as the condition counts every bar but the first (bar_index 0 is
      false), so it returns the cloud edge 26 bars back (one bar further only for the earliest bars,
      which are na anyway). ta.dmi is Wilder's (rma) DMI / ADX. There is no exit: positions end at the
      opposite entry. REVERSAL INTENDED. The margin settings are sizing. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with ADX, RSI and cloud filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
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

NAME = "fmz_451712_sma14_28_cross_adx_rsi_cloud_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 10],
    "slow": [28, 50],
    "adx_min": [20, 25],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28, "adx_min": 20.0, "dmi_len": 14, "rsi_len": 14,
                  "tenkan": 9, "kijun": 26, "span_b": 52, "disp": 26}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
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
    k = int(p["dmi_len"])
    atr = _rma(tr, k)
    dip, dim = 100 * _rma(pdm, k) / atr, 100 * _rma(mdm, k) / atr
    s = dip + dim
    adx = 100 * _rma((dip - dim).abs() / s.where(s != 0, 1.0), k)
    strong = adx > float(p["adx_min"])
    r = _rsi(c, int(p["rsi_len"]))
    rs = r.rolling(int(p["rsi_len"])).mean()
    hl2 = (h + lo) / 2
    tenkan = hl2.rolling(int(p["tenkan"])).mean()
    kijun = hl2.rolling(int(p["kijun"])).mean()
    span_a, span_b = (tenkan + kijun) / 2, hl2.rolling(int(p["span_b"])).mean()
    d = int(p["disp"])
    top, bot = np.maximum(span_a, span_b).shift(d), np.minimum(span_a, span_b).shift(d)
    f, sl = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up_x = (f > sl) & (f.shift(1) <= sl.shift(1))
    dn_x = (f < sl) & (f.shift(1) >= sl.shift(1))
    le = up_x & strong & ~(r < rs) & (c > top)
    se = dn_x & strong & ~(r > rs) & (c < bot)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
