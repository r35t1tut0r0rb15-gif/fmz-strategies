# tv_indicators

Reusable technical indicators for **vectorbt** strategies. They are written to give
the same numbers as **TradingView** (each one follows the Pine Script
built-in, or the published source of the community script it is named after).

Each indicator comes in two forms:

* **Function**: pandas or numpy in, the same type out. Indicators with
  several outputs return a namedtuple.
* **vectorbt class** (`tv_indicators.vbt`): an `IndicatorFactory` class with
  parameter grids, multi-column input and the auto-generated
  `*_crossed_above`, `*_above` and similar helpers.

```python
import tv_indicators as ti
from tv_indicators.vbt import BBANDS, RSI, SUPERTREND
import vectorbt as vbt

bb = ti.bbands(df.close)                     # bb.basis, bb.upper, bb.lower, bb.bandwidth, bb.percent_b
st = ti.supertrend(df.high, df.low, df.close)

# parameter sweep
bb = BBANDS.run(df.close, length=[20, 30], mult=[2.0, 2.5], param_product=True)
entries = bb.close_crossed_below(bb.lower)
exits = bb.close_crossed_above(bb.upper)
pf = vbt.Portfolio.from_signals(df.close, entries, exits)
```

Requirements: `numpy`, `pandas`, `numba` and `vectorbt` (`vectorbt` is only
needed for `tv_indicators.vbt`). `TA-Lib` and `pytest` are only needed for
the tests.

```bash
python -m pytest tv_indicators/tests -q
```

## Indicator list

The names are the vectorbt class names (`tv_indicators.vbt.<NAME>`). Defaults
are TradingView's.

### Bollinger family

| Name | Function | Source | Defaults |
|---|---|---|---|
| BBANDS | `bbands(close, volume=nan, length, mult, ma_type)` | TV built-in *Bollinger Bands* (basis SMA/EMA/SMMA (RMA)/WMA/VWMA; stdev is always population stdev of the source) | 20, 2.0, SMA |
| BB_PERCENT_B | `bb_percent_b` | TV built-in *Bollinger Bands %B* (0..1 scale) | 20, 2.0 |
| BBW | `bbw` | TV built-in *Bollinger BandWidth* (x100), plus the 125-bar highest expansion / lowest contraction lines and a `squeeze` flag (BBW at its 125-bar low) | 20, 2.0, 125, 125 |
| BBTREND | `bbtrend` | TV built-in *BBTrend* (John Bollinger, 2024) | 20, 50, 2.0 |
| BBWP | `bbwp` | *Bollinger Band Width Percentile* [The_Caretaker] | 13, 252, SMA, MA 5 |
| DOUBLE_BBANDS | `double_bbands` | Kathy Lien's Double Bollinger Bands | 20, 1.0, 2.0 |
| SQUEEZE_MOMENTUM | `squeeze_momentum` | *Squeeze Momentum Indicator* [LazyBear], TradingView's most-liked script. `lazybear_compat=True` keeps the original's bug where BB uses `multKC` | 20, 2.0, 20, 1.5 |
| TTM_SQUEEZE | `ttm_squeeze` | *TTM Squeeze Pro* [Beardy_Fred]: BB(20,2) against KC at 1.0/1.5/2.0. `mid_sqz` is the classic John Carter squeeze | 20, 2.0, 1.0, 1.5, 2.0 |

### Moving averages and price sources

| Name | Function | Source |
|---|---|---|
| SMA / EMA / RMA / WMA | `sma`, `ema`, `rma`, `wma` | `ta.sma`, `ta.ema`, `ta.rma`, `ta.wma` |
| VWMA | `vwma(close, volume)` | `ta.vwma` |
| HMA | `hma` | `ta.hma` (`wma(2*wma(n/2) - wma(n), round(sqrt(n)))`) |
| DEMA / TEMA | `dema`, `tema` | TV built-ins |
| ALMA | `alma` | `ta.alma` (9, 0.85, 6) |
| LSMA | `lsma` | `ta.linreg` (25, offset 0) |
| MCGINLEY | `mcginley` | TV built-in *McGinley Dynamic* (14) |
| KAMA | `kama` | Kaufman AMA (not a TV built-in; same as TA-Lib) |
| MA | `ma(close, volume=nan, length, ma_type)` | picks an average by name |
| HL2 / HLC3 / OHLC4 / HLCC4 | `hl2`, `hlc3`, ... | price sources |

### Oscillators

| Name | Function | Source / defaults |
|---|---|---|
| RSI | `rsi` | TV built-in, 14 |
| STOCH | `stoch` → k, d | TV built-in, 14 / 1 / 3 |
| STOCH_RSI | `stoch_rsi` → k, d | TV built-in, 14 / 14 / 3 / 3 |
| MACD | `macd` → macd, signal, hist | TV built-in, 12 / 26 / 9, EMA or SMA for each line |
| CCI | `cci(src)` | TV built-in, 20. TV's default source is `hlc3`, so pass `ti.hlc3(h, l, c)` |
| WILLR | `willr` | Williams %R, 14 |
| MFI | `mfi` | `ta.mfi(hlc3, 14)` |
| ROC / MOM | `roc`, `mom` | 9 / 10 |
| AO | `awesome_oscillator` | 5 / 34 on hl2 |
| TSI | `tsi` → tsi, signal | 25 / 13 / 13 (x100) |
| CMO | `cmo` | TV built-in, 9. Uses plain sums; TA-Lib's CMO uses Wilder smoothing and gives different numbers |
| UO | `ultimate_oscillator` | 7 / 14 / 28 |
| FISHER | `fisher` → fisher, trigger | TV built-in, 9 |
| TRIX | `trix` | TV built-in: `10000 * change(log(ema³))`, 18 |
| WAVETREND | `wavetrend` → wt1, wt2 | *WaveTrend Oscillator* [LazyBear], 10 / 21 / 4 |
| CRSI | `connors_rsi` | TV built-in *Connors RSI*, 3 / 2 / 100 |
| COPPOCK | `coppock` | TV built-in, 10 / 14 / 11 |
| DPO | `dpo` | TV built-in with `isCentered=false` (no look-ahead), 21 |

### Trend and volatility

| Name | Function | Source / defaults |
|---|---|---|
| TR / ATR / NATR | `true_range`, `atr`, `natr` | `ta.tr(true)`, `ta.atr` (RMA 14; `smoothing` can be sma/ema/wma) |
| HV | `historical_volatility` | TV built-in, 10, annual 365 |
| KC | `keltner` | TV built-in *Keltner Channels*: 20, 2.0, EMA, ATR(10) |
| DONCHIAN | `donchian` | TV built-in, 20 |
| ENVELOPE | `envelope` | TV built-in, 20, 10 % |
| SUPERTREND | `supertrend` → supertrend, direction, trend | `ta.supertrend(3, 10)`. `direction` uses TV's convention (-1 = up); `trend` is +1 for up |
| PSAR | `psar` → psar, direction | `ta.sar(0.02, 0.02, 0.2)` |
| DMI / ADX | `dmi` → plus_di, minus_di, adx; `adx` | TV built-in *DMI*, 14 / 14 |
| AROON | `aroon` → up, down, oscillator | TV built-in, 14 |
| ICHIMOKU | `ichimoku` | TV built-in, 9 / 26 / 52 / 26 (see the look-ahead notes below) |
| CHOP | `choppiness` | TV built-in *Choppiness Index*, 14 |
| VORTEX | `vortex` | TV built-in, 14 |
| CHANDELIER_EXIT | `chandelier_exit` | *Chandelier Exit* [everget], 22 / 3.0 / use close |
| UT_BOT | `ut_bot` | *UT Bot Alerts* [QuantNomad], key 1, ATR 10 |
| HEIKIN_ASHI | `heikin_ashi` | Heikin Ashi candles |

### Volume

| Name | Function | Source / defaults |
|---|---|---|
| OBV | `obv` | `ta.cum(sign(change(close)) * volume)` |
| AD | `accdist` | `ta.accdist` |
| CMF | `cmf` | TV built-in, 20 |
| CHAIKIN_OSC | `chaikin_osc` | TV built-in, 3 / 10 |
| PVT | `pvt` | TV built-in |
| EFI | `efi` | Elder Force Index, 13 |
| VWAP_SESSION | `vwap(high, low, close, volume, anchor="D", band_mult)` / `vwap_session(..., session)` | TV built-in *VWAP* on hlc3, with stdev bands. `anchor` is D/W/M/Q/Y. The vbt class takes a `session` id input (`ti.session_ids(index, "D")`) |

### More moving averages and filters (`filters.py`)

| Name | Function | Source / defaults |
|---|---|---|
| ZLEMA | `zlema` | Zero-lag EMA, 20 |
| T3 | `t3` | Tillson T3, 5, vfactor 0.7 (same as TA-Lib) |
| SWMA | `swma` | `ta.swma` (4-bar 1-2-2-1 weights) |
| VIDYA | `vidya` | VAR/VIDYA [KivancOzbilgic], 9 / CMO 9. Starts from 0, like the script |
| TRIMA | `trima` | Triangular MA, 20 (same as TA-Lib) |
| EHMA / THMA | `ehma`, `thma` | Hull Suite [InSilico] exponential and triple Hull, 55 |
| SUPERSMOOTHER | `supersmoother` | Ehlers 2-pole Super Smoother, 10 |
| ULTIMATE_SMOOTHER | `ultimate_smoother` | Ehlers Ultimate Smoother (2024), 20 |
| MEDIAN | `median` | `ta.median` |
| MIDPOINT / MIDPRICE | `midpoint`, `midprice` | Same as TA-Lib, 14 |
| GMMA | `gmma` | Guppy: EMAs 3-15 and 30-60 (12 outputs) |
| ZLSMA | `zlsma` | Zero-lag LSMA [veryfid], 32 |
| MAVILIMW | `mavilimw` | MavilimW [KivancOzbilgic], 3 / 5 |
| CORAL | `coral` | Coral Trend [LazyBear], 21 / 0.4 |
| ITREND | `itrend` | Ehlers Instantaneous Trendline [LazyBear], alpha 0.07 |
| NADARAYA_WATSON | `nadaraya_watson` | Nadaraya-Watson Envelope [LuxAlgo], non-repainting mode, h 8, mult 3, window 500 |
| LAGUERRE / LAGUERRE_RSI | `laguerre`, `laguerre_rsi` | Ehlers Laguerre filter (gamma 0.8) and Laguerre RSI (gamma 0.5, 0..1 scale; Kivanc's version is gamma 0.8, x100) |
| FRAMA | `frama` | Ehlers Fractal Adaptive MA, 16 |
| CG | `center_of_gravity` | Ehlers Center of Gravity, 10 |

### More oscillators (`momentum.py`)

| Name | Function | Source / defaults |
|---|---|---|
| PPO / APO | `ppo`, `apo` | 12 / 26 / 9 (PPO matches TA-Lib with EMA) |
| PRICE_OSC | `price_oscillator` → ppo, signal, hist | TV built-in *Price Oscillator* (v35, which is a PPO): 12 / 26 / 9, EMA or SMA |
| KST | `kst` | TV built-in *Know Sure Thing* |
| RVGI | `rvgi` | TV built-in *Relative Vigor Index*, 10 |
| RVI | `relative_volatility_index` | TV built-in *Relative Volatility Index*, 10 / 14 |
| SMI_ERGODIC | `smi_ergodic` | TV built-in *SMI Ergodic Indicator/Oscillator*, 20 / 5 / 5 |
| SMI | `smi` → smi, signal | Stochastic Momentum Index [UCSgears], 5 / 3 |
| BULL_BEAR_POWER | `bull_bear_power` | Elder-Ray / TV *Bull Bear Power*, 13 |
| BOP | `bop` | Balance of Power |
| QSTICK | `qstick` | Chande Qstick, 8 |
| MASS_INDEX | `mass_index` | TV built-in, 10 |
| ULCER | `ulcer_index` | Ulcer Index, 14 |
| CHAIKIN_VOL | `chaikin_volatility` | 10 / 10 |
| ER | `efficiency_ratio` | Kaufman Efficiency Ratio, 10 |
| VHF | `vhf` | Vertical Horizontal Filter, 28 |
| TREND_STRENGTH | `trend_strength_index` | TV built-in *Trend Strength Index* (correlation with bar index), 14 |
| RCI | `rci` | `ta.rci` Rank Correlation Index, 10 (ties share their average rank) |
| PMO | `pmo` | DecisionPoint Price Momentum Oscillator, 35 / 20 / 10 |
| IFISH_RSI | `inverse_fisher_rsi` | Ehlers Inverse Fisher of RSI, 5 / 9 |
| TDI | `tdi` | Traders Dynamic Index, 13 / 34 / 1.6185 / 2 / 7 |
| MACD_V | `macd_v` | MACD-V (Spiroglou): MACD / ATR(26) x 100 |
| EWO | `elliott_wave_oscillator` | 5 / 35 |
| RMI | `rmi` | Relative Momentum Index, 20 / 5 |
| DEMARKER | `demarker` | 14 |
| PSY | `psychological_line` | 12 |
| DISPARITY | `disparity_index` | 14 |
| AC | `accelerator_oscillator` | TV built-in Accelerator Oscillator |
| ELDER_IMPULSE | `elder_impulse` | Elder Impulse System (+1 / 0 / -1) |
| CFO | `chande_forecast_oscillator` | 14 |
| PGO | `pretty_good_oscillator` | 14 |
| IMI | `intraday_momentum_index` | 14 |
| RWI | `random_walk_index` | 14 |
| ADR | `average_day_range` | TV built-in *Average Day Range*, 14 |
| CHOP_ZONE | `chop_zone` → angle, zone | TV built-in *Chop Zone* (EMA 34 angle, colour zones -4..4) |

### Community trend scripts, stops and bands (`community.py`)

| Name | Function | Source / defaults |
|---|---|---|
| SUPERTREND_KIVANC | `supertrend_kivanc` | SuperTrend [KivancOzbilgic], 10 / 3. Differs from `ta.supertrend` |
| HALFTREND | `halftrend` | HalfTrend [everget], 2 / 2 |
| SSL_CHANNEL | `ssl_channel` | SSL Channel [ErwinBeckers], 10 |
| RANGE_FILTER | `range_filter` | Range Filter Buy and Sell [guikroth], 100 / 3 |
| TWIN_RANGE_FILTER | `twin_range_filter` | Twin Range Filter [colinmck], 27 / 1.6 / 55 / 2 |
| TREND_MAGIC | `trend_magic` | Trend Magic [KivancOzbilgic] (the most-liked version; glaz's differs), CCI 20, ATR 5 x 1 |
| ALPHATREND | `alphatrend` | AlphaTrend [KivancOzbilgic], 1 / 14, MFI (or RSI) |
| OTT | `ott` | Optimized Trend Tracker [KivancOzbilgic], 2 / 1.4 |
| QQE | `qqe` | QQE [Glaz], 14 / 5 / 4.238. For QQE MOD's main line use 6 / 5 / 3 |
| STC | `schaff_trend_cycle` | STC Indicator - A Better MACD [SHK] |
| WAE | `waddah_attar_explosion` | Waddah Attar Explosion [LazyBear], dead zone 20 (`atr_dead_zone=True` for the SHK V2 ATR dead zone) |
| WVF | `williams_vix_fix` | CM_Williams_Vix_Fix [ChrisMoody] |
| VOLATILITY_STOP | `volatility_stop` | TV built-in, 20 / 2 |
| CHANDE_KROLL_STOP | `chande_kroll_stop` | TV built-in, 10 / 1 / 9 |
| ATR_STOP | `atr_stop_loss` | ATR Stop Loss Finder [veryfid], 14 / 1.5 |
| STARC | `starc_bands` | STARC Bands, SMA 6, ATR 15 x 2 |

### Bill Williams, pivots, trend (`bill_williams.py`, `pivots.py`, `trend.py`)

| Name | Function | Source / defaults |
|---|---|---|
| ALLIGATOR | `alligator` | TV built-in; values are the lines drawn under the current bar (no look-ahead) |
| GATOR | `gator` | Gator Oscillator |
| FRACTALS | `fractals` | TV built-in Williams Fractals (same tie rules), flagged when *confirmed* (2 bars later) |
| BW_MFI | `market_facilitation_index` | (high - low) / volume |
| PIVOT_POINTS_SESSION | `pivot_points(open, high, low, close, anchor, kind)` | TV *Pivot Points Standard*: traditional, fibonacci, woodie, classic, camarilla; P, R1-R3, S1-S3 from the previous calendar period of the index's timezone. TV builds them from daily settlement data, so session boundaries can differ; R4/R5 and DM are not included |
| ADXR | `adxr` | 14 (same as TA-Lib) |

### Statistics and volatility estimators (`statistics.py`)

| Name | Function | Notes |
|---|---|---|
| STDEV / VARIANCE / ZSCORE | `stdev`, `variance`, `zscore` | population, like Pine |
| PERCENTRANK | `percentrank` | `ta.percentrank` |
| LINREG | `linreg` → value, slope, intercept, r2, angle | matches TA-Lib's LINEARREG_* |
| CORREL | `correlation(close, other)` | `ta.correlation` |
| BETA | `beta(close, benchmark)` | rolling beta of returns |
| RELATIVE_STRENGTH | `relative_strength(close, benchmark)` | [Modhelius], 55 |
| PARKINSON / GARMAN_KLASS / ROGERS_SATCHELL / YANG_ZHANG | ... | range-based volatility, per bar (`annual` = bars per year to annualize) |

### More volume (`volume.py`)

| Name | Function | Source / defaults |
|---|---|---|
| EOM | `ease_of_movement` | TV built-in, 14 / 10000 |
| NVI / PVI | `nvi`, `pvi` | start 1000, EMA 255 signal |
| KLINGER | `klinger` | TV built-in, 34 / 55 / 13 |
| NET_VOLUME | `net_volume` | Legacy TV version, sign(change) x volume. The current built-in needs intrabar up/down volume |
| WILLIAMS_AD | `williams_ad` | Williams Accumulation/Distribution |
| RVOL | `relative_volume` | volume / sma(volume, 20) |
| VFI | `vfi` | Volume Flow Indicator [LazyBear], 130 |
| VZO | `volume_zone_oscillator` | 14 |
| ROLLING_VWAP | `rolling_vwap` | VWAP over the last N bars |

## Conventions and accuracy notes

* **Warm-up.** EMA and RMA seed with the SMA of the first `length` values,
  as Pine does. TradingView computes from the first bar of the symbol's
  history, while you compute from the first bar of your data, so any
  recursive indicator (EMA, RSI, ATR, ADX, MACD, Supertrend, ...) differs
  slightly at the start of the data and converges after about
  `4-5 × length` bars. For a precise comparison with a TV chart, load extra
  history before the period you trade.
* **`na` handling** follows Pine: comparisons with `na` are false and `x/0`
  gives `na`. EMA/RMA skip `na` inputs (they seed on the first `length`
  non-na values), as the Pine reference documents. Window functions (SMA,
  stdev, highest...) return `na` while their window holds an `na`; Pine
  skips those too, which only matters for series with gaps in the middle.
* **Standard deviation** is population stdev (`ta.stdev`, `biased=true`), the
  same as TradingView and TA-Lib. pandas `.std()` defaults to sample stdev
  (`ddof=1`) and does **not** match.
* **No look-ahead**, with one exception: `ichimoku().chikou` is
  `close[t+25]`, which is future data, so never use it in a signal. Use
  `senkou_a` / `senkou_b` (the cloud drawn under the current bar) for
  cloud rules.
* **PSAR** is a port of the Pine v6 reference code for `ta.sar` (verified
  line by line). It differs from TA-Lib around some reversals, because Pine
  checks for a reversal before clamping SAR to the prior two bars' range
  and TA-Lib clamps first.
* Aroon ties (equal highs) resolve to the most recent bar, as in TA-Lib.

## How it was verified

The tests in `tests/` (143 in all) check each indicator in one of these ways:

1. Against **TA-Lib** where its formula is the same as TradingView's: SMA,
   EMA, WMA, DEMA, TEMA, LINEARREG, KAMA, BBANDS (SMA, EMA and VWMA basis),
   RSI, STOCH, STOCHRSI, MACD, CCI, WILLR, ROC, MOM, ULTOSC, MFI, TRIX
   (after converting its scale), TRANGE, ATR, NATR, PLUS_DI, MINUS_DI, ADX,
   AROON, AD, OBV and ADOSC. Indicators that only differ in their warm-up
   seed are compared after they converge.
2. Against **bar-by-bar Python ports of the Pine source** for the
   TradingView-only scripts: Supertrend, Chandelier Exit, UT Bot, Fisher,
   BBWP, BBTrend, LazyBear Squeeze, Connors RSI, HMA, ALMA, Keltner,
   Donchian, Ichimoku, VWAP and Heikin Ashi.
3. Every vectorbt class runs, parameter grids work, and the results equal
   the function API.

4. Against **TradingView's own source code**: `test_pine_ports_builtin.py`
   ports the built-in scripts as TradingView serves them (the chart's
   "Source code" view) and the Pine v6 reference code, bar by bar, without
   using the library's kernels. `test_pine_ports_community.py` does the same
   for 18 community scripts from their published Pine code (Range Filter,
   Twin Range Filter, HalfTrend, SSL, Trend Magic, AlphaTrend, OTT, Kivanc
   SuperTrend, QQE, STC, WAE, VFI, Coral, Vix Fix, iTrend, MavilimW, ZLSMA,
   Nadaraya-Watson, SMI), including their default inputs. The only script
   whose source could not be found is LazyBear's Laguerre RSI; its formula
   was checked against KivancOzbilgic's version instead.

They have **not** been checked against numbers exported from a TradingView
chart. To spot-check one, export chart data with the indicator on it from
TradingView ("Export chart data") and compare the last few hundred bars.
