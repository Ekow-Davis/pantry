<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, UserCheck, UserX, Trash2, ShieldCheck, User } from 'lucide-vue-next'
import { useAdminStore } from '@/stores/admin'
import { useNotificationsStore } from '@/stores/notifications'

const admin  = useAdminStore()
const notify = useNotificationsStore()
const search = ref('')

onMounted(() => admin.fetchUsers())

const filtered = () => admin.users.filter(u =>
  u.username.toLowerCase().includes(search.value.toLowerCase()) ||
  u.email.toLowerCase().includes(search.value.toLowerCase())
)

async function deactivate(user: any) {
  try {
    await admin.updateUser(user.id, { is_active: false })
    notify.success(`${user.username} deactivated.`)
  } catch { notify.error('Failed to deactivate user.') }
}

async function reactivate(user: any) {
  try {
    await admin.updateUser(user.id, { is_active: true })
    notify.success(`${user.username} reactivated.`)
  } catch { notify.error('Failed to reactivate user.') }
}

async function makeAdmin(user: any) {
  try {
    await admin.updateUser(user.id, { role: 'admin' })
    notify.success(`${user.username} is now an admin.`)
  } catch { notify.error('Failed to update role.') }
}

async function remove(user: any) {
  if (!confirm(`Delete ${user.username}? This cannot be undone.`)) return
  try {
    await admin.deleteUser(user.id)
    notify.success('User deleted.')
  } catch { notify.error('Failed to delete user.') }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6 animate-fade-up">
      <div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Users</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">{{ admin.users.length }} total accounts</p>
      </div>
    </div>

    <div class="relative mb-4 animate-fade-up delay-100">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
      <input v-model="search" class="input !pl-10" placeholder="Search by name or email..." />
    </div>

    <div v-if="admin.loading" class="flex flex-col gap-3">
      <div v-for="i in 5" :key="i" class="skeleton h-16 rounded-xl"></div>
    </div>

    <div v-else class="flex flex-col gap-2 animate-fade-up delay-200">
      <div
        v-for="user in filtered()"
        :key="user.id"
        class="card p-4 flex items-center gap-4"
        :style="!user.is_active ? 'opacity:0.6' : ''"
      >
        <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0"
          :style="user.role === 'admin' ? 'background:var(--color-danger-soft); color:var(--color-danger)' : 'background:var(--color-primary-soft); color:var(--color-primary)'">
          {{ user.username.charAt(0).toUpperCase() }}
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <p class="font-bold text-sm truncate" style="color:var(--color-text)">{{ user.username }}</p>
            <span v-if="user.role === 'admin'" class="badge badge-danger text-[10px]">Admin</span>
            <span v-if="!user.is_active"       class="badge badge-warning text-[10px]">Inactive</span>
          </div>
          <p class="text-xs truncate" style="color:var(--color-text-muted)">{{ user.email }}</p>
        </div>

        <div class="flex items-center gap-1 flex-shrink-0">
          <button v-if="user.role !== 'admin'" @click="makeAdmin(user)" title="Make admin"
            class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:bg-[var(--color-danger-soft)]"
            style="color:var(--color-danger)">
            <ShieldCheck class="w-4 h-4" />
          </button>
          <button v-if="user.is_active" @click="deactivate(user)" title="Deactivate"
            class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:bg-[var(--color-warning-soft)]"
            style="color:var(--color-warning)">
            <UserX class="w-4 h-4" />
          </button>
          <button v-else @click="reactivate(user)" title="Reactivate"
            class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:bg-[var(--color-success-soft)]"
            style="color:var(--color-success)">
            <UserCheck class="w-4 h-4" />
          </button>
          <button @click="remove(user)" title="Delete user"
            class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:bg-[var(--color-danger-soft)]"
            style="color:var(--color-danger)">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div v-if="!admin.loading && !filtered().length" class="card p-10 text-center mt-4">
      <div class="text-5xl mb-3">👤</div>
      <p class="font-semibold">No users found</p>
    </div>
  </div>
</template>
