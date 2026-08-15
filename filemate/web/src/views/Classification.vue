<template>
  <div class="classification-page">
    <el-alert
      title="请先在导入页面上传文件"
      type="info"
      :closable="false"
      v-if="!currentFile"
    />

    <template v-else>
      <el-card>
        <template #header>
          <div class="card-header">
            <h3><el-icon><Collection /></el-icon> 分类预览</h3>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>分类结果</span>
              </template>
              <div class="result-item">
                <el-tag type="primary" size="large">
                  {{ currentFile.category || '待确认' }}
                </el-tag>
                <span class="confidence">
                  置信度: {{ (currentFile.confidence * 100).toFixed(1) }}%
                </span>
              </div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>修改分类</span>
              </template>
              <el-select v-model="selectedCategory" placeholder="选择分类" style="width: 100%">
                <el-option label="课件" value="课件" />
                <el-option label="作业" value="作业" />
                <el-option label="竞赛通知" value="竞赛通知" />
                <el-option label="考试通知" value="考试通知" />
                <el-option label="参考资料" value="参考资料" />
                <el-option label="大创通知" value="大创通知" />
                <el-option label="待确认" value="待确认" />
              </el-select>
              <el-button
                type="primary"
                style="margin-top: 12px"
                @click="confirmCategory"
                :loading="confirming"
              >
                确认分类
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-card>

      <!-- ECharts 饼图：分类统计（真实数据） -->
      <el-card style="margin-top: 20px">
        <template #header>
          <span>分类分布</span>
        </template>
        <div v-loading="chartLoading" style="min-height: 300px">
          <el-empty
            v-if="!hasData"
            :description="chartError || '暂无处理记录，上传资料后会在这里看到分类分布'"
            style="height: 300px"
          />
          <div v-else ref="chartRef" style="height: 300px"></div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Collection } from '@element-plus/icons-vue'
import { getSession, updateSessionDraft, getHistory } from '../services/api'
import { useFileStore } from '../stores/fileStore'
import type { Category } from '../types'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([PieChart, LegendComponent, TooltipComponent, CanvasRenderer])

const route = useRoute()
const fileStore = useFileStore()
const chartRef = ref<HTMLElement>()

const currentFile = computed(() => fileStore.currentFile)
const selectedCategory = ref<Category | ''>('')
const confirming = ref(false)

// 分类分布图表状态（真实数据）
const chartLoading = ref(false)
const chartError = ref('')
const hasData = ref(false)
const chartData = ref<Array<{ name: string; value: number; itemStyle: { color: string } }>>([])

// 单一森林绿阶梯色板（遵循设计系统：只用一个品牌强调色）
const CATEGORY_COLORS: Record<string, string> = {
  '课件': '#2f7d55',
  '作业': '#3e8a61',
  '竞赛通知': '#4e9670',
  '考试通知': '#5ea380',
  '参考资料': '#6eb090',
  '大创通知': '#7ebda0',
  '待确认': '#8fc9b0',
}

watch(currentFile, (file) => {
  if (file) {
    selectedCategory.value = file.category
  }
})

onMounted(() => {
  const sessionId = route.query.session as string
  if (sessionId) {
    loadSession(sessionId)
  }
  loadDistribution()
})

async function loadSession(sessionId: string) {
  try {
    const session = await getSession(sessionId)
    fileStore.setCurrentFile(session)
  } catch (e) {
    console.error('Failed to load session:', e)
  }
}

async function confirmCategory() {
  if (!currentFile.value) return

  confirming.value = true
  try {
    const updated = await updateSessionDraft(currentFile.value.session_id, {
      category: selectedCategory.value
    })
    fileStore.setCurrentFile(updated)
    ElMessage.success('分类已保存，确认命名后执行归档')
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    confirming.value = false
  }
}

async function loadDistribution() {
  chartLoading.value = true
  chartError.value = ''
  try {
    const history = await getHistory(undefined, 200)
    const counts: Record<string, number> = {}
    for (const s of history) {
      const cat = s.category || '待确认'
      counts[cat] = (counts[cat] || 0) + 1
    }
    chartData.value = Object.entries(counts).map(([name, value]) => ({
      name,
      value,
      itemStyle: { color: CATEGORY_COLORS[name] || '#2f7d55' },
    }))
    hasData.value = chartData.value.length > 0
    if (hasData.value) {
      await nextTick()
      renderChart()
    }
  } catch (e: any) {
    chartError.value = e.message || '分类分布加载失败'
    hasData.value = false
  } finally {
    chartLoading.value = false
  }
}

function renderChart() {
  if (!chartRef.value || chartData.value.length === 0) return
  const chart = echarts.init(chartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: '#ffffff',
      borderColor: '#b9d4c0',
      borderWidth: 1,
      textStyle: { color: '#183229' }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#4d655b' }
    },
    series: [
      {
        name: '分类',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#ffffff',
          borderWidth: 2
        },
        label: {
          show: true,
          color: '#4d655b',
          fontSize: 12
        },
        emphasis: {
          scale: true,
          scaleSize: 15,
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(47, 125, 85, 0.4)'
          },
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#183229'
          }
        },
        labelLine: {
          lineStyle: { color: '#d7e3d9' }
        },
        data: chartData.value,
      },
    ],
  }
  chart.setOption(option)
}
</script>

<style scoped>
.classification-page {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header h3 {
  margin: 0;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.confidence {
  color: var(--text-muted);
  font-size: 14px;
}
</style>
