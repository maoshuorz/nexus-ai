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
    { id: "CEO", name: "Alex", status: "active", role: "首席执行官" },
    { id: "CMO", name: "Sarah", status: "active", role: "首席营销官" },
    { id: "CTO", name: "David", status: "active", role: "首席技术官" },
    { id: "CFO", name: "Lisa", status: "active", role: "首席财务官" },
    { id: "CPO", name: "Michael", status: "active", role: "首席产品官" },
    { id: "COO", name: "Emma", status: "active", role: "首席运营官" }
  ],
  projects: {
    discussing: 0,
    in_progress: 0,
    completed: 0
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
