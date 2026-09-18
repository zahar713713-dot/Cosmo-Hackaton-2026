import React, { useState, useEffect, useCallback } from 'react';
import type {
  ScenarioType,
  InvestmentsState,
  ChannelPlan,
  SimulationResult,
  CustomChannelConfig,
} from './types';
import { runSimulationAPI, downloadReport } from './api';
import { Header } from './components/Header';
import { ConstraintAlertBar } from './components/ConstraintAlertBar';
import { InvestmentControls } from './components/InvestmentControls';
import { PlanningSliders } from './components/PlanningSliders';
import { AnalyticsCharts } from './components/AnalyticsCharts';
import { CustomizationModal } from './components/CustomizationModal';
import { Cpu } from 'lucide-react';

const BASELINE_DEMAND: Record<number, number> = {
  2035: 100,
  2036: 140,
  2037: 190,
  2038: 250,
  2039: 320,
  2040: 390,
  2041: 460,
  2042: 530,
  2043: 600,
  2044: 670,
  2045: 740,
};

function createDefaultChannelPlans(horizonYears: number[]): Record<number, Record<string, ChannelPlan>> {
  const plans: Record<number, Record<string, ChannelPlan>> = {};

  for (const y of horizonYears) {
    const d = BASELINE_DEMAND[y] || 100;
    // Balanced baseline dispatcher
    const coreCap = Math.min(190, Math.round(d * 0.6));
    let rem = d - coreCap;

    const flexCap = Math.min(110, Math.round(rem * 0.7));
    rem = Math.max(0, rem - flexCap);

    const isruCap = y >= 2038 ? Math.min(120, rem) : 0;
    rem = Math.max(0, rem - isruCap);

    let finalFlex = flexCap;
    if (rem > 0 && finalFlex + rem <= 110) {
      finalFlex += rem;
      rem = 0;
    }

    plans[y] = {
      'Earth-Core': { reserved_capacity: coreCap, target_order_volume: coreCap },
      'Earth-Flex': { reserved_capacity: finalFlex, target_order_volume: finalFlex },
      'Earth-New': { reserved_capacity: 0, target_order_volume: 0 },
      'Lunar-ISRU': { reserved_capacity: isruCap, target_order_volume: isruCap },
      'Emergency': { reserved_capacity: 20, target_order_volume: 0 }, // Standby reserve
    };
  }
  return plans;
}

export const App: React.FC = () => {
  const [extendedHorizon, setExtendedHorizon] = useState(false);
  const activeYears = extendedHorizon
    ? [2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045]
    : [2035, 2036, 2037, 2038, 2039, 2040];

  const [scenario, setScenario] = useState<ScenarioType>('baseline');
  const [discountRate, setDiscountRate] = useState(0.08);

  const [investments, setInvestments] = useState<InvestmentsState>({
    zbo_year: 2036,
    isru_enabled: true,
    isru_capex_schedule: { 2035: 250, 2036: 500, 2037: 500 },
    earth_new_enabled: false,
    earth_new_option_year: null,
    earth_new_exercise_year: null,
  });

  const [channelPlans, setChannelPlans] = useState<Record<number, Record<string, ChannelPlan>>>(() =>
    createDefaultChannelPlans(activeYears)
  );

  const [customChannel, setCustomChannel] = useState<CustomChannelConfig>({
    enabled: false,
    name: 'Канал-F (Синтетический)',
    max_capacity: 100,
    var_cost: 6.5,
    res_tariff: 0.25,
    take_or_pay: 0.4,
    reliability: 0.95,
  });

  const [isCustomizationOpen, setIsCustomizationOpen] = useState(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [stressSimulationResult, setStressSimulationResult] = useState<SimulationResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Sync horizon changes with channel plans
  useEffect(() => {
    setChannelPlans((prev) => {
      const updated = { ...prev };
      for (const y of activeYears) {
        if (!updated[y]) {
          updated[y] = {
            'Earth-Core': { reserved_capacity: 190, target_order_volume: 190 },
            'Earth-Flex': { reserved_capacity: 110, target_order_volume: 110 },
            'Earth-New': { reserved_capacity: 0, target_order_volume: 0 },
            'Lunar-ISRU': { reserved_capacity: 100, target_order_volume: 100 },
            Emergency: { reserved_capacity: 20, target_order_volume: 0 },
          };
        }
      }
      return updated;
    });
  }, [extendedHorizon]);

  // Reactive simulation recalculation
  const triggerRecalculation = useCallback(async () => {
    setIsCalculating(true);
    try {
      // 1. Current scenario
      const mainResult = await runSimulationAPI(scenario, investments, channelPlans, discountRate);
      setSimulationResult(mainResult);

      // 2. Parallel Stress calculation for comparative charts
      const stressResult = await runSimulationAPI('stress', investments, channelPlans, discountRate);
      setStressSimulationResult(stressResult);
    } catch (e) {
      console.error('Calculation failure:', e);
    } finally {
      setIsCalculating(false);
    }
  }, [scenario, investments, channelPlans, discountRate]);

  useEffect(() => {
    const timer = setTimeout(() => {
      triggerRecalculation();
    }, 80); // Debounced instant reactivity
    return () => clearTimeout(timer);
  }, [triggerRecalculation]);

  const handleReset = () => {
    setScenario('baseline');
    setInvestments({
      zbo_year: 2036,
      isru_enabled: true,
      isru_capex_schedule: { 2035: 250, 2036: 500, 2037: 500 },
      earth_new_enabled: false,
      earth_new_option_year: null,
      earth_new_exercise_year: null,
    });
    setDiscountRate(0.08);
    setExtendedHorizon(false);
    setChannelPlans(createDefaultChannelPlans([2035, 2036, 2037, 2038, 2039, 2040]));
  };

  const handleExport = async (format: 'xlsx' | 'csv') => {
    setIsExporting(true);
    try {
      await downloadReport(scenario, investments, channelPlans, format);
    } catch (e) {
      console.error('Export error:', e);
    } finally {
      setIsExporting(false);
    }
  };


  return (
    <div className="min-h-screen bg-[#050507] text-white flex flex-col selection:bg-[#ccff00] selection:text-black font-sans">
      {/* Header with Presets & Actions */}
      <Header
        currentScenario={scenario}
        onSelectScenario={(s) => setScenario(s)}
        onReset={handleReset}
        onExport={handleExport}
        onOpenCustomization={() => setIsCustomizationOpen(true)}
        isExporting={isExporting}
      />

      {/* Main Operator Console */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        {/* KPI Summary Block (Reference Style: 1 Lime Accent Card + High Impact Metric Cards) */}
        {simulationResult && (
          <div className="mb-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
            {/* Card 1: Electric Lime Accent Card */}
            <div className="p-4 rounded-2xl bg-[#ccff00] text-black border border-[#ccff00] flex flex-col justify-between shadow-lg shadow-[#ccff00]/10">
              <div>
                <span className="text-[10px] font-black uppercase tracking-wider text-black/75 font-mono">
                  &lt;статус узла&gt;
                </span>
                <div className="text-sm font-black uppercase tracking-tight mt-1 leading-snug">
                  {simulationResult.summary_kpi.is_feasible ? 'ПЛАН ИСПОЛНИМ' : 'НАРУШЕНИЕ ЛИМИТОВ'}
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-black/20">
                <div className="text-xs font-black font-mono">
                  SLA: {(simulationResult.summary_kpi.average_service_level_critical * 100).toFixed(1)}%
                </div>
                <div className="text-[10px] font-bold text-black/75 font-mono">
                  {simulationResult.summary_kpi.is_feasible ? 'Критерии 19–20 OK' : 'Требует ребаланса'}
                </div>
              </div>
            </div>

            {/* Card 2: LCC Cost */}
            <div className="p-4 rounded-2xl bg-[#0c0c0e] border border-neutral-800 flex flex-col justify-between hover:border-neutral-700 transition">
              <div>
                <span className="text-[10px] text-neutral-500 font-mono uppercase">&lt;совокупные затраты lcc&gt;</span>
                <div className="text-2xl lg:text-3xl font-black text-white font-mono tracking-tight mt-1">
                  {simulationResult.summary_kpi.total_cost_m_cu.toLocaleString('ru-RU')}
                </div>
              </div>
              <div className="mt-2 text-[10px] text-neutral-400 font-mono uppercase">
                МЛН У.Е. // OPEX + CAPEX
              </div>
            </div>

            {/* Card 3: NPV Cost */}
            <div className="p-4 rounded-2xl bg-[#0c0c0e] border border-neutral-800 flex flex-col justify-between hover:border-neutral-700 transition">
              <div>
                <span className="text-[10px] text-neutral-500 font-mono uppercase">&lt;npv затрат (r=8%)&gt;</span>
                <div className="text-2xl lg:text-3xl font-black text-[#ccff00] font-mono tracking-tight mt-1">
                  {simulationResult.summary_kpi.npv_cost_m_cu.toLocaleString('ru-RU')}
                </div>
              </div>
              <div className="mt-2 text-[10px] text-neutral-400 font-mono uppercase">
                МЛН У.Е. // ДИСКОНТ. СТОИМОСТЬ
              </div>
            </div>

            {/* Card 4: Demand Served */}
            <div className="p-4 rounded-2xl bg-[#0c0c0e] border border-neutral-800 flex flex-col justify-between hover:border-neutral-700 transition">
              <div>
                <span className="text-[10px] text-neutral-500 font-mono uppercase">&lt;обслуженный спрос&gt;</span>
                <div className="text-2xl lg:text-3xl font-black text-white font-mono tracking-tight mt-1">
                  {simulationResult.summary_kpi.total_served_demand_tons.toLocaleString('ru-RU')}
                </div>
              </div>
              <div className="mt-2 text-[10px] text-neutral-400 font-mono uppercase">
                Т КРТ ИЗ {simulationResult.summary_kpi.total_demand_tons.toLocaleString('ru-RU')} Т
              </div>
            </div>

            {/* Card 5: Deficit */}
            <div className="p-4 rounded-2xl bg-[#0c0c0e] border border-neutral-800 flex flex-col justify-between hover:border-neutral-700 transition">
              <div>
                <span className="text-[10px] text-neutral-500 font-mono uppercase">&lt;суммарный дефицит&gt;</span>
                <div
                  className={`text-2xl lg:text-3xl font-black font-mono tracking-tight mt-1 ${
                    simulationResult.summary_kpi.total_deficit_tons > 0 ? 'text-[#ff2a5f] animate-pulse' : 'text-white'
                  }`}
                >
                  {simulationResult.summary_kpi.total_deficit_tons.toLocaleString('ru-RU')}
                </div>
              </div>
              <div className="mt-2 text-[10px] text-neutral-400 font-mono uppercase">
                Т // ОБЩИЙ SLA {(simulationResult.summary_kpi.average_service_level_total * 100).toFixed(1)}%
              </div>
            </div>

            {/* Card 6: Losses */}
            <div className="p-4 rounded-2xl bg-[#0c0c0e] border border-neutral-800 flex flex-col justify-between hover:border-neutral-700 transition">
              <div>
                <span className="text-[10px] text-neutral-500 font-mono uppercase">&lt;потери оборота&gt;</span>
                <div className="text-2xl lg:text-3xl font-black text-white font-mono tracking-tight mt-1">
                  {simulationResult.summary_kpi.total_losses_tons.toLocaleString('ru-RU')}
                </div>
              </div>
              <div className="mt-2 text-[10px] text-neutral-400 font-mono uppercase">
                Т // УДЕЛ: {simulationResult.summary_kpi.cost_per_ton_served_m_cu.toFixed(2)} М/Т
              </div>
            </div>
          </div>
        )}

        {/* 1. Constraint Alert Bar */}
        <ConstraintAlertBar simulation={simulationResult} />

        {/* 2. Investment Gate Controls */}
        <InvestmentControls investments={investments} onChange={(inv) => setInvestments(inv)} />

        {/* 3. Planning Sliders */}
        <PlanningSliders
          channelPlans={channelPlans}
          investments={investments}
          yearlyBalance={simulationResult?.yearly_balance || []}
          onChange={(p) => setChannelPlans(p)}
        />

        {/* 4. Analytics & Comparative Charts */}
        <AnalyticsCharts simulation={simulationResult} stressSimulation={stressSimulationResult} />
      </main>

      {/* Footer */}
      <footer className="bg-[#050507] border-t border-neutral-800 py-4 px-6 text-xs text-neutral-500 font-mono">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Орбитальный топливный узел (ОТУ) // Цислунарный космоконтур 2035–2040 гг.</span>
          <span className="flex items-center gap-2 text-white">
            <Cpu className={`w-3.5 h-3.5 text-[#ccff00] ${isCalculating ? 'animate-spin' : ''}`} />
            <span>
              {isCalculating ? 'ПЕРЕСЧЕТ СЕТКИ...' : 'МАТЕМАТИЧЕСКОЕ ЯДРО АКТИВНО // ОТКЛИК МГНОВЕННЫЙ'}
            </span>
          </span>
        </div>
      </footer>

      {/* Customization Modal */}
      <CustomizationModal
        isOpen={isCustomizationOpen}
        onClose={() => setIsCustomizationOpen(false)}
        extendedHorizon={extendedHorizon}
        onToggleExtendedHorizon={(en) => setExtendedHorizon(en)}
        customChannel={customChannel}
        onUpdateCustomChannel={(c) => setCustomChannel(c)}
        discountRate={discountRate}
        onUpdateDiscountRate={(r) => setDiscountRate(r)}
      />
    </div>
  );
};

export default App;
