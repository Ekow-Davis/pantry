<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CheckCircle, XCircle, Clock } from 'lucide-vue-next'
import { useAdminStore } from '@/stores/admin'
import { useNotificationsStore } from '@/stores/notifications'

const admin   = useAdminStore()
const notify  = useNotificationsStore()
const filter  = ref('pending')
const rejectionReason = ref('')
const rejectingId = ref<string | null>(null)

onMounted(() => admin.fetchContributions('pending'))

async function approve(id: string) {
  try {
    await admin.reviewContribution(id, 'approved')
    notify.success('Contribution approved — meal is now live!')
  } catch { notify.error('Failed to approve.') }
}

function startReject(id: string) {
  rejectingId.value = id
  rejectionReason.value = ''
}

async function confirmReject(id: string) {
  if (!rejectionReason.value.trim()) {
    notify.warning('Please provide a rejection reason.')
    return
  }
  try {
    await admin.reviewContribution(id, 'rejected', rejectionReason.value)
    notify.info('Contribution rejected.')
    rejectingId.value = null
  } catch { notify.error('Failed to reject.') }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6 animate-fade-up">
      <div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Contributions</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">Review user-submitted meals</p>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="flex gap-2 mb-4 animate-fade-up delay-100">
      <button v-for="f in ['pending', 'approved', 'rejected']" :key="f"
        class="px-4 py-2 rounded-full text-sm font-semibold transition-all capitalize"
        :style="filter === f ? 'background:var(--color-danger); color:#fff' : 'background:var(--color-surface); color:var(--color-text-muted); border:1px solid var(--color-border)'"
        @click="filter = f; admin.fetchContributions(f)">
        {{ f }}
      </button>
    </div>

    <div v-if="admin.loading" class="flex flex-col gap-3">
      <div v-for="i in 4" :key="i" class="skeleton h-28 rounded-xl"></div>
    </div>

    <div v-else-if="admin.contributions.length" class="flex flex-col gap-3 animate-fade-up delay-200">
      <div v-for="c in admin.contributions" :key="c.id" class="card p-5">
        <div class="flex items-start gap-4 mb-4">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
            style="background:var(--color-primary-soft)">🍲</div>
          <div class="flex-1 min-w-0">
            <p class="font-bold" style="color:var(--color-text)">{{ c.meal?.name || 'Unnamed meal' }}</p>
            <p class="text-xs" style="color:var(--color-text-muted)">Submitted {{ formatDate(c.submitted_at) }} by user {{ c.user_id.slice(0, 8) }}...</p>
            <p v-if="c.rejection_reason" class="text-xs mt-1 px-2 py-1 rounded-lg inline-block" style="background:var(--color-danger-soft); color:var(--color-danger)">
              Reason: {{ c.rejection_reason }}
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span class="badge" :class="c.status === 'pending' ? 'badge-warning' : c.status === 'approved' ? 'badge-success' : 'badge-danger'">
              {{ c.status }}
            </span>
          </div>
        </div>

        <!-- Actions for pending -->
        <div v-if="c.status === 'pending'" class="flex flex-col gap-2">
          <div v-if="rejectingId === c.id" class="flex gap-2">
            <input v-model="rejectionReason" class="input flex-1 !py-2" placeholder="Reason for rejection..." />
            <button class="btn-primary !py-2 !px-4 text-sm" style="background:var(--color-danger)" @click="confirmReject(c.id)">Confirm</button>
            <button class="btn-surface !py-2 !px-3 text-sm" @click="rejectingId = null">Cancel</button>
          </div>
          <div v-else class="flex gap-2">
            <button class="btn-primary !py-2 !px-4 text-sm flex-1 justify-center" @click="approve(c.id)">
              <CheckCircle class="w-4 h-4" /> Approve
            </button>
            <button class="btn-surface !py-2 !px-4 text-sm" style="color:var(--color-danger); border-color:var(--color-danger)" @click="startReject(c.id)">
              <XCircle class="w-4 h-4" /> Reject
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card p-12 text-center">
      <div class="text-5xl mb-4">
        <CheckCircle v-if="filter === 'approved'" class="w-12 h-12 mx-auto" style="color:var(--color-success)" />
        <Clock v-else-if="filter === 'pending'" class="w-12 h-12 mx-auto" style="color:var(--color-warning)" />
        <XCircle v-else class="w-12 h-12 mx-auto" style="color:var(--color-danger)" />
      </div>
      <p class="font-bold text-lg mb-1" style="font-family:var(--font-display)">No {{ filter }} contributions</p>
      <p class="text-sm" style="color:var(--color-text-muted)">
        {{ filter === 'pending' ? 'All caught up! No submissions waiting for review.' : `No ${filter} contributions yet.` }}
      </p>
    </div>
  </div>
</template>
