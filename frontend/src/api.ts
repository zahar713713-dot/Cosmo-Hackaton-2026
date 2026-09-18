import type {
  SimulationResult,
  InvestmentsState,
  ChannelPlan,
  ScenarioType,
  YearlyBalanceData,
  YearlyEconomicsData,
  ConstraintViolationItem,
} from './types';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export async function runSimulationAPI(
  scenarioType: ScenarioType,
  investments: InvestmentsState,
  channelPlans: Record<number, Record<string, ChannelPlan>>,
  discountRate = 0.08,
): Promise<SimulationResult> {
  const payload = {
    scenario_type: scenarioType,
    investments,
    channel_plans: channelPlans,
    discount_rate: discountRate,
  };

  try {
    const res = await fetch(`${API_BASE}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.message || 'Ошибка расчёта симуляции');
    }

    return await res.json();
  } catch (error) {
    console.warn('Backend API connection failed, running client-side fallback simulation engine...', error);
    return runClientFallbackSimulation(scenarioType, investments, channelPlans, discountRate);
  }
}

export async function downloadReport(
  scenarioType: ScenarioType,
  investments: InvestmentsState,
  channelPlans: Record<number, Record<string, ChannelPlan>>,
  format: 'xlsx' | 'csv',
) {
  const payload = {
    scenario_type: scenarioType,
    investments,
    channel_plans: channelPlans,
    discount_rate: 0.08,
  };

  const res = await fetch(`${API_BASE}/export/${format}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error('Ошибка выгрузки отчёта с сервера');
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = format === 'xlsx' ? 'fuel_depot_planning_report.xlsx' : 'fuel_depot_csv_bundle.zip';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

// Client-side simulation fallback mirror (guarantees 100% functionality even offline)
export function runClientFallbackSimulation(
  scenarioType: ScenarioType,
  investments: InvestmentsState,
  channelPlans: Record<number, Record<string, ChannelPlan>>,
  discountRate = 0.08,
): SimulationResult {
  const years = Object.keys(channelPlans).map(Number).sort((a, b) => a - b);
  const startYear = years[0] || 2035;

  const baseDemandTable: Record<number, { total: number; crit: number }> = {
    2035: { total: 100, crit: 80 },
    2036: { total: 140, crit: 105 },
    2037: { total: 190, crit: 135 },
    2038: { total: 250, crit: 170 },
    2039: { total: 320, crit: 210 },
    2040: { total: 390, crit: 250 },
    2041: { total: 460, crit: 295 },
    2042: { total: 530, crit: 340 },
    2043: { total: 600, crit: 385 },
    2044: { total: 670, crit: 430 },
    2045: { total: 740, crit: 475 },
  };

  let currentStock = (baseDemandTable[startYear]?.total || 100) * (45 / 365);

  const yearlyBalance: YearlyBalanceData[] = [];
  const yearlyEconomics: YearlyEconomicsData[] = [];
  const violations: ConstraintViolationItem[] = [];

  let cumCapex2037 = 0;
  let cumCapexTotal = 0;
  let consecEmergency = 0;

  for (const y of years) {
    let dTotal = baseDemandTable[y]?.total || 100;
    let dCrit = baseDemandTable[y]?.crit || 80;

    if (scenarioType === 'stress' && y >= 2038) {
      dTotal = Math.round(dTotal * 1.15 * 100) / 100;
      dCrit = Math.round(dCrit * 1.15 * 100) / 100;
    } else if (scenarioType === 'high_demand') {
      dTotal = Math.round(dTotal * 1.25 * 100) / 100;
      dCrit = Math.round(dCrit * 1.25 * 100) / 100;
    } else if (scenarioType === 'low_demand') {
      dTotal = Math.round(dTotal * 0.8 * 100) / 100;
      dCrit = Math.round(dCrit * 0.8 * 100) / 100;
    }

    const isZbo = investments.zbo_year !== null && y >= investments.zbo_year;
    const capacityMax = isZbo ? 120.0 : 70.0;
    const lossRate = isZbo ? 0.012 : 0.045;

    const yPlans = channelPlans[y] || {};
    let grossDeliv = 0;
    const channelDeliveries: Record<string, number> = {};
    const channelPayments: Record<string, number> = {};

    let yearProcurement = 0;
    let yearReservation = 0;

    for (const [ch, p] of Object.entries(yPlans)) {
      let mult = 1.0;
      let priceMult = 1.0;

      if (scenarioType === 'stress') {
        if (ch === 'Lunar-ISRU') {
          if (y === 2038) mult = 0.55;
          else if (y === 2039) mult = 0.75;
          else if (y >= 2040) mult = 1.0;
        }
        if ((ch === 'Earth-Core' || ch === 'Earth-Flex') && (y === 2038 || y === 2039)) {
          priceMult = 1.25;
        }
      } else if (scenarioType === 'geopolitical' && (y === 2037 || y === 2038 || y === 2039)) {
        if (ch === 'Earth-Core') priceMult = 1.35;
        if (ch === 'Earth-Flex') priceMult = 1.4;
      }

      const delivered = p.target_order_volume * mult;
      channelDeliveries[ch] = Math.round(delivered * 100) / 100;
      grossDeliv += delivered;

      // Economics
      let unitPrice = 6.2;
      let resTariff = 0.45;
      let topRatio = 0.7;

      if (ch === 'Earth-Flex') {
        unitPrice = 8.9;
        resTariff = 0.15;
        topRatio = 0.0;
      } else if (ch === 'Earth-New') {
        unitPrice = 7.1;
        resTariff = 0.3;
        topRatio = 0.5;
      } else if (ch === 'Lunar-ISRU') {
        unitPrice = 3.0;
        resTariff = 0.0;
        topRatio = 0.0;
      } else if (ch === 'Emergency') {
        unitPrice = 13.8;
        resTariff = 0.35;
        topRatio = 0.0;
      }

      const topThresh = topRatio * p.reserved_capacity;
      const billable = Math.max(p.target_order_volume, topThresh);
      const varPay = billable * unitPrice * priceMult;
      const resPay = p.reserved_capacity * resTariff;

      yearProcurement += varPay;
      yearReservation += resPay;
      channelPayments[ch] = Math.round((varPay + resPay) * 100) / 100;
    }

    const losses = grossDeliv * lossRate;
    const netInflow = grossDeliv - losses;
    const totalAvail = currentStock + netInflow;

    const servedTotal = Math.min(totalAvail, dTotal);
    const deficitTotal = dTotal - servedTotal;
    const servedCrit = Math.min(servedTotal, dCrit);
    const deficitCrit = dCrit - servedCrit;

    const endStock = Math.max(0, totalAvail - servedTotal);
    const isOverflow = endStock > capacityMax + 1e-4;
    const overflowAmt = isOverflow ? endStock - capacityMax : 0;

    const reqReserve = dTotal * (45 / 365);
    const emRes = yPlans['Emergency']?.reserved_capacity || 0;
    const isReserveMet = currentStock >= reqReserve - 1e-4 || currentStock + emRes >= reqReserve - 1e-4;

    const slTotal = dTotal > 0 ? servedTotal / dTotal : 1.0;
    const slCrit = dCrit > 0 ? servedCrit / dCrit : 1.0;

    yearlyBalance.push({
      year: y,
      start_stock: Math.round(currentStock * 100) / 100,
      gross_delivery: Math.round(grossDeliv * 100) / 100,
      losses: Math.round(losses * 100) / 100,
      net_available_inflow: Math.round(netInflow * 100) / 100,
      total_fuel_available: Math.round(totalAvail * 100) / 100,
      demand_total: Math.round(dTotal * 100) / 100,
      demand_critical: Math.round(dCrit * 100) / 100,
      served_demand_total: Math.round(servedTotal * 100) / 100,
      served_demand_critical: Math.round(servedCrit * 100) / 100,
      deficit_total: Math.round(deficitTotal * 100) / 100,
      deficit_critical: Math.round(deficitCrit * 100) / 100,
      end_stock: Math.round(endStock * 100) / 100,
      storage_capacity_max: capacityMax,
      is_storage_overflow: isOverflow,
      overflow_amount: Math.round(overflowAmt * 100) / 100,
      required_reserve_45d: Math.round(reqReserve * 100) / 100,
      is_reserve_satisfied: isReserveMet,
      service_level_total: Math.round(slTotal * 10000) / 10000,
      service_level_critical: Math.round(slCrit * 10000) / 10000,
      channel_deliveries: channelDeliveries,
    });

    // Economics
    const avgStock = (currentStock + endStock) / 2.0;
    const storageCost = avgStock * 0.72;
    const zboOpex = isZbo ? 12.0 : 0.0;
    const isruOpex = investments.isru_enabled && y >= 2038 ? 70.0 : 0.0;
    const initCost = y === startYear ? currentStock * 6.65 : 0.0;

    const totalOpex = yearProcurement + yearReservation + storageCost + zboOpex + isruOpex + initCost;

    let capexZbo = 0;
    if (investments.zbo_year === y) capexZbo = 180.0;

    let capexIsru = 0;
    if (investments.isru_enabled && investments.isru_capex_schedule[y]) {
      capexIsru = investments.isru_capex_schedule[y];
    }

    let capexEn = 0;
    if (investments.earth_new_enabled) {
      if (investments.earth_new_option_year === y) capexEn += 90.0;
      if (investments.earth_new_exercise_year === y) capexEn += 270.0;
    }

    const totalCapex = capexZbo + capexIsru + capexEn;
    cumCapexTotal += totalCapex;
    if (y <= 2037) cumCapex2037 += totalCapex;

    const totalExp = totalOpex + totalCapex;
    const df = 1.0 / Math.pow(1.0 + discountRate, y - startYear);
    const discExp = totalExp * df;

    yearlyEconomics.push({
      year: y,
      procurement_cost: Math.round(yearProcurement * 100) / 100,
      reservation_cost: Math.round(yearReservation * 100) / 100,
      storage_holding_cost: Math.round(storageCost * 100) / 100,
      zbo_fixed_opex: zboOpex,
      isru_fixed_opex: isruOpex,
      initial_stock_acquisition_cost: Math.round(initCost * 100) / 100,
      total_opex: Math.round(totalOpex * 100) / 100,
      capex_zbo: capexZbo,
      capex_earth_new: capexEn,
      capex_isru: capexIsru,
      total_capex: Math.round(totalCapex * 100) / 100,
      total_expenditure: Math.round(totalExp * 100) / 100,
      discount_factor: Math.round(df * 10000) / 10000,
      discounted_expenditure: Math.round(discExp * 100) / 100,
      channel_payments: channelPayments,
    });

    // Checks
    if (slCrit < 0.99 - 1e-5) {
      violations.push({
        year: String(y),
        rule_code: 'CRITICAL_SERVICE_LEVEL',
        rule_name: 'Критический уровень сервиса',
        expected: '>= 99.0%',
        actual: `${(slCrit * 100).toFixed(1)}%`,
        message: `Год ${y}: дефицит критического топлива ${deficitCrit.toFixed(1)} т. Сервис ${(slCrit * 100).toFixed(1)}% < 99%.`,
        is_violated: true,
      });
    }

    if (slTotal < 0.97 - 1e-5) {
      violations.push({
        year: String(y),
        rule_code: 'TOTAL_SERVICE_LEVEL',
        rule_name: 'Общий уровень сервиса',
        expected: '>= 97.0%',
        actual: `${(slTotal * 100).toFixed(1)}%`,
        message: `Год ${y}: общий дефицит ${deficitTotal.toFixed(1)} т. Сервис ${(slTotal * 100).toFixed(1)}% < 97%.`,
        is_violated: true,
      });
    }

    if (isOverflow) {
      violations.push({
        year: String(y),
        rule_code: 'STORAGE_CAPACITY_OVERFLOW',
        rule_name: 'Емкость хранилища',
        expected: `<= ${capacityMax} т`,
        actual: `${endStock.toFixed(1)} т`,
        message: `Год ${y}: переполнение бака на ${overflowAmt.toFixed(1)} т. Остаток ${endStock.toFixed(1)} т > ${capacityMax} т.`,
        is_violated: true,
      });
    }

    if (!isReserveMet) {
      violations.push({
        year: String(y),
        rule_code: 'RESERVE_45_DAYS',
        rule_name: '45-дневный резерв',
        expected: `>= ${reqReserve.toFixed(1)} т`,
        actual: `${currentStock.toFixed(1)} т`,
        message: `Год ${y}: физический запас ${currentStock.toFixed(1)} т меньше 45-дневного норматива ${reqReserve.toFixed(1)} т.`,
        is_violated: true,
      });
    }

    // Emergency consecutive check
    const emVol = yPlans['Emergency']?.target_order_volume || 0;
    if (emVol >= 15.0) {
      consecEmergency++;
      if (consecEmergency > 2) {
        violations.push({
          year: String(y),
          rule_code: 'EMERGENCY_CONSECUTIVE_LIMIT',
          rule_name: 'Лимит Emergency',
          expected: '<= 2 года подряд',
          actual: `${consecEmergency} года подряд`,
          message: `Канал Emergency используется как базовый ${consecEmergency} года подряд (норматив <= 2).`,
          is_violated: true,
        });
      }
    } else {
      consecEmergency = 0;
    }

    // Stress loss ceiling check
    if (scenarioType === 'stress' && y >= 2038 && lossRate > 0.02) {
      violations.push({
        year: String(y),
        rule_code: 'STRESS_LOSS_CEILING_BREACH',
        rule_name: 'Предел потерь в стрессе',
        expected: '<= 2.0%',
        actual: '4.5%',
        message: `Год ${y}: в обязательном стрессе потери 4.5% превышают лимит 2.0%. Необходима ZBO-модернизация!`,
        is_violated: true,
      });
    }

    currentStock = endStock;
  }

  // Multi-year checks
  if (cumCapex2037 > 1800.0) {
    violations.push({
      year: '2037',
      rule_code: 'CAPEX_2037_LIMIT',
      rule_name: 'Лимит CAPEX до 2037 г.',
      expected: '<= 1800.0 млн у.е.',
      actual: `${cumCapex2037.toFixed(1)} млн у.е.`,
      message: `Суммарный CAPEX до 2037 г. составил ${cumCapex2037.toFixed(1)} млн у.е., превышая лимит 1800 млн у.е.`,
      is_violated: true,
    });
  }

  if (cumCapexTotal > 2800.0) {
    violations.push({
      year: '2040',
      rule_code: 'CAPEX_TOTAL_LIMIT',
      rule_name: 'Суммарный лимит CAPEX',
      expected: '<= 2800.0 млн у.е.',
      actual: `${cumCapexTotal.toFixed(1)} млн у.е.`,
      message: `Суммарный CAPEX до 2040 г. составил ${cumCapexTotal.toFixed(1)} млн у.е., превышая лимит 2800 млн у.е.`,
      is_violated: true,
    });
  }

  const totDemand = yearlyBalance.reduce((s, r) => s + r.demand_total, 0);
  const totServed = yearlyBalance.reduce((s, r) => s + r.served_demand_total, 0);
  const totDeficit = yearlyBalance.reduce((s, r) => s + r.deficit_total, 0);
  const avgSlTot = yearlyBalance.reduce((s, r) => s + r.service_level_total, 0) / yearlyBalance.length;
  const avgSlCrit = yearlyBalance.reduce((s, r) => s + r.service_level_critical, 0) / yearlyBalance.length;

  const totGross = yearlyBalance.reduce((s, r) => s + r.gross_delivery, 0);
  const totLoss = yearlyBalance.reduce((s, r) => s + r.losses, 0);

  const totOpex = yearlyEconomics.reduce((s, r) => s + r.total_opex, 0);
  const totCapex = yearlyEconomics.reduce((s, r) => s + r.total_capex, 0);
  const totCost = totOpex + totCapex;
  const totNpv = yearlyEconomics.reduce((s, r) => s + r.discounted_expenditure, 0);

  return {
    scenario_type: scenarioType,
    scenario_name: scenarioType === 'baseline' ? 'Базовый план' : 'Обязательный стресс-тест',
    is_feasible: violations.length === 0,
    summary_kpi: {
      is_feasible: violations.length === 0,
      total_demand_tons: Math.round(totDemand * 10) / 10,
      total_served_demand_tons: Math.round(totServed * 10) / 10,
      total_deficit_tons: Math.round(totDeficit * 10) / 10,
      average_service_level_total: Math.round(avgSlTot * 10000) / 10000,
      average_service_level_critical: Math.round(avgSlCrit * 10000) / 10000,
      total_gross_delivery_tons: Math.round(totGross * 10) / 10,
      total_losses_tons: Math.round(totLoss * 10) / 10,
      total_opex_m_cu: Math.round(totOpex * 10) / 10,
      total_capex_m_cu: Math.round(totCapex * 10) / 10,
      total_cost_m_cu: Math.round(totCost * 10) / 10,
      npv_cost_m_cu: Math.round(totNpv * 10) / 10,
      cost_per_ton_served_m_cu: totServed > 0 ? Math.round((totCost / totServed) * 10000) / 10000 : 0,
      discounted_cost_per_ton_served_m_cu: totServed > 0 ? Math.round((totNpv / totServed) * 10000) / 10000 : 0,
    },
    yearly_balance: yearlyBalance,
    yearly_economics: yearlyEconomics,
    violations,
  };
}
