import React from 'react';
import type { SimulationResult } from '../types';
import {
  BarChart,
  Bar,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { BarChart3, Database, Coins, ArrowRightLeft } from 'lucide-react';

interface AnalyticsChartsProps {
  simulation: SimulationResult | null;
  stressSimulation: SimulationResult | null;
}

export const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ simulation, stressSimulation }) => {
  if (!simulation) return null;

  const { yearly_balance, yearly_economics } = simulation;

  // 1. Data for Material Balance Stacked Bar
  const balanceChartData = yearly_balance.map((b) => ({
    year: b.year,
    'Earth-Core': b.channel_deliveries['Earth-Core'] || 0,
    'Earth-Flex': b.channel_deliveries['Earth-Flex'] || 0,
    'Earth-New': b.channel_deliveries['Earth-New'] || 0,
    'Lunar-ISRU': b.channel_deliveries['Lunar-ISRU'] || 0,
    Emergency: b.channel_deliveries['Emergency'] || 0,
    'Общий спрос': b.demand_total,
    'Критический спрос': b.demand_critical,
    Дефицит: b.deficit_total,
  }));

  // 2. Data for Inventory Trajectory Area Chart
  const inventoryChartData = yearly_balance.map((b) => ({
    year: b.year,
    'Фактический остаток': b.end_stock,
    '45-дневный резерв': b.required_reserve_45d,
    'Ёмкость баков': b.storage_capacity_max,
  }));

  // 3. Data for Cost Breakdown Stacked Bar
  const costChartData = yearly_economics.map((e) => ({
    year: e.year,
    Закупки: e.procurement_cost,
    Бронирование: e.reservation_cost,
    Хранение: e.storage_holding_cost,
    'OPEX ZBO/ISRU': e.zbo_fixed_opex + e.isru_fixed_opex,
    CAPEX: e.total_capex,
    'Дисконтированные (NPV)': e.discounted_expenditure,
  }));

  // 4. Data for Scenario Comparison
  const comparisonData = yearly_balance.map((b, idx) => {
    const stressBal = stressSimulation?.yearly_balance[idx];
    const baseEcon = yearly_economics[idx];
    const stressEcon = stressSimulation?.yearly_economics[idx];

    return {
      year: b.year,
      'NPV (Базовый план)': baseEcon ? baseEcon.discounted_expenditure : 0,
      'NPV (Стресс-тест)': stressEcon ? stressEcon.discounted_expenditure : 0,
      'Потери (Базовый план)': b.losses,
      'Потери (Стресс-тест)': stressBal ? stressBal.losses : 0,
      'Дефицит (Стресс-тест)': stressBal ? stressBal.deficit_total : 0,
    };
  });

  const customTooltipStyle = {
    backgroundColor: '#050507',
    border: '1px solid #262626',
    borderRadius: '12px',
    fontSize: '11px',
    fontFamily: 'monospace',
    boxShadow: '0 10px 25px rgba(0,0,0,0.8)',
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Chart 1: Material Balance */}
      <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl">
        <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-[#ccff00] text-black">
              <BarChart3 className="w-4 h-4 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-[10px] text-neutral-500 font-mono">&lt;график 01 // материальный баланс&gt;</span>
              <h3 className="text-sm font-black uppercase tracking-wider text-white">
                ПОСТАВКИ И ПОКРЫТИЕ СПРОСА (Т/ГОД)
              </h3>
            </div>
          </div>
          <span className="text-[10px] text-neutral-500 font-mono hidden sm:inline">&lt;критерии 1 & 8&gt;</span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={balanceChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
              <XAxis dataKey="year" stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <YAxis stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <Tooltip contentStyle={customTooltipStyle} itemStyle={{ color: '#ffffff' }} />
              <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '8px', fontFamily: 'monospace' }} />
              <Bar dataKey="Earth-Core" stackId="a" fill="#ccff00" />
              <Bar dataKey="Earth-Flex" stackId="a" fill="#ffffff" />
              <Bar dataKey="Earth-New" stackId="a" fill="#00e5ff" />
              <Bar dataKey="Lunar-ISRU" stackId="a" fill="#9d4edd" />
              <Bar dataKey="Emergency" stackId="a" fill="#ffb703" />
              <Line type="monotone" dataKey="Общий спрос" stroke="#ff2a5f" strokeWidth={2.5} dot={{ r: 3 }} />
              <Line
                type="monotone"
                dataKey="Критический спрос"
                stroke="#38bdf8"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 2 }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 2: Inventory Dynamics */}
      <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl">
        <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-white text-black">
              <Database className="w-4 h-4 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-[10px] text-neutral-500 font-mono">&lt;график 02 // складской контур&gt;</span>
              <h3 className="text-sm font-black uppercase tracking-wider text-white">
                ДИНАМИКА ЗАПАСОВ И РЕЗЕРВА 45 ДНЕЙ
              </h3>
            </div>
          </div>
          <span className="text-[10px] text-neutral-500 font-mono hidden sm:inline">&lt;критерии 1 & 4&gt;</span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={inventoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
              <XAxis dataKey="year" stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <YAxis stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <Tooltip contentStyle={customTooltipStyle} itemStyle={{ color: '#ffffff' }} />
              <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '8px', fontFamily: 'monospace' }} />
              <Area type="monotone" dataKey="Фактический остаток" stroke="#ccff00" fill="#ccff00" fillOpacity={0.2} />
              <Line type="monotone" dataKey="45-дневный резерв" stroke="#00e5ff" strokeWidth={2} strokeDasharray="4 4" />
              <Line type="stepAfter" dataKey="Ёмкость баков" stroke="#ff2a5f" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 3: Cost Structure */}
      <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl">
        <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-[#ccff00] text-black">
              <Coins className="w-4 h-4 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-[10px] text-neutral-500 font-mono">&lt;график 03 // структура затрат lcc&gt;</span>
              <h3 className="text-sm font-black uppercase tracking-wider text-white">
                СТРУКТУРА СТОИМОСТИ ЖИЗНЕННОГО ЦИКЛА (МЛН)
              </h3>
            </div>
          </div>
          <span className="text-[10px] text-neutral-500 font-mono hidden sm:inline">&lt;критерий 3&gt;</span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={costChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
              <XAxis dataKey="year" stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <YAxis stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <Tooltip contentStyle={customTooltipStyle} itemStyle={{ color: '#ffffff' }} />
              <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '8px', fontFamily: 'monospace' }} />
              <Bar dataKey="Закупки" stackId="cost" fill="#ccff00" />
              <Bar dataKey="Бронирование" stackId="cost" fill="#ffffff" />
              <Bar dataKey="Хранение" stackId="cost" fill="#ffb703" />
              <Bar dataKey="OPEX ZBO/ISRU" stackId="cost" fill="#9d4edd" />
              <Bar dataKey="CAPEX" stackId="cost" fill="#ff2a5f" />
              <Line type="monotone" dataKey="Дисконтированные (NPV)" stroke="#00e5ff" strokeWidth={2.5} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 4: Scenario Comparison */}
      <div className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 shadow-2xl">
        <div className="flex items-center justify-between mb-4 border-b border-neutral-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-white text-black">
              <ArrowRightLeft className="w-4 h-4 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-[10px] text-neutral-500 font-mono">&lt;график 04 // сопоставление стресс-теста&gt;</span>
              <h3 className="text-sm font-black uppercase tracking-wider text-white">
                БАЗОВЫЙ ПЛАН VS ОБЯЗАТЕЛЬНЫЙ СТРЕСС-ТЕСТ
              </h3>
            </div>
          </div>
          <span className="text-[10px] text-neutral-500 font-mono hidden sm:inline">&lt;критерии 10 & 13&gt;</span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1c1c1f" />
              <XAxis dataKey="year" stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <YAxis stroke="#52525b" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <Tooltip contentStyle={customTooltipStyle} itemStyle={{ color: '#ffffff' }} />
              <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '8px', fontFamily: 'monospace' }} />
              <Bar dataKey="NPV (Базовый план)" fill="#ccff00" />
              <Bar dataKey="NPV (Стресс-тест)" fill="#ff2a5f" />
              <Line type="monotone" dataKey="Потери (Стресс-тест)" stroke="#ffb703" strokeWidth={2} />
              <Line type="monotone" dataKey="Дефицит (Стресс-тест)" stroke="#ffffff" strokeWidth={2.5} strokeDasharray="3 3" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

