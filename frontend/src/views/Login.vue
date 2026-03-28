<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="background-decoration">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 主内容 -->
    <div class="login-wrapper">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="logo-container">
            <div class="logo-icon">
              <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="24" cy="24" r="22" stroke="url(#gradient1)" stroke-width="2" fill="none"/>
                <path d="M24 12C17.373 12 12 17.373 12 24C12 30.627 17.373 36 24 36" stroke="url(#gradient1)" stroke-width="2" stroke-linecap="round"/>
                <circle cx="24" cy="24" r="4" fill="url(#gradient1)"/>
                <path d="M30 18L34 14M34 14L38 18M34 14V22" stroke="url(#gradient1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <defs>
                  <linearGradient id="gradient1" x1="12" y1="12" x2="36" y2="36">
                    <stop stop-color="#fb923c"/>
                    <stop offset="1" stop-color="#f97316"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h1 class="brand-title">
              <span class="title-main">SilentElder</span>
              <span class="title-accent">Sense</span>
            </h1>
          </div>

          <p class="brand-tagline">智能守护 · 温暖相伴</p>

          <div class="feature-list">
            <div class="feature-item">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
              <div class="feature-text">
                <span class="feature-title">隐私保护</span>
                <span class="feature-desc">本地AI识别，数据不出户</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
              </div>
              <div class="feature-text">
                <span class="feature-title">实时监测</span>
                <span class="feature-desc">7x24小时智能看护</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon warning">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
              </div>
              <div class="feature-text">
                <span class="feature-title">即时告警</span>
                <span class="feature-desc">异常行为秒级响应</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-section">
        <div class="form-card">
          <div class="form-header">
            <h2 class="form-title">{{ isRegisterMode ? '创建账户' : '欢迎回来' }}</h2>
            <p class="form-subtitle">
              {{ isRegisterMode ? '开始您的智能守护之旅' : '登录以继续使用系统' }}
            </p>
          </div>

          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            class="login-form"
            @submit.prevent="handleSubmit"
          >
            <div class="form-group">
              <label class="form-label">用户名</label>
              <el-form-item prop="username">
                <el-input
                  v-model="formData.username"
                  placeholder="请输入用户名"
                  size="large"
                  :prefix-icon="User"
                />
              </el-form-item>
            </div>

            <div class="form-group">
              <label class="form-label">密码</label>
              <el-form-item prop="password">
                <el-input
                  v-model="formData.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  @keyup.enter="handleSubmit"
                />
              </el-form-item>
            </div>

            <transition name="slide-up" mode="out-in">
              <div v-if="isRegisterMode" class="form-group">
                <label class="form-label">邮箱</label>
                <el-form-item prop="email">
                  <el-input
                    v-model="formData.email"
                    placeholder="请输入邮箱"
                    size="large"
                    :prefix-icon="Message"
                  />
                </el-form-item>
              </div>
            </transition>

            <div class="form-actions">
              <el-button
                type="primary"
                size="large"
                class="submit-button"
                :loading="loading"
                @click="handleSubmit"
              >
                <span class="button-content">
                  <span class="button-text">{{ isRegisterMode ? '创建账户' : '登录系统' }}</span>
                  <span class="button-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                  </span>
                </span>
              </el-button>
            </div>
          </el-form>

          <div class="form-footer">
            <div class="divider">
              <span class="divider-text">或</span>
            </div>

            <button class="mode-switch" @click="toggleMode">
              <span class="switch-text">
                {{ isRegisterMode ? '已有账号？' : '还没有账号？' }}
              </span>
              <span class="switch-action">
                {{ isRegisterMode ? '立即登录' : '立即注册' }}
              </span>
            </button>
          </div>
        </div>

        <!-- 底部版权 -->
        <div class="copyright">
          <p>© 2024 SilentElderSense. 保留所有权利。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login, register } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const isRegisterMode = ref(false)

const formData = reactive({
  username: '',
  password: '',
  email: ''
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度为 6-32 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isRegisterMode.value) {
          await register({
            username: formData.username,
            password: formData.password,
            email: formData.email
          })
          ElMessage({
            message: '注册成功，请登录',
            type: 'success',
            customClass: 'custom-message'
          })
          isRegisterMode.value = false
        } else {
          await authStore.login({
            username: formData.username,
            password: formData.password
          })
          ElMessage({
            message: '登录成功，欢迎回来',
            type: 'success',
            customClass: 'custom-message'
          })
          router.push('/dashboard')
        }
      } catch (error) {
        ElMessage({
          message: error.message || '操作失败，请重试',
          type: 'error',
          customClass: 'custom-message'
        })
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* ============================================
   登录页面 - 温暖科技感设计
   ============================================ */

.login-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d12 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.3) 0%, transparent 70%);
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, transparent 70%);
  bottom: -150px;
  right: -150px;
  animation-delay: -7s;
}

.orb-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.05);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.95);
  }
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}

/* 主布局 */
.login-wrapper {
  display: flex;
  width: 100%;
  max-width: 1200px;
  min-height: 600px;
  margin: 20px;
  position: relative;
  z-index: 1;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
}

.brand-content {
  max-width: 400px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.9;
  }
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.brand-title {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.title-main {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--neutral-800);
  letter-spacing: -0.02em;
}

.title-accent {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 300;
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-tagline {
  font-size: 18px;
  color: var(--neutral-400);
  margin-bottom: 48px;
  font-weight: 300;
  letter-spacing: 0.05em;
}

/* 特性列表 */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all var(--transition-base);
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateX(8px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border-radius: var(--radius-md);
  color: white;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 24px;
  height: 24px;
}

.feature-icon.success {
  background: linear-gradient(135deg, var(--success-500) 0%, var(--success-600) 100%);
}

.feature-icon.warning {
  background: linear-gradient(135deg, var(--warning-500) 0%, var(--warning-600) 100%);
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-700);
}

.feature-desc {
  font-size: 13px;
  color: var(--neutral-400);
}

/* 右侧表单区域 */
.form-section {
  width: 480px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px 0;
}

.form-card {
  background: rgba(26, 26, 36, 0.8);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-2xl);
  padding: 48px;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--neutral-800);
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 15px;
  color: var(--neutral-400);
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--neutral-500);
}

.form-group :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  padding: 4px 16px;
  height: 52px;
  box-shadow: none;
  transition: all var(--transition-base);
}

.form-group :deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.form-group :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-500);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.15);
}

.form-group :deep(.el-input__inner) {
  color: var(--neutral-800);
  font-size: 15px;
}

.form-group :deep(.el-input__inner::placeholder) {
  color: var(--neutral-400);
}

.form-group :deep(.el-input__prefix) {
  color: var(--neutral-400);
}

.form-group :deep(.el-form-item) {
  margin-bottom: 0;
}

.form-group :deep(.el-form-item__error) {
  padding-top: 6px;
  font-size: 12px;
}

/* 提交按钮 */
.form-actions {
  margin-top: 8px;
}

.submit-button {
  width: 100%;
  height: 56px;
  border-radius: var(--radius-lg);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border: none;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-base);
}

.submit-button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.submit-button:hover::before {
  opacity: 1;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow:
    0 10px 40px rgba(249, 115, 22, 0.4),
    0 0 0 1px rgba(249, 115, 22, 0.2);
}

.submit-button:active {
  transform: translateY(0);
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.button-text {
  font-weight: 600;
}

.button-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  transition: transform var(--transition-base);
}

.button-icon svg {
  width: 100%;
  height: 100%;
}

.submit-button:hover .button-icon {
  transform: translateX(4px);
}

/* 表单底部 */
.form-footer {
  margin-top: 32px;
}

.divider {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.divider-text {
  padding: 0 16px;
  font-size: 13px;
  color: var(--neutral-400);
}

.mode-switch {
  width: 100%;
  padding: 16px;
  background: transparent;
  border: 1px dashed rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.mode-switch:hover {
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.03);
}

.switch-text {
  font-size: 14px;
  color: var(--neutral-400);
}

.switch-action {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-400);
  transition: color var(--transition-base);
}

.mode-switch:hover .switch-action {
  color: var(--primary-300);
}

/* 版权信息 */
.copyright {
  text-align: center;
  margin-top: 32px;
}

.copyright p {
  font-size: 13px;
  color: var(--neutral-400);
}

/* 过渡动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all var(--transition-slow);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-wrapper {
    flex-direction: column;
    max-width: 480px;
  }

  .brand-section {
    padding: 40px 0;
  }

  .brand-content {
    text-align: center;
  }

  .logo-container {
    justify-content: center;
  }

  .feature-list {
    display: none;
  }

  .form-section {
    width: 100%;
    padding: 0;
  }
}

@media (max-width: 480px) {
  .form-card {
    padding: 32px 24px;
  }

  .form-title {
    font-size: 24px;
  }
}
</style>
