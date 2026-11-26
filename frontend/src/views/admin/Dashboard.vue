<template>
  <div class="dashboard" v-loading="loading">
    <div class="stat-grid">
      <div v-for="item in cards" :key="item.label" class="stat-card panel">
        <div class="stat-icon" :style="{ background: item.bg, color: item.color }">
          <el-icon :size="24"><component :is="item.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <div class="chart-row">
      <div class="panel chart-card">
        <h3 class="chart-title">近 7 天发布趋势</h3>
        <div ref="trendRef" class="chart"></div>
      </div>
      <div class="panel chart-card">
        <h3 class="chart-title">分类在售分布</h3>
        <div ref="categoryRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { User, Goods, Sell, ChatDotRound } from '@element-plus/icons-vue'
import { adminApi } from '../../api'

const loading = ref(false)
const stats = ref({
  user_count: 0,
  product_count: 0,
  on_sale_count: 0,
  sold_count: 0,
  message_count: 0,
  category_stat: [],
  trend: []
})

const trendRef = ref()
const categoryRef = ref()
let trendChart = null
let categoryChart = null

const cards = computed(() => [
  { label: '学生用户', value: stats.value.user_count, icon: User, bg: '#eef4ff', color: '#3b7bfd' },
  { label: '商品总数', value: stats.value.product_count, icon: Goods, bg: '#fff4e6', color: '#ff8f1f' },
  { label: '在售商品', value: stats.value.on_sale_count, icon: Sell, bg: '#eafaf1', color: '#18a058' },
  { label: '留言总数', value: stats.value.message_count, icon: ChatDotRound, bg: '#fdeef0', color: '#e8466e' }
])

function renderTrend() {
  if (!trendRef.value) return
  trendChart = trendChart || echarts.init(trendRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 24, bottom: 30 },
    xAxis: {
      type: 'category',
      data: stats.value.trend.map(t => t.date),
      axisLine: { lineStyle: { color: '#d7dbe5' } }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#f0f2f7' } }
    },
    series: [
      {
        name: '新增商品',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        data: stats.value.trend.map(t => t.count),
        itemStyle: { color: '#ff6b35' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255,107,53,0.35)' },
            { offset: 1, color: 'rgba(255,107,53,0.02)' }
          ])
        }
      }
    ]
  })
}

function renderCategory() {
  if (!categoryRef.value) return
  categoryChart = categoryChart || echarts.init(categoryRef.value)
  categoryChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 件 ({d}%)' },
    legend: { bottom: 0, icon: 'circle' },
    color: ['#ff6b35', '#3b7bfd', '#18a058', '#ffb020', '#8b5cf6', '#e8466e', '#14b8a6'],
    series: [
      {
        name: '在售商品',
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        data: stats.value.category_stat
      }
    ]
  })
}

function handleResize() {
  trendChart && trendChart.resize()
  categoryChart && categoryChart.resize()
}

async function loadStats() {
  loading.value = true
  try {
    stats.value = await adminApi.stats()
    await nextTick()
    renderTrend()
    renderCategory()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart && trendChart.dispose()
  categoryChart && categoryChart.dispose()
})
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px 24px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  margin-top: 2px;
  color: var(--text-sub);
  font-size: 13px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
  margin-top: 18px;
}

.chart-card {
  padding: 18px 22px 10px;
}

.chart-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
}

.chart {
  height: 320px;
}

@media (max-width: 1100px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>
