import React, { useState, useMemo } from 'react';
import type { SimulationResult } from '../types';
import {
  ComposedChart,
  Bar,
  Line,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  BarChart3,
  Database,
  Coins,
  ArrowRightLeft,
  PieChart as PieIcon,
  LayoutGrid,
  Sparkles,
  Info,
} from 'lucide-react';

interface AnalyticsChartsProps {
  simulation: SimulationResult | null;
  stressSimulation: SimulationResult | null;
}

type TabType = 'all' | 'balance' | 'inventory' | 'economics' | 'stress' | 'mix';

export const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ simulation, stressSimulation }) => {
  // ALL HOOKS MUST BE AT THE TOP (NO EARLY RETURNS BEFORE HOOKS)
  const [activeTab, setActiveTab] = useState<TabType>('all');

  const yearly_balance = simulation?.yearly_balance;
  const yearly_economics = simulation?.yearly_economics;

  // 1. Data for Material Balance Stacked Bar & Lines
  const balanceChartData = useMemo(() => {
    if (!yearly_balance) return [];
    return yearly_balance.map((b) => ({
      year: b.year,
      'Earth-Core': Number((b.channel_deliveries?.['Earth-Core'] || 0).toFixed(2)),
      'Earth-Flex': Number((b.channel_deliveries?.['Earth-Flex'] || 0).toFixed(2)),
      'Earth-New': Number((b.channel_deliveries?.['Earth-New'] || 0).toFixed(2)),
      'Lunar-ISRU': Number((b.channel_deliveries?.['Lunar-ISRU'] || 0).toFixed(2)),
      Emergency: Number((b.channel_deliveries?.['Emergency'] || 0).toFixed(2)),
      Дефицит: Number((b.deficit_total || 0).toFixed(2)),
      'Общий спрос': Number(b.demand_total.toFixed(2)),
      'Критический спрос': Number(b.demand_critical.toFixed(2)),
    }));
  }, [yearly_balance]);

  // 2. Data for Inventory Trajectory Area Chart
  const inventoryChartData = useMemo(() => {
    if (!yearly_balance) return [];
    return yearly_balance.map((b) => ({
      year: b.year,
      'Фактический остаток': Number(b.end_stock.toFixed(2)),
      '45-дневный резерв': Number(b.required_reserve_45d.toFixed(2)),
      'Вместимость баков': Number(b.storage_capacity_max.toFixed(2)),
    }));
  }, [yearly_balance]);

  // 3. Data for Cost Breakdown Stacked Bar
  const costChartData = useMemo(() => {
    if (!yearly_economics) return [];
    return yearly_economics.map((e) => ({
      year: e.year,
      Закупки: Number(e.procurement_cost.toFixed(2)),
      Бронирование: Number(e.reservation_cost.toFixed(2)),
      Хранение: Number(e.storage_holding_cost.toFixed(2)),
      'OPEX ZBO/ISRU': Number((e.zbo_fixed_opex + e.isru_fixed_opex).toFixed(2)),
      CAPEX: Number(e.total_capex.toFixed(2)),
      'Дисконтированные (NPV)': Number(e.discounted_expenditure.toFixed(2)),
    }));
  }, [yearly_economics]);

  // 4. Data for Dual-Axis Scenario Comparison
  const comparisonData = useMemo(() => {
    if (!yearly_balance || !yearly_economics) return [];
    return yearly_balance.map((b, idx) => {
      const stressBal = stressSimulation?.yearly_balance?.[idx];
      const baseEcon = yearly_economics[idx];
      const stressEcon = stressSimulation?.yearly_economics?.[idx];

      return {
        year: b.year,
        'NPV (Базовый план)': Number((baseEcon ? baseEcon.discounted_expenditure : 0).toFixed(2)),
        'NPV (Стресс-тест)': Number((stressEcon ? stressEcon.discounted_expenditure : 0).toFixed(2)),
        'Потери (Стресс-тест)': Number((stressBal ? stressBal.losses : 0).toFixed(2)),
        'Дефицит (Стресс-тест)': Number((stressBal ? stressBal.deficit_total : 0).toFixed(2)),
      };
    });
  }, [yearly_balance, yearly_economics, stressSimulation]);

  // 5. Data for Total Deliveries Channel Mix (Pie / Donut)
  const channelMixData = useMemo(() => {
    const totals: Record<string, number> = {
      'Earth-Core': 0,
      'Earth-Flex': 0,
      'Earth-New': 0,
      'Lunar-ISRU': 0,
      Emergency: 0,
    };

    if (yearly_balance) {
      yearly_balance.forEach((b) => {
        if (b.channel_deliveries) {
          totals['Earth-Core'] += b.channel_deliveries['Earth-Core'] || 0;
          totals['Earth-Flex'] += b.channel_deliveries['Earth-Flex'] || 0;
          totals['Earth-New'] += b.channel_deliveries['Earth-New'] || 0;
          totals['Lunar-ISRU'] += b.channel_deliveries['Lunar-ISRU'] || 0;
          totals['Emergency'] += b.channel_deliveries['Emergency'] || 0;
        }
      });
    }

    const totalAll = Object.values(totals).reduce((a, b) => a + b, 0);
    const colors: Record<string, string> = {
      'Earth-Core': '#ccff00',
      'Earth-Flex': '#ffffff',
      'Earth-New': '#00e5ff',
      'Lunar-ISRU': '#9d4edd',
      Emergency: '#ffb703',
    };

    const items = Object.entries(totals)
      .map(([name, value]) => ({
        name,
        value: Number(value.toFixed(1)),
        percent: totalAll > 0 ? Number(((value / totalAll) * 100).toFixed(1)) : 0,
        color: colors[name] || '#888888',
      }))
      .filter((item) => item.value > 0);

    const isruTotal = totals['Lunar-ISRU'];
    const isruShare = totalAll > 0 ? ((isruTotal / totalAll) * 100).toFixed(1) : '0';

    return { items, totalAll: Number(totalAll.toFixed(1)), isruShare };
  }, [yearly_balance]);

  // Safe cyber-brutalist Tooltip Style
  const customTooltipStyle = {
    backgroundColor: '#070709',
    border: '1px solid #27272a',
    borderRadius: '12px',
    fontSize: '11px',
    fontFamily: 'monospace',
    boxShadow: '0 10px 25px rgba(0,0,0,0.9)',
    color: '#ffffff',
  };

  // EARLY RETURN ONLY AFTER ALL HOOKS
  if (!simulation) return null;

  const isGrid = activeTab === 'all';

  return (
    <div className="mb-8 space-y-4">
      {/* Top Filter Tabs Toolbar */}
      <div className="bg-[#0a0a0c] p-2 rounded-2xl border border-neutral-800 shadow-xl flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 max-w-full">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold uppercase transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
              activeTab === 'all'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/20'
                : 'bg-neutral-900 text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span>Сводная сетка 2×2</span>
          </button>

          <button
            onClick={() => setActiveTab('balance')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold uppercase transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
              activeTab === 'balance'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/20'
                : 'bg-neutral-900 text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>01 Баланс & Спрос</span>
          </button>

          <button
            onClick={() => setActiveTab('inventory')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold uppercase transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
              activeTab === 'inventory'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/20'
                : 'bg-neutral-900 text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>02 Склад & Буфер 45д</span>
          </button>

          <button
            onClick={() => setActiveTab('economics')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold uppercase transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
              activeTab === 'economics'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/20'
                : 'bg-neutral-900 text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <Coins className="w-3.5 h-3.5" />
            <span>03 Экономика LCC</span>
          </button>

          <button
            onClick={() => setActiveTab('stress')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold uppercase transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
              activeTab === 'stress'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/20'
                : 'bg-neutral-900 text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <ArrowRightLeft className="w-3.5 h-3.5" />
            <span>04 Стресс-тест (Dual-Axis)</span>
          </button>

          <button
            onClick={() => setActiveTab('mix')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold uppercase transition flex items-center gap-1.5 cursor-pointer whitespace-nowrap ${
              activeTab === 'mix'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/20'
                : 'bg-neutral-900 text-neutral-400 hover:text-white hover:bg-neutral-800'
            }`}
          >
            <PieIcon className="w-3.5 h-3.5" />
            <span>05 Доли каналов & ISRU</span>
          </button>
        </div>

        <div className="hidden md:flex items-center gap-2 text-[11px] text-neutral-400 font-mono pr-2">
          <Sparkles className="w-3.5 h-3.5 text-[#ccff00]" />
          <span>РЕЖИМ: {activeTab === 'all' ? 'ОБЗОР 4 ГРАФИКОВ' : 'ДЕТАЛЬНЫЙ АНАЛИЗ'}</span>
        </div>
      </div>

      {/* Grid or Single View */}
      <div className={isGrid ? 'grid grid-cols-1 lg:grid-cols-2 gap-6' : 'space-y-6'}>
        {/* CHART 1: Material Balance & Demand */}
        {(isGrid || activeTab === 'balance') && (
          <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-[#ccff00] text-black">
                  <BarChart3 className="w-4 h-4 stroke-[2.5]" />
                </div>
                <div>
                  <span className="text-[10px] text-neutral-500 font-mono">&lt;график 01 // материальный баланс&gt;</span>
                  <h3 className="text-sm font-black uppercase tracking-wider text-white">
                    ПОСТАВКИ КАНАЛОВ И ПОКРЫТИЕ СПРОСА (Т/ГОД)
                  </h3>
                </div>
              </div>
              <span className="text-[10px] text-[#ccff00] font-mono border border-[#ccff00]/30 px-2 py-0.5 rounded-md bg-[#ccff00]/10">
                SLA &ge; 97%
              </span>
            </div>

            <div className={`${isGrid ? 'h-72 sm:h-80' : 'h-96'} w-full`}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={balanceChartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
                  <XAxis dataKey="year" stroke="#71717a" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11, fontFamily: 'monospace' }} unit=" т" />
                  <Tooltip
                    contentStyle={customTooltipStyle}
                    formatter={(val: any, name: any) => [`${Number(val).toLocaleString('ru-RU')} т`, name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '10px', fontFamily: 'monospace' }} />
                  <Bar dataKey="Earth-Core" stackId="deliveries" fill="#ccff00" name="Earth-Core (А)" />
                  <Bar dataKey="Earth-Flex" stackId="deliveries" fill="#ffffff" name="Earth-Flex (B)" />
                  <Bar dataKey="Earth-New" stackId="deliveries" fill="#00e5ff" name="Earth-New (C)" />
                  <Bar dataKey="Lunar-ISRU" stackId="deliveries" fill="#9d4edd" name="Lunar-ISRU (Луна)" />
                  <Bar dataKey="Emergency" stackId="deliveries" fill="#ffb703" name="Emergency (Резерв)" />
                  <Bar dataKey="Дефицит" stackId="deliveries" fill="#ff2a5f" name="Дефицит (Недопоставка)" />
                  <Line
                    type="monotone"
                    dataKey="Общий спрос"
                    stroke="#ff2a5f"
                    strokeWidth={2.5}
                    dot={{ r: 3.5, fill: '#ff2a5f' }}
                    name="Общий спрос"
                  />
                  <Line
                    type="monotone"
                    dataKey="Критический спрос"
                    stroke="#38bdf8"
                    strokeWidth={2}
                    strokeDasharray="4 4"
                    dot={{ r: 2.5, fill: '#38bdf8' }}
                    name="Критический спрос"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-3 pt-2.5 border-t border-neutral-850 flex items-center justify-between text-[11px] font-mono text-neutral-400">
              <span className="flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-neutral-500" />
                <span>Столбцы суммируют приход топлива; линии показывают директивный спрос.</span>
              </span>
              <span className="text-white font-bold">
                Обслужено: {simulation.summary_kpi.total_served_demand_tons.toLocaleString('ru-RU')} т
              </span>
            </div>
          </div>
        )}

        {/* CHART 2: Storage Dynamics & 45-day Buffer */}
        {(isGrid || activeTab === 'inventory') && (
          <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-white text-black">
                  <Database className="w-4 h-4 stroke-[2.5]" />
                </div>
                <div>
                  <span className="text-[10px] text-neutral-500 font-mono">&lt;график 02 // складской контур&gt;</span>
                  <h3 className="text-sm font-black uppercase tracking-wider text-white">
                    ДИНАМИКА ЗАПАСОВ И 45-ДНЕВНЫЙ БУФЕР
                  </h3>
                </div>
              </div>
              <span className="text-[10px] text-neutral-400 font-mono border border-neutral-700 px-2 py-0.5 rounded-md bg-neutral-900">
                Буфер 45 суток
              </span>
            </div>

            <div className={`${isGrid ? 'h-72 sm:h-80' : 'h-96'} w-full`}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={inventoryChartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                  <defs>
                    <linearGradient id="invGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ccff00" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#ccff00" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
                  <XAxis dataKey="year" stroke="#71717a" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11, fontFamily: 'monospace' }} unit=" т" />
                  <Tooltip
                    contentStyle={customTooltipStyle}
                    formatter={(val: any, name: any) => [`${Number(val).toLocaleString('ru-RU')} т`, name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '10px', fontFamily: 'monospace' }} />
                  <Area
                    type="monotone"
                    dataKey="Фактический остаток"
                    stroke="#ccff00"
                    strokeWidth={2.5}
                    fill="url(#invGradient)"
                    name="Фактический остаток"
                  />
                  <Line
                    type="monotone"
                    dataKey="45-дневный резерв"
                    stroke="#00e5ff"
                    strokeWidth={2.5}
                    strokeDasharray="4 4"
                    dot={{ r: 3, fill: '#00e5ff' }}
                    name="45-дневный буфер (Мин)"
                  />
                  <Line
                    type="stepAfter"
                    dataKey="Вместимость баков"
                    stroke="#a1a1aa"
                    strokeWidth={1.8}
                    strokeDasharray="3 3"
                    name="Предельная ёмкость баков"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-3 pt-2.5 border-t border-neutral-850 flex items-center justify-between text-[11px] font-mono text-neutral-400">
              <span className="flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-neutral-500" />
                <span>Зеленая область должна находиться строго выше синего пунктира (буфер 45 суток).</span>
              </span>
              <span className="text-[#00e5ff] font-bold">Буфер гарантирован</span>
            </div>
          </div>
        )}

        {/* CHART 3: Lifecycle Cost Structure (LCC) */}
        {(isGrid || activeTab === 'economics') && (
          <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-[#ccff00] text-black">
                  <Coins className="w-4 h-4 stroke-[2.5]" />
                </div>
                <div>
                  <span className="text-[10px] text-neutral-500 font-mono">&lt;график 03 // структура затрат lcc&gt;</span>
                  <h3 className="text-sm font-black uppercase tracking-wider text-white">
                    СТРУКТУРА СТОИМОСТИ ЖИЗНЕННОГО ЦИКЛА (МЛН У.Е.)
                  </h3>
                </div>
              </div>
              <span className="text-[10px] text-[#ccff00] font-mono border border-[#ccff00]/30 px-2 py-0.5 rounded-md bg-[#ccff00]/10">
                NPV (r=8%)
              </span>
            </div>

            <div className={`${isGrid ? 'h-72 sm:h-80' : 'h-96'} w-full`}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={costChartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
                  <XAxis dataKey="year" stroke="#71717a" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11, fontFamily: 'monospace' }} unit="M" />
                  <Tooltip
                    contentStyle={customTooltipStyle}
                    formatter={(val: any, name: any) => [`${Number(val).toLocaleString('ru-RU')} млн у.е.`, name]}
                  />
                  <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '10px', fontFamily: 'monospace' }} />
                  <Bar dataKey="Закупки" stackId="cost" fill="#ccff00" name="Закупка топлива" />
                  <Bar dataKey="Бронирование" stackId="cost" fill="#ffffff" name="Бронь мощностей" />
                  <Bar dataKey="Хранение" stackId="cost" fill="#ffb703" name="Хранение на ОТУ" />
                  <Bar dataKey="OPEX ZBO/ISRU" stackId="cost" fill="#9d4edd" name="OPEX ZBO / ISRU" />
                  <Bar dataKey="CAPEX" stackId="cost" fill="#ff2a5f" name="CAPEX инвестиции" />
                  <Line
                    type="monotone"
                    dataKey="Дисконтированные (NPV)"
                    stroke="#00e5ff"
                    strokeWidth={2.5}
                    dot={{ r: 3.5, fill: '#00e5ff' }}
                    name="Дисконтировано (NPV)"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-3 pt-2.5 border-t border-neutral-850 flex items-center justify-between text-[11px] font-mono text-neutral-400">
              <span className="flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-neutral-500" />
                <span>Столбцы — фактический LCC за год; бирюзовая линия — дисконтированный денежный поток.</span>
              </span>
              <span className="text-[#ccff00] font-bold">
                LCC: {simulation.summary_kpi.total_cost_m_cu.toLocaleString('ru-RU')} млн
              </span>
            </div>
          </div>
        )}

        {/* CHART 4: Dual-Axis Scenario Comparison (Stress vs Base) */}
        {(isGrid || activeTab === 'stress') && (
          <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-white text-black">
                  <ArrowRightLeft className="w-4 h-4 stroke-[2.5]" />
                </div>
                <div>
                  <span className="text-[10px] text-neutral-500 font-mono">&lt;график 04 // стресс-тест dual-axis&gt;</span>
                  <h3 className="text-sm font-black uppercase tracking-wider text-white">
                    БАЗОВЫЙ ПЛАН VS СТРЕСС-ТЕСТ (ФИНАНСЫ & ОБЪЁМЫ)
                  </h3>
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] font-mono">
                <span className="text-[#ccff00] border border-[#ccff00]/30 px-1.5 py-0.5 rounded bg-[#ccff00]/10">
                  Шкала 1: Млн
                </span>
                <span className="text-[#ffb703] border border-[#ffb703]/30 px-1.5 py-0.5 rounded bg-[#ffb703]/10">
                  Шкала 2: Тонны
                </span>
              </div>
            </div>

            <div className={`${isGrid ? 'h-72 sm:h-80' : 'h-96'} w-full`}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={comparisonData} margin={{ top: 10, right: -5, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
                  <XAxis dataKey="year" stroke="#71717a" tick={{ fontSize: 11, fontFamily: 'monospace' }} />

                  {/* Left Axis: Currency (M c.u.) */}
                  <YAxis
                    yAxisId="left"
                    stroke="#71717a"
                    tick={{ fontSize: 11, fontFamily: 'monospace' }}
                    unit="M"
                    orientation="left"
                  />

                  {/* Right Axis: Physical Tons */}
                  <YAxis
                    yAxisId="right"
                    stroke="#ffb703"
                    tick={{ fontSize: 11, fontFamily: 'monospace', fill: '#ffb703' }}
                    unit=" т"
                    orientation="right"
                  />

                  <Tooltip
                    contentStyle={customTooltipStyle}
                    formatter={(val: any, name: any) => {
                      const isTons = String(name).includes('Потери') || String(name).includes('Дефицит');
                      return [`${Number(val).toLocaleString('ru-RU')} ${isTons ? 'т' : 'млн у.е.'}`, name];
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '10px', fontFamily: 'monospace' }} />

                  {/* Left Axis Bars: Financial NPV */}
                  <Bar yAxisId="left" dataKey="NPV (Базовый план)" fill="#ccff00" name="NPV Базовый (млн)" />
                  <Bar yAxisId="left" dataKey="NPV (Стресс-тест)" fill="#ff2a5f" name="NPV Стресс-тест (млн)" />

                  {/* Right Axis Lines: Physical Deficit and Losses in Tons */}
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="Потери (Стресс-тест)"
                    stroke="#ffb703"
                    strokeWidth={2.5}
                    dot={{ r: 3.5, fill: '#ffb703' }}
                    name="Потери при стрессе (т)"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="Дефицит (Стресс-тест)"
                    stroke="#00e5ff"
                    strokeWidth={2.5}
                    strokeDasharray="4 4"
                    dot={{ r: 4, fill: '#00e5ff' }}
                    name="Дефицит при стрессе (т)"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-3 pt-2.5 border-t border-neutral-850 flex items-center justify-between text-[11px] font-mono text-neutral-400">
              <span className="flex items-center gap-1">
                <Info className="w-3.5 h-3.5 text-neutral-500" />
                <span>Двойная ось: левая шкала для затрат (млн), правая — для физических потерь и дефицита (т).</span>
              </span>
              <span className="text-[#ffb703] font-bold">Отказоустойчивость ТЗ</span>
            </div>
          </div>
        )}

        {/* CHART 5: Channel Mix & Lunar ISRU Sovereignty (Single Tab or Extra) */}
        {activeTab === 'mix' && (
          <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-6 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-[#9d4edd] text-white">
                  <PieIcon className="w-4 h-4 stroke-[2.5]" />
                </div>
                <div>
                  <span className="text-[10px] text-neutral-500 font-mono">&lt;график 05 // структура поставок&gt;</span>
                  <h3 className="text-sm font-black uppercase tracking-wider text-white">
                    МИКС КАНАЛОВ И ДОЛЯ ЛУННОГО РЕСУРСА (ISRU)
                  </h3>
                </div>
              </div>
              <span className="text-[10px] text-[#9d4edd] font-mono border border-[#9d4edd]/30 px-2 py-0.5 rounded-md bg-[#9d4edd]/10">
                Критерий ТЗ: Независимость от Земли
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              {/* Donut Chart */}
              <div className="h-80 w-full relative flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={channelMixData.items}
                      cx="50%"
                      cy="50%"
                      innerRadius={65}
                      outerRadius={105}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {channelMixData.items.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={customTooltipStyle}
                      formatter={(val: any) => [`${Number(val).toLocaleString('ru-RU')} т`, 'Объём']}
                    />
                  </PieChart>
                </ResponsiveContainer>

                {/* Center KPI in Donut */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-2xl font-black font-mono text-white">{channelMixData.isruShare}%</span>
                  <span className="text-[10px] font-mono text-[#9d4edd] uppercase font-bold tracking-wider">
                    LUNAR-ISRU
                  </span>
                </div>
              </div>

              {/* Breakdown Cards */}
              <div className="space-y-3">
                <div className="text-xs font-mono uppercase text-neutral-400 font-bold tracking-wider mb-2">
                  Совокупные поставки за горизонт планирования:
                </div>
                {channelMixData.items.map((item) => (
                  <div
                    key={item.name}
                    className="flex items-center justify-between p-3 rounded-xl bg-neutral-900/60 border border-neutral-800"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-md" style={{ backgroundColor: item.color }} />
                      <span className="text-xs font-bold text-white font-mono">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-3 font-mono text-xs">
                      <span className="text-neutral-400">{item.value.toLocaleString('ru-RU')} т</span>
                      <span className="font-bold text-white bg-neutral-800 px-2 py-0.5 rounded-md">
                        {item.percent}%
                      </span>
                    </div>
                  </div>
                ))}

                <div className="pt-3 border-t border-neutral-800 flex items-center justify-between font-mono text-xs">
                  <span className="text-neutral-400">ВСЕГО ПОСТАВЛЕНО:</span>
                  <span className="text-[#ccff00] font-bold text-sm">
                    {channelMixData.totalAll.toLocaleString('ru-RU')} т
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
