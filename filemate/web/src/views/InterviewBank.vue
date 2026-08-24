<template>
  <div class="interview-bank-page">
    <header class="page-head">
      <div>
        <p class="eyebrow">INTERVIEW QUESTION BANK</p>
        <h1>面试题库管理</h1>
        <p>按场景和难度维护模拟面试题目，题目会参与面试创建时的自动选题。</p>
      </div>
    </header>

    <section class="bank-toolbar">
      <el-select v-model="filters.scenario" placeholder="全部场景" clearable @change="load">
        <el-option v-for="item in scenarios" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="filters.difficulty" placeholder="全部难度" clearable @change="load">
        <el-option v-for="item in difficulties" :key="item" :label="item" :value="item" />
      </el-select>
      <el-button type="primary" @click="openCreate">新增题目</el-button>
    </section>

    <el-table :data="questions" v-loading="loading" class="bank-table">
      <el-table-column prop="scenario" label="场景" width="140" />
      <el-table-column prop="difficulty" label="难度" width="110" />
      <el-table-column prop="text" label="题目" min-width="280" show-overflow-tooltip />
      <el-table-column label="启用" width="90">
        <template #default="{ row }">
          <el-switch v-model="row.enabled" :active-value="1" :inactive-value="0" @change="toggle(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑题目' : '新增题目'" width="min(560px, calc(100vw - 32px))">
      <el-form label-position="top">
        <el-form-item label="场景">
          <el-select v-model="form.scenario" style="width: 100%">
            <el-option v-for="item in scenarios" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="form.difficulty" style="width: 100%">
            <el-option v-for="item in difficulties" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容">
          <el-input v-model="form.text" type="textarea" :rows="4" placeholder="输入面试题目" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!form.text.trim()" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createInterviewQuestion,
  deleteInterviewQuestion,
  getInterviewQuestions,
  updateInterviewQuestion,
  type InterviewQuestion
} from '../services/api'

const scenarios = ['求职面试', '竞赛答辩', '保研复试']
const difficulties = ['入门', '标准', '压力面']
const filters = reactive({ scenario: '', difficulty: '' })
const questions = ref<InterviewQuestion[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref('')
const form = reactive({ scenario: '求职面试', difficulty: '入门', text: '', enabled: true })

async function load(): Promise<void> {
  loading.value = true
  try {
    questions.value = await getInterviewQuestions({
      scenario: filters.scenario || undefined,
      difficulty: filters.difficulty || undefined
    })
  } catch (error: any) {
    ElMessage.error(error.message || '加载题库失败')
  } finally {
    loading.value = false
  }
}

function openCreate(): void {
  editingId.value = ''
  Object.assign(form, { scenario: '求职面试', difficulty: '入门', text: '', enabled: true })
  dialogVisible.value = true
}

function openEdit(row: InterviewQuestion): void {
  editingId.value = row.id
  Object.assign(form, {
    scenario: row.scenario,
    difficulty: row.difficulty,
    text: row.text,
    enabled: Boolean(row.enabled)
  })
  dialogVisible.value = true
}

async function save(): Promise<void> {
  const payload = {
    scenario: form.scenario,
    difficulty: form.difficulty,
    text: form.text.trim(),
    enabled: form.enabled
  }
  try {
    if (editingId.value) {
      await updateInterviewQuestion(editingId.value, payload)
      ElMessage.success('题目已更新')
    } else {
      await createInterviewQuestion(payload)
      ElMessage.success('题目已新增')
    }
    dialogVisible.value = false
    await load()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

async function toggle(row: InterviewQuestion): Promise<void> {
  try {
    await updateInterviewQuestion(row.id, { enabled: Boolean(row.enabled) })
    ElMessage.success(row.enabled ? '已启用' : '已停用')
  } catch (error: any) {
    ElMessage.error(error.message || '状态更新失败')
    await load()
  }
}

async function remove(row: InterviewQuestion): Promise<void> {
  try {
    await deleteInterviewQuestion(row.id)
    ElMessage.success('题目已删除')
    await load()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.interview-bank-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px;
  color: var(--text-primary);
}
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  margin-bottom: 24px;
}
.eyebrow {
  margin: 0;
  color: var(--accent);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.15em;
}
.page-head h1 {
  font-size: 32px;
  margin: 6px 0;
}
.page-head p {
  margin: 0;
  color: var(--text-secondary);
}
.bank-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 18px;
}
.bank-toolbar .el-select {
  width: 180px;
}
.bank-table {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
}
</style>
