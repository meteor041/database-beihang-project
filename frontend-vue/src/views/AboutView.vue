<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card elevation="2" class="pa-6">
          <v-card-title class="text-h4 font-weight-bold text-center mb-6">
            关于校内二手交易平台
          </v-card-title>

          <v-card-text>
            <p class="text-h6 mb-6 text-center text-grey-darken-1">
              一个安全、便捷的校园二手物品交易平台
            </p>

            <v-divider class="my-6"></v-divider>

            <div class="text-body-1">
              <h3 class="text-h5 font-weight-bold mb-4">项目简介</h3>
              <p class="mb-4">
                本平台是为北航学生打造的二手物品交易系统，旨在为校内师生提供一个安全、便捷的二手物品交易渠道，
                促进资源的合理利用和循环，倡导环保理念。
              </p>

              <h3 class="text-h5 font-weight-bold mb-4 mt-6">核心功能</h3>
              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title>实名认证与信用评级系统</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title>商品发布与浏览</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title>订单管理与交易流程</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title>即时消息通信</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title>收藏与地址管理</v-list-item-title>
                </v-list-item>
              </v-list>

              <h3 class="text-h5 font-weight-bold mb-4 mt-6">技术栈</h3>
              <v-row>
                <v-col cols="12" md="6">
                  <v-card variant="outlined">
                    <v-card-title class="text-subtitle-1">前端技术</v-card-title>
                    <v-card-text>
                      <v-chip class="ma-1" size="small">Vue 3</v-chip>
                      <v-chip class="ma-1" size="small">TypeScript</v-chip>
                      <v-chip class="ma-1" size="small">Vuetify 3</v-chip>
                      <v-chip class="ma-1" size="small">Pinia</v-chip>
                      <v-chip class="ma-1" size="small">Vite</v-chip>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="6">
                  <v-card variant="outlined">
                    <v-card-title class="text-subtitle-1">后端技术</v-card-title>
                    <v-card-text>
                      <v-chip class="ma-1" size="small">Python Flask</v-chip>
                      <v-chip class="ma-1" size="small">GaussDB</v-chip>
                      <v-chip class="ma-1" size="small">原生SQL</v-chip>
                      <v-chip class="ma-1" size="small">PyMySQL</v-chip>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>

              <h3 class="text-h5 font-weight-bold mb-4 mt-6">开发团队</h3>
              <p class="mb-2">本项目由北航数据库系统课程小组开发</p>
              <p class="text-grey-darken-1">团队成员：肖一涵、刘鑫宇</p>

              <v-divider class="my-6"></v-divider>

              <div class="text-center">
                <p class="text-caption text-grey">© 2024-2025 校内二手物品交易平台</p>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
// AboutView - 关于页面
</script>

<style scoped>
.v-card {
  min-height: 60vh;
}
</style>
