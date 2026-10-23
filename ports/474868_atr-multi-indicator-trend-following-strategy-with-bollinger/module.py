"""Broker days: the close crossing over the upper Bollinger band (20, 2) with ADX (17 / 14) over 25, volume over 1.5 x its 20-day average and the close above the supertrend (3, 10) goes long; the mirror under the lower band goes short; a long closes on a MACD bearish crossing or ADX under 20, a short on a MACD bullish crossing or ADX under 20; reversing.
Port of FMZ strategy #474868 "多指标趋势追踪策略结合布林带和-ATR-动态止损-Multi-Indicator-Trend-Following-Strategy-with-Bollinger-Bands-and-ATR-Dynamic-Stop-Loss" (Nifty Options Trendy Markets with TSL).

FMZ source id: 474868

Source
    https://www.fmz.com/strategy/474868 (PineScript v5, FMZ last modified 2024-12-12 16:08:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-157), BB 20 x 2; supertrend 3 / 10; DMI 17 / 14, ADX 25 entry / 20 exit; MACD 12 / 26 / 9; volume SMA 20 x 1.5; ATR 14 x 1.5 "trailing stop"
    longEntry = crossover(close, upperBB) and adx > 25 and volumeSpike and close > supertrend -> entry Long;  shortEntry mirrored
    longExit = crossunder(macd, signal) or close < close - 1.5 atr or adx < 20 -> close Long;  shortExit = crossover(macd, signal) or close > close + 1.5 atr or adx < 20 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trailing stop" tests compare the close with itself minus / plus 1.5 ATR, so they can never be
      true (weird case): the exits are the MACD crossings and ADX under 20. The closes act only on a
      position the bar's entries leave unchanged, from the bar after the fill; an opposite entry
      reverses. ta.supertrend and ta.dmi as Pine's reference implementations; Pine's stdev is the
      population deviation. The title names Nifty options; the rules are generic. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts with ADX, supertrend and volume confirmation, MACD / ADX exits.
    3 crypto-exchange-only: no (exchange pair in the header only (Nifty options named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474868_bollinger_breakout_adx_supertrend_volume_macd_exit_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_entry": [25.0, 30.0],
    "adx_exit": [20.0, 15.0],
}
DEFAULT_PARAMS = {"adx_entry": 25.0, "adx_exit": 20.0, "vol_mult": 1.5}


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


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi(h, lo, c, n, sm):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    plus, minus = _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)
    tot = plus + minus
    adx = 100 * _rma((plus - minus).abs() / tot.where(tot != 0, 1.0), sm)
    return plus, minus, adx


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    basis, dev = c.rolling(20).mean(), 2.0 * c.rolling(20).std(ddof=0)
    up_b, lo_b = basis + dev, basis - dev
    st, _ = _supertrend(bars_df, 3.0, 10)
    _, _, adx = _dmi(h, lo, c, 17, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    vol_ok = v > v.rolling(20).mean() * float(p["vol_mult"])
    strong = adx > float(p["adx_entry"])
    buy = ((c > up_b) & (c.shift(1) <= up_b.shift(1)) & strong & vol_ok & (c > st)).to_numpy()
    sell = ((c < lo_b) & (c.shift(1) >= lo_b.shift(1)) & strong & vol_ok & (c < st)).to_numpy()
    weak = adx < float(p["adx_exit"])
    ex_l = (((macd < sig) & (macd.shift(1) >= sig.shift(1))) | weak).to_numpy()
    ex_s = (((macd > sig) & (macd.shift(1) <= sig.shift(1))) | weak).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
