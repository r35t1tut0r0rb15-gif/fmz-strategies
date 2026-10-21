"""SSL Hybrid baseline channel breaks with an ATR bracket, 1-hour bars: a close above the EMA 30 plus 0.2 x the EMA 30 of the true range goes long, a close under the EMA minus it goes short (reversing); each trade
has a stop 4 ATR 14 from the signal close and a target twice as far; a new same-side entry waits until the script's own flags see the bracket hit.
Port of FMZ strategy #438805 "基于SSL的均线趋势跟随策略Trend-Following-Strategy-Based-on-SSL-Baseline" ([f] SSL).

FMZ source id: 438805

Source
    https://www.fmz.com/strategy/438805 (PineScript v5, FMZ last modified 2024-01-15 14:36:39).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 174-480), baseline EMA 30, channel 0.2 (true range on); SL type ATR (14 x 4); risk:reward 2; risk 1 % (sizing); date range true
    upperk = ema(close, 30) + ema(tr, 30) x 0.2;  lowerk = the minus side;  goLong = close > upperk;  goShort = close < lowerk;  openLong = goLong and not inLong -> entry Long (inLong := true, inShort := false)
    slPercent = 4 atr(14) / close;  levels from the signal close;  exit(profit = 2 x, loss = 1 x, in ticks of those percents);  inLong / inShort reset when the bar's high / low reaches the script's levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent in ticks of percents of the signal close (correct price math), fixed from the
      fill: sl_stop = 4 x ATR(14) / close of the signal bar (shifted one bar inside stops()) and tp_stop
      twice that. The entry flags follow the script: they are cleared on a bar whose high or low reaches
      the stop / target levels measured from the signal close (the test uses the flags of the bar's
      start), so a new same-side entry waits for that. The baseline types other than EMA are not swept.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The risk
      quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, baseline channel and ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438805_ssl_baseline_channel_atr_bracket"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [30, 60],
    "sl_mult": [4.0, 2.0],
}
DEFAULT_PARAMS = {"length": 30, "sl_mult": 4.0, "multy": 0.2, "atr_len": 14, "rr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _frac(bars_df, p):
    return float(p["sl_mult"]) * _rma(_tr(bars_df), int(p["atr_len"])) / bars_df["close"]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    kma = c.ewm(span=n, adjust=False).mean()
    rng = _tr(bars_df).ewm(span=n, adjust=False).mean()
    upper = (kma + rng * float(p["multy"])).to_numpy()
    lower = (kma - rng * float(p["multy"])).to_numpy()
    f = _frac(bars_df, p).to_numpy()
    rr = float(p["rr"])
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_l = in_s = False
    slp = tpp = np.nan
    for i in range(m):
        go_l, go_s = cv[i] > upper[i], cv[i] < lower[i]
        in_trade = in_l or in_s
        open_l = go_l and not in_l
        open_s = go_s and not in_s
        if open_l and i + 1 < m:
            le[i], in_l, in_s = True, True, False
        if open_s and i + 1 < m:
            se[i], in_s, in_l = True, True, False
        if (open_l or open_s) and not np.isnan(f[i]):
            off = f[i] * cv[i]
            slp = cv[i] - off if open_l else cv[i] + off
            tpp = cv[i] + rr * off if open_l else cv[i] - rr * off
        sl_hit = (in_s and hv[i] >= slp) or (in_l and lv[i] <= slp)
        tp_hit = (in_l and hv[i] >= tpp) or (in_s and lv[i] <= tpp)
        if in_trade and (sl_hit or tp_hit):
            in_l = in_s = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = _frac(bars_df, p)
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["rr"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
