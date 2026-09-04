<template>
  <article class="companion-card" :class="[`mood-${mood}`, { compact }]">
    <div class="portrait-shell">
      <div
        class="portrait"
        role="img"
        :aria-label="`FileMate 学习伙伴：${moodLabel}`"
      >
        <img
          :style="portraitStyle"
          :src="expressionsUrl"
          alt=""
          aria-hidden="true"
        />
      </div>
      <span class="mood-chip">{{ moodLabel }}</span>
    </div>
    <div class="companion-copy">
      <p>FILEMATE 学习伙伴</p>
      <h2>{{ title }}</h2>
      <span>{{ message }}</span>
      <small v-if="evidence">{{ evidence }}</small>
      <div v-if="growth" class="growth-progress">
        <div><span>伙伴阶段 · {{ growth.stage }}</span><b>{{ growth.points }} 成长值</b></div>
        <i role="progressbar" :aria-valuenow="growth.progress" aria-valuemin="0" aria-valuemax="100"><em :style="{ width: `${growth.progress}%` }" /></i>
        <p>{{ growth.nextStage ? `距“${growth.nextStage}”还需 ${growth.pointsToNext} 成长值` : '伙伴阶段已全部解锁' }} · 这是互动进度，不是能力分数</p>
      </div>
    </div>
    <router-link v-if="route && actionLabel" class="companion-action" :to="route">
      {{ actionLabel }}
    </router-link>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import expressionsUrl from '../assets/filemate-mascot-expressions.png'
import type { CompanionGrowth, CompanionMood } from '../composables/useCompanion'

const props = withDefaults(defineProps<{
  mood: CompanionMood
  title: string
  message: string
  evidence?: string
  route?: string
  actionLabel?: string
  compact?: boolean
  growth?: CompanionGrowth | null
}>(), {
  evidence: '',
  route: '',
  actionLabel: '',
  compact: false,
  growth: null
})

const moodMap: Record<CompanionMood, { label: string; x: number; y: number }> = {
  happy: { label: '开心', x: 0, y: -52 },
  thinking: { label: '思考', x: -130, y: -52 },
  focused: { label: '专注', x: -260, y: -52 },
  surprised: { label: '惊喜', x: -390, y: -52 },
  shy: { label: '害羞', x: 0, y: -225 },
  frustrated: { label: '再试一次', x: -130, y: -225 },
  encouraging: { label: '陪你复盘', x: -260, y: -225 },
  wink: { label: '干得漂亮', x: -390, y: -225 }
}

const config = computed(() => moodMap[props.mood])
const moodLabel = computed(() => config.value.label)
const portraitStyle = computed(() => ({
  transform: `translate(${config.value.x}px, ${config.value.y}px)`
}))
</script>

<style scoped>
.companion-card {
  position: relative;
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr) auto;
  align-items: center;
  gap: 22px;
  min-height: 178px;
  padding: 22px 24px;
  overflow: hidden;
  border: 1px solid #cbddeb;
  border-radius: 22px;
  background:
    radial-gradient(circle at 12% 14%, rgba(84, 137, 255, .18), transparent 34%),
    linear-gradient(120deg, #f8fbff 0%, #ffffff 52%, #eff9f4 100%);
  box-shadow: 0 16px 40px rgba(35, 78, 111, .09);
}

.companion-card::after {
  position: absolute;
  right: -62px;
  bottom: -92px;
  width: 220px;
  height: 220px;
  border: 28px solid rgba(47, 143, 104, .08);
  border-radius: 50%;
  content: '';
}

.portrait-shell { position: relative; z-index: 1; justify-self: center; }
.portrait {
  position: relative;
  width: 132px;
  height: 132px;
  overflow: hidden;
  border: 4px solid rgba(255, 255, 255, .94);
  border-radius: 36px 36px 48px 48px;
  background: #f5f8ff;
  box-shadow: 0 12px 28px rgba(37, 99, 235, .16);
}
.portrait img {
  position: absolute;
  top: 0;
  left: 0;
  width: 520px;
  max-width: none;
  transition: transform 360ms cubic-bezier(.2, .8, .2, 1);
}
.mood-chip {
  position: absolute;
  right: -10px;
  bottom: -7px;
  padding: 6px 10px;
  border: 2px solid #fff;
  border-radius: 999px;
  background: #2563eb;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  box-shadow: 0 6px 14px rgba(37, 99, 235, .2);
}
.companion-copy { position: relative; z-index: 1; min-width: 0; }
.companion-copy p { margin: 0 0 8px; color: #2563eb; font-size: 11px; font-weight: 800; letter-spacing: .12em; }
.companion-copy h2 { margin: 0 0 8px; color: #132b46; font-size: clamp(19px, 2vw, 25px); line-height: 1.3; }
.companion-copy > span { display: block; color: #526a80; line-height: 1.65; }
.companion-copy small { display: inline-block; margin-top: 10px; padding: 5px 9px; border-radius: 8px; background: rgba(37, 99, 235, .07); color: #48627a; }
.growth-progress { max-width: 600px; margin-top: 13px; }
.growth-progress > div { display: flex; justify-content: space-between; gap: 14px; color: #36566f; font-size: 11px; }
.growth-progress > div b { color: #176f52; }
.growth-progress > i { display: block; height: 6px; margin-top: 6px; overflow: hidden; border-radius: 99px; background: rgba(41, 92, 125, .12); }
.growth-progress > i em { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #2d78e4, #35a17c); transition: width .3s ease; }
.growth-progress > p { margin: 5px 0 0; color: #708595; font-size: 10px; }
.companion-action {
  position: relative;
  z-index: 1;
  display: inline-flex;
  min-height: 42px;
  align-items: center;
  padding: 0 16px;
  border-radius: 11px;
  background: #176f52;
  color: #fff;
  font-weight: 700;
  text-decoration: none;
}
.compact { grid-template-columns: 104px minmax(0, 1fr) auto; min-height: 132px; padding: 16px 20px; }
.compact .portrait { width: 92px; height: 92px; border-radius: 28px 28px 34px 34px; }
.compact .mood-chip { right: -8px; }
.mood-encouraging .mood-chip,
.mood-frustrated .mood-chip { background: #9b5b35; }
.mood-wink .mood-chip,
.mood-happy .mood-chip { background: #18815d; }

@media (prefers-reduced-motion: no-preference) {
  .portrait-shell { animation: companion-breathe 4.8s ease-in-out infinite; }
}
@keyframes companion-breathe { 50% { transform: translateY(-4px); } }
@media (max-width: 720px) {
  .companion-card { grid-template-columns: 104px 1fr; gap: 16px; }
  .portrait { width: 92px; height: 92px; border-radius: 28px; }
  .companion-action { grid-column: 2; justify-self: start; }
}
</style>
