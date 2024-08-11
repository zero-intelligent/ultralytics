<template>
  <div class="container">
    <video-player :options="videoOptions" class="video-css"></video-player>
  </div>
</template>
 
<script>
import videoPlayer from './videoPlayer.vue'
export default {
  name: 'videoComponent',
  components: { videoPlayer },
  props: {
    videoSrc: {
      type: String
    }
  },
  data() {
    return {
      videoOptions: {
        //controls配置项决定是否显示默认控件
        controls: true,
        //fluid配置项根据外层css样式大小，自动填充宽高
        fluid: true,
        //sources配置项配置视频播放源
        sources: [
          {
            //播放源
            src: this.videoSrc,
            //视频类型
            type: "video/mp4"
          }
        ]

      }
    }
  }
}
</script>
 
<style scoped>
.container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 视频宽高将由此样式调整 */
.video-css {
  width: 800px;
  height: auto;
}
</style>