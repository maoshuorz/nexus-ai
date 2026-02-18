const fs = require('fs');
const path = require('path');

// 读取真实数据
const ordersPath = path.join(__dirname, '../data/orders.json');
let ordersData = { orders: [], metadata: {} };

try {
  const content = fs.readFileSync(ordersPath, 'utf8');
  ordersData = JSON.parse(content);
} catch (e) {
  console.log('Using default empty data');
}

const metadata = ordersData.metadata || {};
const orders = ordersData.orders || [];

// 生成Dashboard数据
const dashboardData = {
  today_revenue: 0,
  total_orders: orders.length,
  active_agents: 6,
  new_inquiries: orders.length,
  unread_messages: 0,
  status: "真实数据",
  message: "公司运营中 - 等待首单",
  last_updated: new Date().toISOString(),
  agents: [
    { id: "CEO", name: "Alex", status: "active", role: "首席执行官", current_task: "实时决策与监督" },
    { id: "CMO", name: "Sarah", status: "active", role: "首席营销官", current_task: "市场调研与项目提案" },
    { id: "CTO", name: "David", status: "active", role: "首席技术官", current_task: "网站实时数据修复" },
    { id: "CFO", name: "Lisa", status: "active", role: "首席财务官", current_task: "财务监控与收入追踪" },
    { id: "CPO", name: "Michael", status: "active", role: "首席产品官", current_task: "产品规划与UI优化" },
    { id: "COO", name: "Emma", status: "active", role: "首席运营官", current_task: "Gmail接单系统监控" }
  ],
  projects: {
    discussing: [
      // CMO提交的待讨论项目
      { name: "AI播客自动生成", priority: "P0", submitter: "CMO Sarah", date: "2026-02-18" },
      { name: "智能客服外包", priority: "P0", submitter: "CMO Sarah", date: "2026-02-18" },
      { name: "AI技能市场", priority: "P1", submitter: "CMO Sarah", date: "2026-02-18" },
      { name: "小说IP衍生品", priority: "P1", submitter: "CMO Sarah", date: "2026-02-18" },
      { name: "运营监控SaaS", priority: "P2", submitter: "CMO Sarah", date: "2026-02-18" },
      { name: "工作流编排服务", priority: "P1", submitter: "CMO Sarah", date: "2026-02-18" }
    ],
    in_progress: [
      // CEO决策并分配的进行中的项目
      { name: "网站实时更新修复", owner: "CTO David", progress: 100, deadline: "2026-02-18" }
    ],
    completed: [
      // 已完成的项目
      { name: "Gmail自动接单系统v2.0", date: "2026-02-18" },
      { name: "网站UI重设计v3.5", date: "2026-02-18" },
      { name: "VoxYZ风格监控系统", date: "2026-02-18" },
      { name: "项目管理工作流程v2.0", date: "2026-02-18" }
    ]
  }
};

// 确保目录存在
const dataDir = path.join(__dirname, '../data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// 写入文件
const outputPath = path.join(dataDir, 'dashboard.json');
fs.writeFileSync(outputPath, JSON.stringify(dashboardData, null, 2));

console.log('Dashboard data generated:', outputPath);
console.log('Data:', JSON.stringify(dashboardData, null, 2));
