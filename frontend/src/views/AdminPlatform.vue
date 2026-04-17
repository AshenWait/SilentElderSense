<template>
  <div class="admin-platform">
    <!-- 标签页 -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: activeTab === 'platform-users' }" @click="activeTab = 'platform-users'">平台用户</button>
      <button class="tab-btn" :class="{ active: activeTab === 'groups' }" @click="activeTab = 'groups'">社区组</button>
      <button class="tab-btn" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">用户管理</button>
    </div>

    <!-- 平台用户 -->
    <section v-if="activeTab === 'platform-users'">
      <div class="section-header">
        <h3>平台用户管理</h3>
        <button class="btn-primary" @click="showCreatePlatformUser = true">创建平台用户</button>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>组织名称</th>
              <th>联系人</th>
              <th>联系电话</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in platformUsers" :key="u.id">
              <td>{{ u.id }}</td>
              <td>{{ u.username }}</td>
              <td>{{ u.org_name || '-' }}</td>
              <td>{{ u.org_contact_name || '-' }}</td>
              <td>{{ u.org_contact_phone || '-' }}</td>
              <td>{{ formatDate(u.created_at) }}</td>
              <td>
                <div class="action-btns">
                  <button class="action-btn secondary" @click="editPlatformUser(u)">编辑</button>
                  <button class="action-btn danger" @click="handleResetPassword(u)">重设密码</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="platformUsers.length === 0" class="empty-state">暂无平台用户</div>
      </div>
    </section>

    <!-- 社区组 -->
    <section v-if="activeTab === 'groups'">
      <div class="section-header">
        <h3>社区组管理</h3>
        <button class="btn-primary" @click="openCreateGroup">创建社区组</button>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>所属平台</th>
              <th>地址</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in groups" :key="g.id">
              <td>{{ g.id }}</td>
              <td>{{ g.name }}</td>
              <td>{{ g.platform_org_name || '-' }}</td>
              <td>{{ g.address || '-' }}</td>
              <td>
                <span class="status-badge" :class="g.status === 'active' ? 'active' : 'suspended'">
                  <span class="status-dot"></span>
                  {{ g.status === 'active' ? '运营中' : '已挂起' }}
                </span>
              </td>
              <td>
                <div class="action-btns">
                  <button class="action-btn secondary" @click="editGroup(g)">编辑</button>
                  <button class="action-btn danger" @click="handleSuspendGroup(g)">
                    {{ g.status === 'active' ? '挂起' : '恢复' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="groups.length === 0" class="empty-state">暂无社区组</div>
      </div>
    </section>

    <!-- 用户管理 -->
    <section v-if="activeTab === 'users'">
      <div class="section-header">
        <h3>所有用户</h3>
        <button class="btn-primary" @click="openCreateUser">创建用户</button>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>社区组</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in allUsers" :key="u.id">
              <td>{{ u.id }}</td>
              <td>{{ u.username }}</td>
              <td>{{ u.email || '-' }}</td>
              <td>
                <span class="status-badge" :class="roleBadgeClass(u.role)">
                  {{ roleLabel(u.role) }}
                </span>
              </td>
              <td>{{ u.community_group_name || '-' }}</td>
              <td>{{ formatDate(u.created_at) }}</td>
              <td>
                <div class="action-btns">
                  <button v-if="u.role === 'user' || u.role === 'platform'" class="action-btn secondary" @click="u.role === 'platform' ? editPlatformUser(u) : editUser(u)">编辑</button>
                  <button class="action-btn danger" @click="handleResetPassword(u)">重设密码</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="allUsers.length === 0" class="empty-state">暂无用户</div>
      </div>
    </section>

    <!-- 创建平台用户弹窗 -->
    <div v-if="showCreatePlatformUser" class="modal-overlay" @click.self="showCreatePlatformUser = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>创建平台用户</h3>
          <button class="modal-close" @click="showCreatePlatformUser = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>用户名</label>
            <input v-model="newPlatformUser.username" placeholder="输入用户名" class="form-input" />
          </div>
          <div class="form-item">
            <label>密码</label>
            <input v-model="newPlatformUser.password" type="password" placeholder="输入密码" class="form-input" />
          </div>
          <div class="form-item">
            <label>邮箱（可选）</label>
            <input v-model="newPlatformUser.email" placeholder="输入邮箱" class="form-input" />
          </div>
          <div class="form-item">
            <label>组织名称</label>
            <input v-model="newPlatformUser.org_name" placeholder="输入组织名称" class="form-input" />
          </div>
          <div class="form-item">
            <label>组织描述</label>
            <textarea v-model="newPlatformUser.org_description" placeholder="输入描述" class="form-input" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>联系人</label>
            <input v-model="newPlatformUser.org_contact_name" placeholder="输入联系人" class="form-input" />
          </div>
          <div class="form-item">
            <label>联系电话</label>
            <input v-model="newPlatformUser.org_contact_phone" placeholder="输入联系电话" class="form-input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreatePlatformUser = false">取消</button>
          <button class="btn-primary" @click="savePlatformUser" :disabled="!newPlatformUser.username || !newPlatformUser.password">创建</button>
        </div>
      </div>
    </div>

    <!-- 编辑平台用户弹窗 -->
    <div v-if="showEditPlatformUser" class="modal-overlay" @click.self="showEditPlatformUser = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑平台用户</h3>
          <button class="modal-close" @click="showEditPlatformUser = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>组织名称</label>
            <input v-model="editForm.org_name" placeholder="输入组织名称" class="form-input" />
          </div>
          <div class="form-item">
            <label>组织描述</label>
            <textarea v-model="editForm.org_description" placeholder="输入描述" class="form-input" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>联系人</label>
            <input v-model="editForm.org_contact_name" placeholder="输入联系人" class="form-input" />
          </div>
          <div class="form-item">
            <label>联系电话</label>
            <input v-model="editForm.org_contact_phone" placeholder="输入联系电话" class="form-input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditPlatformUser = false">取消</button>
          <button class="btn-primary" @click="saveEditPlatformUser">保存</button>
        </div>
      </div>
    </div>

    <!-- 重设密码弹窗 -->
    <div v-if="showResetPassword" class="modal-overlay" @click.self="showResetPassword = false">
      <div class="modal-content" style="width: 360px">
        <div class="modal-header">
          <h3>重设密码</h3>
          <button class="modal-close" @click="showResetPassword = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="reset-user-info">用户：{{ resetTarget?.username }}</p>
          <div class="form-item">
            <label>新密码</label>
            <input v-model="newPassword" type="password" placeholder="输入新密码" class="form-input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showResetPassword = false">取消</button>
          <button class="btn-primary" @click="confirmResetPassword" :disabled="!newPassword || newPassword.length < 4">确认重设</button>
        </div>
      </div>
    </div>

    <!-- 创建社区组弹窗 -->
    <div v-if="showCreateGroup" class="modal-overlay" @click.self="showCreateGroup = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingGroup ? '编辑社区组' : '创建社区组' }}</h3>
          <button class="modal-close" @click="showCreateGroup = false; editingGroup = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item" v-if="!editingGroup">
            <label>所属平台用户</label>
            <select v-model="groupForm.platform_user_id" class="form-input">
              <option value="">请选择平台用户</option>
              <option v-for="u in platformUsers" :key="u.id" :value="u.id">{{ u.org_name || u.username }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>社区组名称</label>
            <input v-model="groupForm.name" placeholder="输入社区组名称" class="form-input" />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="groupForm.description" placeholder="输入描述" class="form-input" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>地址</label>
            <input v-model="groupForm.address" placeholder="输入地址" class="form-input" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreateGroup = false; editingGroup = null">取消</button>
          <button class="btn-primary" @click="saveGroup">保存</button>
        </div>
      </div>
    </div>

    <!-- 创建用户弹窗 -->
    <div v-if="showCreateUser" class="modal-overlay" @click.self="showCreateUser = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingUser ? '编辑用户' : '创建用户' }}</h3>
          <button class="modal-close" @click="closeUserModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item" v-if="!editingUser">
            <label>用户名</label>
            <input v-model="newUser.username" placeholder="输入用户名" class="form-input" />
          </div>
          <div class="form-item" v-if="!editingUser">
            <label>密码</label>
            <input v-model="newUser.password" type="password" placeholder="输入密码（至少4位）" class="form-input" />
          </div>
          <div class="form-item">
            <label>邮箱（可选）</label>
            <input v-model="newUser.email" placeholder="输入邮箱" class="form-input" />
          </div>
          <div class="form-item">
            <label>所属平台用户</label>
            <select v-model="selectedUserPlatformId" @change="loadUserGroups" class="form-input">
              <option value="">无</option>
              <option v-for="p in platformUsers" :key="p.id" :value="p.id">
                {{ p.org_name || p.username }}
              </option>
            </select>
          </div>
          <div class="form-item" v-if="userGroups.length > 0">
            <label>社区组（可选）</label>
            <select v-model="newUser.community_group_id" class="form-input">
              <option :value="null">无</option>
              <option v-for="g in userGroups" :key="g.id" :value="g.id">
                {{ g.name }}
              </option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUserModal">取消</button>
          <button class="btn-primary" @click="saveUser" :disabled="!editingUser && (!newUser.username || !newUser.password)">
            {{ editingUser ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  listPlatformUsers, updatePlatformUser, listAllUsers, adminResetPassword,
  createGroup, listGroups, updateGroup, suspendGroup,
  adminCreateUser, adminUpdateUser,
} from '@/api/platform'
import { createPlatformUser as createPlatformUserApi } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('platform-users')

// 平台用户
const platformUsers = ref([])
const showCreatePlatformUser = ref(false)
const showEditPlatformUser = ref(false)
const newPlatformUser = ref({ username: '', password: '', email: '', org_name: '', org_description: '', org_contact_name: '', org_contact_phone: '' })
const editForm = ref({ org_name: '', org_description: '', org_contact_name: '', org_contact_phone: '' })
const editingUserId = ref(null)

// 社区组
const groups = ref([])
const selectedPlatformUserId = ref('')
const showCreateGroup = ref(false)
const editingGroup = ref(null)
const groupForm = ref({ name: '', description: '', address: '', platform_user_id: '' })

// 用户管理
const allUsers = ref([])
const showCreateUser = ref(false)
const editingUser = ref(null)
const newUser = ref({ username: '', password: '', email: '', community_group_id: null })
const selectedUserPlatformId = ref('')
const userGroups = ref([])

// 重设密码
const showResetPassword = ref(false)
const resetTarget = ref(null)
const newPassword = ref('')

// 过滤后的用户列表
const filteredUsers = computed(() => {
  if (!filterPlatformUserId.value) return allUsers.value
  return allUsers.value.filter(u => u.platform_user_id === filterPlatformUserId.value)
})

async function loadPlatformUsers() {
  try {
    const res = await listPlatformUsers()
    platformUsers.value = Array.isArray(res.data) ? res.data : res
    await loadGroups() // 平台用户加载完后加载社区组
  } catch (e) { console.error(e) }
}

async function loadAllUsers() {
  try {
    const res = await listAllUsers()
    allUsers.value = Array.isArray(res.data) ? res.data : res
  } catch (e) { console.error(e) }
}

async function savePlatformUser() {
  try {
    await createPlatformUserApi(newPlatformUser.value)
    ElMessage.success('平台用户创建成功')
    newPlatformUser.value = { username: '', password: '', email: '', org_name: '', org_description: '', org_contact_name: '', org_contact_phone: '' }
    showCreatePlatformUser.value = false
    loadPlatformUsers()
    loadAllUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '创建失败')
  }
}

function editPlatformUser(u) {
  editingUserId.value = u.id
  editForm.value = {
    org_name: u.org_name || '',
    org_description: u.org_description || '',
    org_contact_name: u.org_contact_name || '',
    org_contact_phone: u.org_contact_phone || '',
  }
  showEditPlatformUser.value = true
}

async function saveEditPlatformUser() {
  try {
    await updatePlatformUser(editingUserId.value, editForm.value)
    ElMessage.success('更新成功')
    showEditPlatformUser.value = false
    loadPlatformUsers()
    loadAllUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '更新失败')
  }
}

function handleResetPassword(u) {
  resetTarget.value = u
  newPassword.value = ''
  showResetPassword.value = true
}

async function confirmResetPassword() {
  try {
    await adminResetPassword({ user_id: resetTarget.value.id, new_password: newPassword.value })
    ElMessage.success(`${resetTarget.value.username} 密码已重置`)
    showResetPassword.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '重设失败')
  }
}

function openCreateGroup() {
  editingGroup.value = null
  groupForm.value = { name: '', description: '', address: '', platform_user_id: '' }
  showCreateGroup.value = true
}

async function loadGroups() {
  try {
    if (platformUsers.value.length === 0) {
      groups.value = []
      return
    }
    const promises = platformUsers.value.map(u => listGroups(u.id))
    const results = await Promise.all(promises)
    let allGroups = []
    results.forEach((res, index) => {
      let gs = Array.isArray(res.data) ? res.data : res
      gs.forEach(g => {
        g.platform_org_name = platformUsers.value[index].org_name || platformUsers.value[index].username
        allGroups.push(g)
      })
    })
    groups.value = allGroups
  } catch (e) {
    console.error('加载社区组失败', e)
  }
}

async function saveGroup() {
  try {
    if (editingGroup.value) {
      await updateGroup(editingGroup.value.id, groupForm.value)
      ElMessage.success('更新成功')
    } else {
      if (!groupForm.value.platform_user_id) {
        ElMessage.warning('请选择所属的平台用户')
        return
      }
      await createGroup(groupForm.value.platform_user_id, groupForm.value)
      ElMessage.success('创建成功')
    }
    showCreateGroup.value = false
    editingGroup.value = null
    groupForm.value = { name: '', description: '', address: '', platform_user_id: '' }
    loadGroups()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

function editGroup(g) {
  editingGroup.value = g
  groupForm.value = { name: g.name, description: g.description || '', address: g.address || '', platform_user_id: g.platform_user_id || '' }
  showCreateGroup.value = true
}

async function handleSuspendGroup(g) {
  try {
    if (g.status === 'active') {
      await suspendGroup(g.id)
      ElMessage.success('已挂起')
    } else {
      await updateGroup(g.id, { status: 'active' })
      ElMessage.success('已恢复')
    }
    loadGroups()
  } catch (e) { ElMessage.error('操作失败') }
}

// 用户管理相关
function openCreateUser() {
  editingUser.value = null
  newUser.value = { username: '', password: '', email: '', community_group_id: null }
  selectedUserPlatformId.value = ''
  userGroups.value = []
  showCreateUser.value = true
}

function closeUserModal() {
  showCreateUser.value = false
  editingUser.value = null
  selectedUserPlatformId.value = ''
  userGroups.value = []
}

async function loadUserGroups() {
  newUser.value.community_group_id = null
  if (!selectedUserPlatformId.value) { userGroups.value = []; return }
  try {
    const res = await listGroups(selectedUserPlatformId.value)
    userGroups.value = Array.isArray(res.data) ? res.data : res
  } catch (e) { userGroups.value = [] }
}

function editUser(u) {
  editingUser.value = u
  newUser.value = {
    username: u.username,
    email: u.email || '',
    community_group_id: u.community_group_id,
  }
  selectedUserPlatformId.value = ''
  userGroups.value = []
  showCreateUser.value = true
}

async function saveUser() {
  try {
    if (editingUser.value) {
      await adminUpdateUser(editingUser.value.id, {
        email: newUser.value.email,
        community_group_id: newUser.value.community_group_id,
      })
      ElMessage.success('更新成功')
    } else {
      await adminCreateUser(newUser.value)
      ElMessage.success('用户创建成功')
    }
    closeUserModal()
    loadAllUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  }
}

function roleLabel(role) {
  return { admin: '管理员', platform: '平台用户', user: '普通用户' }[role] || role
}

function roleBadgeClass(role) {
  return { admin: 'active', platform: 'platform', user: '' }[role] || ''
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('zh-CN')
}

onMounted(() => { loadPlatformUsers(); loadAllUsers() })
</script>

<style scoped>
.admin-platform {
  max-width: 1200px;
  margin: 0 auto;
}

.tab-bar {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: rgba(26, 26, 36, 0.6);
  border-radius: 12px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #888;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
}

.tab-btn:hover:not(.active) {
  color: #ccc;
  background: rgba(255, 255, 255, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h3 {
  color: #f0f0f5;
  font-size: 16px;
  margin: 0;
}

.btn-primary {
  padding: 8px 20px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #ccc;
  font-size: 14px;
  cursor: pointer;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-select {
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ccc;
  font-size: 13px;
  outline: none;
}

.table-wrapper {
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 12px;
  color: #888;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #ddd;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
}

.status-badge.active { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.status-badge.suspended { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.status-badge.platform { background: rgba(59, 130, 246, 0.15); color: #93c5fd; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.action-btns { display: flex; gap: 6px; }

.action-btn {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  border: none;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #aaa;
}

.action-btn.danger {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.form-card {
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item label {
  font-size: 13px;
  color: #888;
}

.form-input {
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ddd;
  font-size: 14px;
  outline: none;
  resize: vertical;
}

.form-input:focus {
  border-color: rgba(249, 115, 22, 0.5);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.reset-user-info {
  color: #ddd;
  font-size: 14px;
  margin: 0 0 12px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: #1e1e2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  width: 480px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-header h3 {
  color: #f0f0f5;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: #888;
  font-size: 18px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
