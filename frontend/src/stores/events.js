import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEventsStore = defineStore('events', () => {
  const events = ref([
    {
      id: 1,
      type: 'fall',
      typeName: '跌倒检测',
      riskLevel: 'high',
      time: '2026-03-22 14:32:15',
      duration: 8,
      status: 'pending',
      description: '在客厅区域检测到跌倒行为',
      location: '客厅',
      confidence: 0.92
    },
    {
      id: 2,
      type: 'stillness',
      typeName: '长时间静止',
      riskLevel: 'medium',
      time: '2026-03-22 12:15:30',
      duration: 1800,
      status: 'handled',
      description: '卧室区域静止超过30分钟',
      location: '卧室',
      confidence: 0.85
    },
    {
      id: 3,
      type: 'night_activity',
      typeName: '夜间异常活动',
      riskLevel: 'low',
      time: '2026-03-22 03:45:22',
      duration: 45,
      status: 'handled',
      description: '夜间在走廊反复徘徊',
      location: '走廊',
      confidence: 0.78
    },
    {
      id: 4,
      type: 'fall',
      typeName: '跌倒检测',
      riskLevel: 'high',
      time: '2026-03-21 18:20:10',
      duration: 12,
      status: 'handled',
      description: '在卫生间检测到滑倒',
      location: '卫生间',
      confidence: 0.95
    },
    {
      id: 5,
      type: 'stillness',
      typeName: '长时间静止',
      riskLevel: 'medium',
      time: '2026-03-21 09:45:00',
      duration: 2400,
      status: 'handled',
      description: '书房区域静止超过40分钟',
      location: '书房',
      confidence: 0.82
    }
  ])

  const statistics = ref({
    total: 156,
    today: 8,
    fall: 45,
    stillness: 67,
    nightActivity: 44,
    handled: 142,
    pending: 14,
    accuracy: 94.5
  })

  const addEvent = (event) => {
    events.value.unshift({
      ...event,
      id: Date.now(),
      time: new Date().toLocaleString('zh-CN')
    })
    statistics.value.total++
    statistics.value.today++
  }

  const updateEventStatus = (id, status) => {
    const event = events.value.find(e => e.id === id)
    if (event) {
      event.status = status
      if (status === 'handled') {
        statistics.value.handled++
        statistics.value.pending--
      }
    }
  }

  const getEventsByType = (type) => {
    return events.value.filter(e => e.type === type)
  }

  const getRecentEvents = (limit = 10) => {
    return events.value.slice(0, limit)
  }

  return {
    events,
    statistics,
    addEvent,
    updateEventStatus,
    getEventsByType,
    getRecentEvents
  }
})