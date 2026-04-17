import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMyCommunities } from '@/api/platform'

export const usePlatformStore = defineStore('platform', () => {
  const communities = ref([])
  const selectedGroupId = ref(null)

  const fetchCommunities = async () => {
    try {
      const res = await getMyCommunities()
      communities.value = Array.isArray(res.data) ? res.data : res
    } catch (e) {
      console.error(e)
    }
  }

  const selectGroup = (groupId) => {
    selectedGroupId.value = groupId
  }

  return { communities, selectedGroupId, fetchCommunities, selectGroup }
})
