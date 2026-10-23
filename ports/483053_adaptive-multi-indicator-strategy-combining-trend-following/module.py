"""Hourly bars: in a trend (ADX 14 over 25) a supertrend (2, 10) up-trend with EMA 20 above EMA 50 and the close above the session VWAP goes long, the mirror goes short; out of trend a close at the lower Bollinger band (20, 2) with RSI 14 under 30 goes long, at the upper band with RSI over 70 short; a long closes on a supertrend down-turn or RSI 70, a short on an up-turn or RSI 30; a 1 % stop from position_avg_price is armed only by a signal while a trade is open, followed in the signals.
Port of FMZ strategy #483053 "Adaptive Multi Indicator Strategy Combining Trend Following and Range Trading" (Nifty/BankNifty Multi-Strategy v2).

FMZ source id: 483053

Source
    https://www.fmz.com/strategy/483053 (PineScript v5, FMZ last modified 2025-02-21 11:08:52).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-193), supertrend 2 / 10; EMA 20 / 50; DMI 14 / 14, ADX 25; RSI 14 (70 / 30); BB 20 x 2; session VWAP of hlc3; stop 1 % of position_avg_price
    longConditionTrend = adx > 25 and direction < 0 and ema20 > ema50 and close > vwap;  longConditionRange = adx <= 25 and close <= lowerBB and rsi < 30 -> entry Long, exit(stop = position_avg_price x 0.99)
    shortConditionTrend = adx > 25 and direction > 0 and ema20 <= ema50 and close < vwap;  shortConditionRange = adx <= 25 and close >= upperBB and rsi > 70 -> entry Short, exit(stop = position_avg_price x 1.01)
    direction > 0 or rsi >= 70 -> close Long;  direction < 0 or rsi <= 30 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop takes position_avg_price at the signal bar: na when the signal opens a trade from flat (no
      stop exists), the old trade's fill on a reversal bar, the trade's own fill on a repeated signal
      while it is open; the signals follow it: a bar whose low (high) reaches an armed stop closes the
      trade at the next open (mark trailing_stop_pending). The closes act only on a position the bar's
      entries leave unchanged; an opposite entry reverses. ta.vwap(hlc3) restarts each session: the house
      session is the broker day (17:00 America/New_York). The title names Nifty / BankNifty; the rules
      are generic. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; position-price stop followed in the signals.
    2 generic: PASS, trend / range regime switch by ADX with supertrend, VWAP, Bollinger and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only (Nifty named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483053_adx_regime_supertrend_vwap_bollinger_rsi_1h_reversal"
FAMILY = "regime_switch"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [25.0, 20.0],
    "st_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"adx_min": 25.0, "st_mult": 2.0, "atr_len": 10, "sl": 0.01}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    _, d = _supertrend(bars_df, float(p["st_mult"]), int(p["atr_len"]))
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    _, _, adx = _dmi(h, lo, c, 14, 14)
    r = _rsi(c, 14)
    basis, dev = c.rolling(20).mean(), 2.0 * c.rolling(20).std(ddof=0)
    day = broker_day(bars_df.index)
    src = (h + lo + c) / 3
    vw = (src * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    trend = adx > float(p["adx_min"])
    buy = ((trend & (d < 0) & (e20 > e50) & (c > vw)) | (~trend & (c <= basis - dev) & (r < 30))).to_numpy()
    sell = ((trend & (d > 0) & ~(e20 > e50) & (c < vw)) | (~trend & (c >= basis + dev) & (r > 70))).to_numpy()
    ex_l, ex_s = ((d > 0) | (r >= 70)).to_numpy(), ((d < 0) | (r <= 30)).to_numpy()
    on, hn, ln = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl = float(p["sl"])
    m = len(on)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine, fp, pend, stop = 0, 0, np.nan, False, np.nan
    for i in range(m):
        held = pine
        if pend:
            fp, pend = on[i], False
        if (held == 1 and ln[i] <= stop) or (held == -1 and hn[i] >= stop):
            held, stop, fp = 0, np.nan, np.nan
        new, sent = held, np.nan
        if buy[i]:
            new = 1
            sent = fp * (1 - sl) if held != 0 else np.nan
        if sell[i]:
            new = -1
            sent = fp * (1 + sl) if held != 0 else np.nan
        if new == held:
            if held == 1 and ex_l[i]:
                new = 0
            elif held == -1 and ex_s[i]:
                new = 0
        if new != held:
            stop, pend = (sent if new != 0 else np.nan), new != 0
        elif not np.isnan(sent):
            stop = sent
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
