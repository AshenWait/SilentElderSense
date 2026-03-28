/**
 * 风险相关工具函数
 * 用于前后端统一的风险等级和原因映射
 */

// 风险等级 → Element Plus Tag 类型
export const RISK_TAG_TYPES = {
  'HIGH': 'danger',
  'MEDIUM': 'warning',
  'LOW': 'primary',
  'NORMAL': 'success'
}

// 风险等级中文
export const RISK_LEVEL_LABELS = {
  'HIGH': '高风险',
  'MEDIUM': '中风险',
  'LOW': '低风险',
  'NORMAL': '正常'
}

// 风险原因中文
export const RISK_REASON_LABELS = {
  'fallen': '跌倒',
  'stillness': '长时间静止',
  'night_abnormal': '夜间异常'
}

// 事件类型中文
export const EVENT_TYPE_LABELS = {
  'FALLEN': '跌倒',
  'STILLNESS': '长时间静止',
  'NIGHT_ABNORMAL': '夜间异常'
}

/**
 * 获取风险等级对应的 Element Plus Tag 类型
 * @param {string} riskLevel - 风险等级 (HIGH/MEDIUM/LOW/NORMAL)
 * @returns {string} Tag 类型
 */
export function getRiskTagType(riskLevel) {
  return RISK_TAG_TYPES[riskLevel] || 'info'
}

/**
 * 获取风险的中文显示标签
 * @param {string} riskLevel - 风险等级
 * @param {string} riskReason - 风险原因
 * @returns {string} 中文标签
 */
export function getRiskLabel(riskLevel, riskReason) {
  if (riskLevel === 'NORMAL') return '正常'

  const levelStr = RISK_LEVEL_LABELS[riskLevel] || riskLevel
  const reasonStr = RISK_REASON_LABELS[riskReason] || riskReason || ''

  return reasonStr ? `${levelStr}：${reasonStr}` : levelStr
}

/**
 * 获取事件类型的中文标签
 * @param {string} eventType - 事件类型 (FALLEN/STILLNESS/NIGHT_ABNORMAL)
 * @returns {string} 中文标签
 */
export function getEventTypeLabel(eventType) {
  return EVENT_TYPE_LABELS[eventType] || eventType
}