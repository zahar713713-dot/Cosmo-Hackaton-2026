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

  const { violations, summary_kpi, yearly_balance, yearly_economics } = simulation;

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

  // Find minimum service levels across all years to match constraint checks
  const minCritSl =
    yearly_balance && yearly_balance.length > 0
      ? Math.min(...yearly_balance.map((b) => b.service_level_critical))
      : summary_kpi.average_service_level_critical;

  const minTotSl =
    yearly_balance && yearly_balance.length > 0
      ? Math.min(...yearly_balance.map((b) => b.service_level_total))
      : summary_kpi.average_service_level_total;

  // Calculate actual capex thru 2037
  const capexThru2037 =
    yearly_economics && yearly_economics.length > 0
      ? yearly_economics
          .filter((e) => parseInt(String(e.year), 10) <= 2037)
          .reduce((sum, e) => sum + e.total_capex, 0)
      : (capex37Violations[0] ? parseFloat(capex37Violations[0].actual) : summary_kpi.total_capex_m_cu);

  const cards = [
    {
      tag: '<крит. спрос>',
      title: 'КРИТИЧЕСКИЙ SLA',
      rule: critViolations.length === 0 ? 'Норма: ≥ 99.0%' : `Норма: ≥ 99.0% (ср. ${(summary_kpi.average_service_level_critical * 100).toFixed(1)}%)`,
      status: critViolations.length === 0,
      actual: critViolations.length === 0
        ? `${(summary_kpi.average_service_level_critical * 100).toFixed(1)}%`
        : `${(minCritSl * 100).toFixed(1)}%`,
      badge: critViolations.length > 0 ? `Худший год: ${(minCritSl * 100).toFixed(1)}%` : undefined,
      violationSummary: critViolations.length === 1
        ? critViolations[0].message
        : (critViolations.length > 1
            ? `Нарушено в ${critViolations.length} гг. (мин: ${(minCritSl * 100).toFixed(1)}%): ${critViolations.map((v) => `${v.year} г. (${v.actual})`).join(', ')}`
            : undefined),
    },
    {
      tag: '<общий спрос>',
      title: 'ОБЩИЙ SLA',
      rule: totViolations.length === 0 ? 'Норма: ≥ 97.0%' : `Норма: ≥ 97.0% (ср. ${(summary_kpi.average_service_level_total * 100).toFixed(1)}%)`,
      status: totViolations.length === 0,
      actual: totViolations.length === 0
        ? `${(summary_kpi.average_service_level_total * 100).toFixed(1)}%`
        : `${(minTotSl * 100).toFixed(1)}%`,
      badge: totViolations.length > 0 ? `Худший год: ${(minTotSl * 100).toFixed(1)}%` : undefined,
      violationSummary: totViolations.length === 1
        ? totViolations[0].message
        : (totViolations.length > 1
            ? `Нарушено в ${totViolations.length} гг. (мин: ${(minTotSl * 100).toFixed(1)}%): ${totViolations.map((v) => `${v.year} г. (${v.actual})`).join(', ')}`
            : undefined),
    },
    {
      tag: '<инвест этап 1>',
      title: 'CAPEX ДО 2037',
      rule: 'Лимит: ≤ 1 800 млн',
      status: capex37Violations.length === 0,
      actual: `${capexThru2037.toFixed(0)} млн`,
      badge: undefined,
      violationSummary: capex37Violations[0]?.message,
    },
    {
      tag: '<полный бюджет>',
      title: 'СУММАРНЫЙ CAPEX',
      rule: 'Лимит: ≤ 2 800 млн',
      status: capexTotViolations.length === 0,
      actual: `${summary_kpi.total_capex_m_cu.toFixed(0)} млн`,
      badge: undefined,
      violationSummary: capexTotViolations[0]?.message,
    },
    {
      tag: '<расходы opex>',
      title: 'СУММАРНЫЙ OPEX',
      rule: 'Закупки + Хранение',
      status: true,
      actual: `${summary_kpi.total_opex_m_cu.toLocaleString('ru-RU')} млн`,
      badge: undefined,
      violationSummary: undefined,
    },
    {
      tag: '<буферный запас>',
      title: 'РЕЗЕРВ 45 ДНЕЙ',
      rule: 'Страховой буфер',
      status: reserveViolations.length === 0,
      actual: reserveViolations.length === 0 ? 'СОБЛЮДЕН' : 'ДЕФИЦИТ',
      badge: reserveViolations.length > 1 ? `Нарушен в ${reserveViolations.length} гг.` : undefined,
      violationSummary: reserveViolations.length === 1
        ? reserveViolations[0].message
        : (reserveViolations.length > 1
            ? `Дефицит буфера в ${reserveViolations.length} гг.: ${reserveViolations.map((v) => `${v.year} г.`).join(', ')}`
            : undefined),
    },
    {
      tag: '<емкость оту>',
      title: 'ОБЪЕМ БАКОВ',
      rule: '70 т / 120 т (ZBO)',
      status: storageViolations.length === 0,
      actual: storageViolations.length === 0 ? 'В НОРМЕ' : 'ПЕРЕПОЛНЕНО',
      badge: storageViolations.length > 1 ? `Переполнение в ${storageViolations.length} гг.` : undefined,
      violationSummary: storageViolations.length === 1
        ? storageViolations[0].message
        : (storageViolations.length > 1
            ? `Переполнение баков в ${storageViolations.length} гг.: ${storageViolations.map((v) => `${v.year} г.`).join(', ')}`
            : undefined),
    },
  ];

  const opexAuditRecord = {
    year: '2035–2040',
    rule_code: 'OPEX_EXPENDITURE',
    rule_name: 'Операционные расходы (OPEX)',
    expected: 'Контроль эффективности',
    actual: `${summary_kpi.total_opex_m_cu.toLocaleString('ru-RU')} млн у.е.`,
    message: `Совокупные операционные затраты OPEX программы: ${summary_kpi.total_opex_m_cu.toLocaleString('ru-RU')} млн у.е. (включает закупку топлива, бронирование мощностей, хранение на ОТУ и эксплуатацию ZBO/ISRU).`,
    is_violated: false,
  };

  const displayedAuditRecords = filterOnlyViolations
    ? trueViolations
    : [opexAuditRecord, ...violations];

  return (
    <section className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 mb-6 shadow-2xl relative overflow-hidden">
      {/* Top bar with status pill */}
      <div className="flex items-center justify-between gap-3 mb-5 border-b border-neutral-800 pb-4">
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
        </div>
      </div>

      {/* 7 Metric Grid Blocks (Symmetrical & Centered) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2.5 sm:gap-3 items-stretch">
        {cards.map((c, i) => (
          <div
            key={i}
            onClick={() => {
              if (!c.status) {
                setShowAllDetails(true);
              }
            }}
            className={`h-full min-h-[135px] sm:min-h-[140px] p-3 sm:p-4 rounded-xl border transition-all flex flex-col items-center justify-between text-center relative ${
              i === 6 ? 'col-span-2 sm:col-span-1 md:col-span-2 lg:col-span-1' : ''
            } ${
              c.status
                ? 'bg-[#0f0f12] border-neutral-800/90 hover:border-neutral-700'
                : 'bg-[#1a080d] border-[#ff2a5f]/60 text-white shadow-lg shadow-[#ff2a5f]/10 cursor-pointer hover:border-[#ff2a5f]'
            }`}
            title={!c.status ? 'Нажмите, чтобы открыть подробный журнал нарушений' : undefined}
          >
            <div className="w-full flex items-center justify-between mb-1">
              <span className="text-[9px] sm:text-[10px] text-neutral-500 font-mono">{c.tag}</span>
              {c.status ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-[#ccff00] shrink-0" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 text-[#ff2a5f] shrink-0 animate-bounce" />
              )}
            </div>

            <div className="my-auto py-1">
              <div className="text-[10px] sm:text-[11px] font-black uppercase tracking-wider text-neutral-300">
                {c.title}
              </div>
              <div
                className={`text-lg sm:text-xl font-black font-mono tracking-tight mt-1 ${
                  c.status ? 'text-white' : 'text-[#ff2a5f]'
                }`}
              >
                {c.actual}
              </div>
              {c.badge && (
                <div className="text-[9px] text-[#ff6685] font-mono font-bold mt-0.5">
                  {c.badge}
                </div>
              )}
            </div>

            <div className="w-full text-[10px] text-neutral-500 font-mono pt-1.5 border-t border-neutral-850">
              {c.rule}
            </div>

            {!c.status && c.violationSummary && (
              <div className="mt-2 text-[10px] leading-tight text-rose-300 bg-rose-950/80 p-1.5 rounded border border-rose-800/80 font-mono w-full text-left break-words">
                {c.violationSummary}
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

      {/* Detailed Audit toggle bar placed right above the Journal */}
      <div className="mt-5 pt-4 border-t border-neutral-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <button
          onClick={() => setShowAllDetails(!showAllDetails)}
          className="flex items-center gap-2 text-xs font-mono border border-neutral-800 hover:border-neutral-600 px-3.5 py-1.5 rounded-full bg-neutral-900/80 text-neutral-300 hover:text-[#ccff00] transition self-start shadow-sm"
        >
          <span className="font-bold">
            {trueViolations.length > 0
              ? `НАРУШЕНИЯ (${trueViolations.length})`
              : `ПОДРОБНЫЙ АУДИТ (${displayedAuditRecords.length})`}
          </span>
          <span className="text-neutral-500 text-[11px]">
            {showAllDetails ? '• скрыть журнал' : '• открыть журнал ограничений'}
          </span>
          {showAllDetails ? (
            <ChevronUp className="w-3.5 h-3.5 text-[#ccff00]" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-[#ccff00]" />
          )}
        </button>

        {showAllDetails && (
          <div className="flex items-center gap-3 animate-fadeIn">
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
        )}
      </div>

      {/* Expandable detailed audit list */}
      {showAllDetails && (
        <div className="mt-3.5 animate-fadeIn">
          <div className="text-xs font-black uppercase tracking-wider text-neutral-300 mb-2.5">
            ЖУРНАЛ КОНТРОЛЬНЫХ ОГРАНИЧЕНИЙ И ШТРАФОВ (КРИТЕРИЙ 19)
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
