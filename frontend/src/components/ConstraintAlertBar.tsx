import React, { useState } from 'react';
import type { SimulationResult } from '../types';
import { CheckCircle2, AlertTriangle, XCircle, ChevronDown, ChevronUp, ShieldAlert, Zap } from 'lucide-react';

interface ConstraintAlertBarProps {
  simulation: SimulationResult | null;
}

export const ConstraintAlertBar: React.FC<ConstraintAlertBarProps> = ({ simulation }) => {
  const [showAllDetails, setShowAllDetails] = useState(false);
  const [filterOnlyViolations, setFilterOnlyViolations] = useState(false);

  if (!simulation) return null;

  const { violations, summary_kpi } = simulation;

  // Filter ONLY real violations where is_violated === true
  const trueViolations = violations.filter((v) => v.is_violated);
  const critViolations = violations.filter((v) => v.is_violated && v.rule_code === 'CRITICAL_SERVICE_LEVEL');
  const totViolations = violations.filter((v) => v.is_violated && v.rule_code === 'TOTAL_SERVICE_LEVEL');
  const capex37Violations = violations.filter((v) => v.is_violated && v.rule_code === 'CAPEX_2037_LIMIT');
  const capexTotViolations = violations.filter((v) => v.is_violated && v.rule_code === 'CAPEX_TOTAL_LIMIT');
  const reserveViolations = violations.filter((v) => v.is_violated && v.rule_code === 'RESERVE_45_DAYS');
  const storageViolations = violations.filter((v) => v.is_violated && v.rule_code === 'STORAGE_CAPACITY_OVERFLOW');
  const emergencyViolations = violations.filter((v) => v.is_violated && v.rule_code === 'EMERGENCY_CONSECUTIVE_LIMIT');
  const stressLossViolations = violations.filter((v) => v.is_violated && v.rule_code === 'STRESS_LOSS_CEILING_BREACH');

  const cards = [
    {
      tag: '<крит. спрос>',
      title: 'КРИТИЧЕСКИЙ SLA',
      rule: 'Норма: ≥ 99.0%',
      status: critViolations.length === 0,
      actual: `${(summary_kpi.average_service_level_critical * 100).toFixed(1)}%`,
      violation: critViolations[0],
    },
    {
      tag: '<общий спрос>',
      title: 'ОБЩИЙ SLA',
      rule: 'Норма: ≥ 97.0%',
      status: totViolations.length === 0,
      actual: `${(summary_kpi.average_service_level_total * 100).toFixed(1)}%`,
      violation: totViolations[0],
    },
    {
      tag: '<инвест этап 1>',
      title: 'CAPEX ДО 2037',
      rule: 'Лимит: ≤ 1 800 млн',
      status: capex37Violations.length === 0,
      actual: `${summary_kpi.total_capex_m_cu.toFixed(0)} млн`,
      violation: capex37Violations[0],
    },
    {
      tag: '<полный бюджет>',
      title: 'СУММАРНЫЙ CAPEX',
      rule: 'Лимит: ≤ 2 800 млн',
      status: capexTotViolations.length === 0,
      actual: `${summary_kpi.total_capex_m_cu.toFixed(0)} млн`,
      violation: capexTotViolations[0],
    },
    {
      tag: '<буферный запас>',
      title: 'РЕЗЕРВ 45 ДНЕЙ',
      rule: 'Страховой буфер',
      status: reserveViolations.length === 0,
      actual: reserveViolations.length === 0 ? 'СОБЛЮДЕН' : 'ДЕФИЦИТ',
      violation: reserveViolations[0],
    },
    {
      tag: '<емкость оту>',
      title: 'ОБЪЕМ БАКОВ',
      rule: '70 т / 120 т (ZBO)',
      status: storageViolations.length === 0,
      actual: storageViolations.length === 0 ? 'В НОРМЕ' : 'ПЕРЕПОЛНЕНО',
      violation: storageViolations[0],
    },
  ];

  const displayedAuditRecords = filterOnlyViolations
    ? trueViolations
    : violations;

  return (
    <section className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 mb-6 shadow-2xl relative overflow-hidden">
      {/* Top bar with status pill and audit toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 border-b border-neutral-800 pb-4">
        <div className="flex items-center gap-3">
          {summary_kpi.is_feasible ? (
            <div className="flex items-center gap-2 bg-[#ccff00] text-black px-4 py-1.5 rounded-full text-xs font-black tracking-wider uppercase shadow-lg shadow-[#ccff00]/20">
              <Zap className="w-3.5 h-3.5 fill-black" />
              <span>ПЛАН ИСПОЛНИМ // ВСЕ ОГРАНИЧЕНИЯ В НОРМЕ</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 bg-[#ff2a5f] text-white px-4 py-1.5 rounded-full text-xs font-black tracking-wider uppercase animate-pulse shadow-lg shadow-[#ff2a5f]/20">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>НАРУШЕНЫ ОГРАНИЧЕНИЯ КЕЙСА ({trueViolations.length})</span>
            </div>
          )}
          <span className="text-[11px] text-neutral-500 font-mono tracking-wide hidden md:inline">
            &lt;контроль критериев 4, 10, 19&gt;
          </span>
        </div>

        <button
          onClick={() => setShowAllDetails(!showAllDetails)}
          className="flex items-center gap-1.5 text-xs text-neutral-400 hover:text-[#ccff00] transition font-mono border border-neutral-800 hover:border-neutral-600 px-3 py-1 rounded-full bg-neutral-900/60"
        >
          <span>
            {trueViolations.length > 0
              ? `НАРУШЕНИЯ (${trueViolations.length})`
              : `ПОДРОБНЫЙ АУДИТ (${violations.length})`}
          </span>
          {showAllDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5 text-[#ccff00]" />}
        </button>
      </div>

      {/* 6 Metric Grid Blocks (Symmetrical & Centered) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 items-stretch">
        {cards.map((c, i) => (
          <div
            key={i}
            className={`h-full min-h-[140px] p-4 rounded-xl border transition-all flex flex-col items-center justify-between text-center relative ${
              c.status
                ? 'bg-[#0f0f12] border-neutral-800/90 hover:border-neutral-700'
                : 'bg-[#1a080d] border-[#ff2a5f]/60 text-white shadow-lg shadow-[#ff2a5f]/10'
            }`}
          >
            <div className="w-full flex items-center justify-between mb-1">
              <span className="text-[10px] text-neutral-500 font-mono">{c.tag}</span>
              {c.status ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-[#ccff00] shrink-0" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 text-[#ff2a5f] shrink-0 animate-bounce" />
              )}
            </div>

            <div className="my-auto py-1">
              <div className="text-[11px] font-black uppercase tracking-wider text-neutral-300">
                {c.title}
              </div>
              <div
                className={`text-xl sm:text-2xl font-black font-mono tracking-tight mt-1 ${
                  c.status ? 'text-white' : 'text-[#ff2a5f]'
                }`}
              >
                {c.actual}
              </div>
            </div>

            <div className="w-full text-[10px] text-neutral-500 font-mono pt-1.5 border-t border-neutral-850">
              {c.rule}
            </div>

            {!c.status && c.violation && (
              <div className="mt-2 text-[10px] leading-tight text-rose-300 bg-rose-950/80 p-1.5 rounded border border-rose-800/80 font-mono w-full">
                {c.violation.message}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Additional specific rule flags if violated */}
      {(emergencyViolations.length > 0 || stressLossViolations.length > 0) && (
        <div className="mt-4 flex flex-wrap gap-2">
          {emergencyViolations.map((v, i) => (
            <div
              key={i}
              className="text-xs bg-amber-950/80 border border-amber-500 text-amber-300 px-3.5 py-1.5 rounded-full flex items-center gap-2 font-mono"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>{v.message}</span>
            </div>
          ))}
          {stressLossViolations.map((v, i) => (
            <div
              key={i}
              className="text-xs bg-rose-950/80 border border-rose-500 text-rose-300 px-3.5 py-1.5 rounded-full flex items-center gap-2 font-mono"
            >
              <XCircle className="w-3.5 h-3.5 text-rose-400" />
              <span>{v.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Expandable detailed audit list */}
      {showAllDetails && (
        <div className="mt-5 pt-4 border-t border-neutral-800 animate-fadeIn">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <span className="text-xs font-black uppercase tracking-wider text-neutral-300">
              ЖУРНАЛ КОНТРОЛЬНЫХ ОГРАНИЧЕНИЙ И ШТРАФОВ (КРИТЕРИЙ 19)
            </span>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-1.5 text-[11px] text-neutral-400 cursor-pointer font-mono">
                <input
                  type="checkbox"
                  checked={filterOnlyViolations}
                  onChange={(e) => setFilterOnlyViolations(e.target.checked)}
                  className="rounded border-neutral-700 bg-neutral-800 text-[#ccff00] focus:ring-0"
                />
                <span>Только нарушения</span>
              </label>
              <span className="text-[11px] text-neutral-500 font-mono">
                Записей: {displayedAuditRecords.length} (Нарушений: {trueViolations.length})
              </span>
            </div>
          </div>

          <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
            {displayedAuditRecords.length === 0 ? (
              <div className="text-xs text-[#ccff00] p-3 rounded-xl bg-neutral-900/60 border border-neutral-800 font-mono">
                ✓ Нарушений не зафиксировано. Программа поставок полностью удовлетворяет жестким ограничениям ТЗ.
              </div>
            ) : (
              displayedAuditRecords.map((v, i) => (
                <div
                  key={i}
                  className={`flex items-start gap-3 text-xs p-3 rounded-xl font-mono border ${
                    v.is_violated
                      ? 'bg-[#14080b] border-rose-900/60'
                      : 'bg-neutral-900/40 border-neutral-800/80 text-neutral-300'
                  }`}
                >
                  <span
                    className={`text-[10px] font-black px-2 py-0.5 rounded-full shrink-0 ${
                      v.is_violated
                        ? 'bg-[#ff2a5f] text-white'
                        : 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
                    }`}
                  >
                    {v.is_violated ? 'НАРУШЕНИЕ' : 'В НОРМЕ'}
                  </span>
                  <span className="font-bold text-neutral-400 shrink-0">[{v.rule_code}]</span>
                  <span className="flex-1 text-neutral-300">{v.message}</span>
                  {v.year && <span className="text-neutral-500 shrink-0">Год: {v.year}</span>}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </section>
  );
};
