"""Multi-timeframe MACD down-ticks with RSI, ADX, stochastic and Bollinger filters, broker days: when the day's last 5- and 15-minute MACDs fall (and the 60-minute one does not rise) with RSI under 40, ADX
at least 12, %K under %D and a falling lower band, the script goes short; any close above the EMA 5 goes long; reversing.
Port of FMZ strategy #439871 "单根K线技术指标组合短期贸易策略Intraday-Single-Candle-Indicator-Combo-Short-Term-Trading-Strategy" (BankNifty_Bearish_Intraday).

FMZ source id: 439871

Source
    https://www.fmz.com/strategy/439871 (PineScript v5, FMZ last modified 2024-01-24 15:04:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 155-212), stochastic 14 / 3 / 3; MACD 12 / 26 / 9 on "5", "15", "60"; RSI 14 < 40; DMI 14 / 14, ADX >= 12; BB 20 x 2
    macd5 / macd15 / macd60 = request.security("5" / "15" / "60", macdLine);  short = macd5 < macd5[1] and macd15 < macd15[1] and macd60 <= macd60[1] and rsi < 40 and adx >= 12 and k < d and lower < lower[1]
    if short: entry Short;  if close > ema(close, 5): entry ShortSquareoff (long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A lower time frame requested from a daily chart returns its last bar inside the chart bar (as
      #436765): each MACD is computed on 5- / 15- / 60-minute bars built from the module's minutes and
      read from the broker day's last bar of that size, counted from the broker day's start; [1] is the
      previous day's value. The "square-off" order is a long entry, so it reverses the short into a
      long, as written (the intended close is owed); when both fire, the later long wins (as #437773).
      strategy.entry reverses: REVERSAL INTENDED. The margin settings are sizing. Daily bars are broker
      days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; lower-time-frame values from the day's last bar.
    2 generic: PASS, MACD slopes, RSI, ADX, stochastic and Bollinger filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439871_banknifty_mtf_macd_downtick_short"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_weak": [40, 50],
    "adx_min": [12, 20],
}
DEFAULT_PARAMS = {"rsi_weak": 40, "adx_min": 12, "stoch_len": 14, "smooth_k": 3, "smooth_d": 3}

LTF = ("5min", "15min", "60min")


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    day_lab = bars.index
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    for tf in LTF:
        b = _resample(df, tf)
        cl = b["close"]
        macd = cl.ewm(span=12, adjust=False).mean() - cl.ewm(span=26, adjust=False).mean()
        bl = broker_day(b.index)
        last = ~bl.duplicated(keep="last")                    # the broker day's last bar of that size
        v = pd.Series(macd.to_numpy()[last], index=bl[last])
        bars["macd_" + tf] = v.reindex(day_lab).to_numpy()
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


def _adx(bars_df, dilen, adxlen):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where(up.isna(), np.where((up > dn) & (up > 0), up, 0.0))
    mdm = dn.where(dn.isna(), np.where((dn > up) & (dn > 0), dn, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    trr = _rma(tr, dilen)
    with np.errstate(divide="ignore", invalid="ignore"):
        pl = 100 * _rma(pdm, dilen) / trr
        mi = 100 * _rma(mdm, dilen) / trr
    s = pl + mi
    return 100 * _rma((pl - mi).abs() / s.where(s != 0, 1.0), adxlen)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    m5, m15, m60 = (bars_df["macd_" + tf] for tf in LTF)
    md = (m5 < m5.shift(1)) & (m15 < m15.shift(1)) & (m60 <= m60.shift(1))
    weak = _rsi(c, 14) < float(p["rsi_weak"])
    strong = _adx(bars_df, 14, 14) >= float(p["adx_min"])
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    lower = c.rolling(20).mean() - 2 * c.rolling(20).std(ddof=0)
    short_ = (md & weak & strong & (k < d) & (lower < lower.shift(1))).to_numpy()
    long_ = (c > c.ewm(span=5, adjust=False).mean()).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_[i]:
            pos = 1
        elif short_[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
