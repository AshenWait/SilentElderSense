// 模拟数据生成器
export const mockData = {
  // 模拟事件数据
  events: [
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
    }
  ],

  // 模拟统计数据
  statistics: {
    total: 156,
    today: 8,
    fall: 45,
    stillness: 67,
    nightActivity: 44,
    handled: 142,
    pending: 14,
    accuracy: 94.5
  },

  // 模拟摄像头数据
  cameras: [
    { id: 1, name: '客厅摄像头', location: '客厅', status: 'online', resolution: '1920x1080' },
    { id: 2, name: '卧室摄像头', location: '卧室', status: 'online', resolution: '1920x1080' },
    { id: 3, name: '卫生间摄像头', location: '卫生间', status: 'offline', resolution: '1280x720' },
    { id: 4, name: '厨房摄像头', location: '厨房', status: 'online', resolution: '1920x1080' }
  ],

  // 模拟用户数据
  users: [
    { id: 1, username: 'admin', password: 'admin123', name: '系统管理员', role: 'admin' },
    { id: 2, username: 'family', password: 'family123', name: '家属用户', role: 'family' },
    { id: 3, username: 'monitor', password: 'monitor123', name: '监护人', role: 'monitor' }
  ],

  // 模拟场景数据
  scenes: [
    { id: 1, name: '客厅场景', location: '客厅', camera: '客厅摄像头', type: '起居室', area: '客厅全区域', enabled: true },
    { id: 2, name: '卧室场景', location: '卧室', camera: '卧室摄像头', type: '卧室', area: '卧室全区域', enabled: true },
    { id: 3, name: '卫生间场景', location: '卫生间', camera: '卫生间摄像头', type: '卫生间', area: '卫生间全区域', enabled: true }
  ],

  // 模拟时段数据
  timePeriods: [
    { id: 1, name: '日间监测', startTime: '06:00', endTime: '22:00', type: 'day', sensitivity: '高', enabled: true },
    { id: 2, name: '夜间监测', startTime: '22:00', endTime: '06:00', type: 'night', sensitivity: '中', enabled: true }
  ],

  // 模拟告警规则数据
  alertRules: [
    { id: 1, name: '跌倒告警规则', eventType: '跌倒检测', riskLevel: 'high', threshold: '置信度>0.8', notificationMethods: ['短信', 'APP推送'], enabled: true },
    { id: 2, name: '长时间静止告警', eventType: '长时间静止', riskLevel: 'medium', threshold: '静止>30分钟', notificationMethods: ['APP推送'], enabled: true }
  ]
}

// 生成随机事件
export function generateRandomEvent() {
  const types = ['fall', 'stillness', 'night_activity']
  const typeNames = ['跌倒检测', '长时间静止', '夜间异常活动']
  const locations = ['客厅', '卧室', '卫生间', '厨房', '走廊']
  const riskLevels = ['high', 'medium', 'low']

  const randomIndex = Math.floor(Math.random() * types.length)

  return {
    id: Date.now(),
    type: types[randomIndex],
    typeName: typeNames[randomIndex],
    riskLevel: riskLevels[Math.floor(Math.random() * riskLevels.length)],
    time: new Date().toLocaleString('zh-CN'),
    duration: Math.floor(Math.random() * 3600),
    status: 'pending',
    description: `在${locations[Math.floor(Math.random() * locations.length)]}检测到异常行为`,
    location: locations[Math.floor(Math.random() * locations.length)],
    confidence: 0.7 + Math.random() * 0.3
  }
}

// 生成模拟统计数据
export function generateMockStatistics() {
  return {
    total: Math.floor(Math.random() * 200) + 100,
    today: Math.floor(Math.random() * 20) + 5,
    fall: Math.floor(Math.random() * 60) + 30,
    stillness: Math.floor(Math.random() * 80) + 40,
    nightActivity: Math.floor(Math.random() * 50) + 20,
    handled: Math.floor(Math.random() * 150) + 100,
    pending: Math.floor(Math.random() * 20) + 5,
    accuracy: 90 + Math.random() * 9
  }
}