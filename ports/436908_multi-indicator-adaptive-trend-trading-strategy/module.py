"""Trend-regime score system, broker days, long only (the defaults): with the EMA 300 rising, a long needs the RMA 7 above the HMA 54, the stochastic RSI under 61 and the WaveTrend under 82; with it falling, the
first two; the long closes on the mirror sell score only above a minimum profit (3.6 % / 1 %), at an 11.5 % close-based target (rising regime) or at a 7.5 % / 7.4 % close-based stop.
Port of FMZ strategy #436908 "Multi indicator Adaptive Trend Trading Strategy" (Instrument-Z).

FMZ source id: 436908

Source
    https://www.fmz.com/strategy/436908 (PineScript v5, FMZ last modified 2023-12-28 17:59:58).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 298-815), trade direction LONG, trend MA EMA 300; UT / DT: MA position RMA 7 vs HMA 54, stoch RSI 12 / 20 levels 61 / 13, WaveTrend 9 / 12 levels 82 / 15 (UT only); min profit 3.6 / 1 %, TP 11.5 % (UT), SL 7.5 / 7.4 %
    UpTrend = mat > mat[1];  BCond = (UpTrend ? UTSigB == UTReqScore : DTSigB == DTReqScore) with the enabled signals: MA position (ma1 > ma2), stoch RSI level (k < 61), WaveTrend level (wt1 < 82, uptrend only); SCond mirrors (ma1 < ma2, k > 13, wt1 > 15)
    entry inLong on BCond;  close when SCond and close > avg price x (1 + min profit) and open profit > 0;  close when close > avg x 1.115 (uptrend);  close when close < avg x (1 - 0.075 / 0.074);  trade expiry off

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default switches are ported: every signal family that is off by default (MA cross and
      histogram, stoch RSI cross / position / divergence, WaveTrend cross / position / divergence, the
      downtrend WaveTrend level, TrendTrade, trade expiry, the SHORT direction) adds 0 to both sides of its
      score test and is left out. The regime picks the uptrend or downtrend set on each bar. The target and
      stops are tested on bar closes against the position's average price (the fill price, one entry): close-
      based exits from simulate() (rule 3), kept as percents of the fill price, the script's own measure.
      hma(n) = wma(2 wma(n / 2) - wma(n), floor(sqrt(n))) as the script's own ma(). The VWMA option needs
      volume and is left out (check 8; not a default). Closes only act on an open position; an entry while
      long is ignored. The alert texts (an external bot's token) place no orders. Long only. The 90 % of
      equity size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target and stops tested on closes.
    2 generic: PASS, score of dimensionless tests; percent exits from the fill price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436908_instrument_z_regime_score_long"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mat_length": [300, 150],
    "ma2_length": [54, 30],
}
DEFAULT_PARAMS = {"mat_length": 300, "ma2_length": 54, "ma1_length": 7, "rsi_len": 12, "stoch_len": 20,
                  "srsi_buy_below": 61.0, "srsi_sell_above": 13.0, "wt_len_c": 9, "wt_len_a": 12,
                  "wt_buy_below": 82.0, "wt_sell_above": 15.0, "ut_min_prof": 0.036, "dt_min_prof": 0.01,
                  "ut_tp": 0.115, "ut_sl": 0.075, "dt_sl": 0.074}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(np.floor(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    mat = c.ewm(span=int(p["mat_length"]), adjust=False).mean()
    uptrend = (mat > mat.shift(1)).to_numpy()
    ma1 = _rma(c, int(p["ma1_length"]))
    ma2 = _hma(c, int(p["ma2_length"]))
    ma_up, ma_dn = (ma1 > ma2).to_numpy(), (ma1 < ma2).to_numpy()
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    rl, rh = r.rolling(n).min(), r.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (r - rl) / (rh - rl).where(rh > rl)
    rk = st.rolling(3).mean()
    s_up = (rk < float(p["srsi_buy_below"])).to_numpy()
    s_dn = (rk > float(p["srsi_sell_above"])).to_numpy()
    ap = (h + lo + c) / 3
    esa = ap.ewm(span=int(p["wt_len_c"]), adjust=False).mean()
    d1 = (ap - esa).abs().ewm(span=int(p["wt_len_c"]), adjust=False).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        ci = (ap - esa) / (0.015 * d1)
    wt1 = ci.ewm(span=int(p["wt_len_a"]), adjust=False).mean()
    w_up = (wt1 < float(p["wt_buy_below"])).to_numpy()
    w_dn = (wt1 > float(p["wt_sell_above"])).to_numpy()
    buy = np.where(uptrend, ma_up & s_up & w_up, ma_up & s_up)
    sell = np.where(uptrend, ma_dn & s_dn & w_dn, ma_dn & s_dn)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            e = ov[entry_i]
            mp = float(p["ut_min_prof"]) if uptrend[i] else float(p["dt_min_prof"])
            spl = sell[i] and cv[i] > e * (1 + mp) and cv[i] > e
            tpl = uptrend[i] and cv[i] > e * (1 + float(p["ut_tp"]))
            sl = float(p["ut_sl"]) if uptrend[i] else float(p["dt_sl"])
            sll = cv[i] < e * (1 - sl)
            if spl or tpl or sll:
                lx[i] = True
                pos = 0
                continue
        if pos == 0 and buy[i] and i + 1 < m:
            le[i] = True
            pos, entry_i = 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
