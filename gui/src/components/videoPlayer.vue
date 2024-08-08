<template>
    <div class="videoBox">
        <video ref="videoPlayer" class="video-js"></video>
    </div>
</template>
   
<script>
import 'video.js/dist/video-js.css';
export default {
    name: 'videoPlayer',
    props:{
            options: {
                type: Object
            }
        },
        data(){
            return{
                player:null
            }
        },
        methods:{
            //定义好一个实例化播放器的方法
            createVideoPlayer(){
                this.player = this.$videoJS(this.$refs.videoPlayer,this.options)
            }
        },
        //在组件挂载时调用播放器实例化方法
        mounted(){
            this.createVideoPlayer()
        },
        //组件销毁前销毁播放器
        beforeDestroy(){
            if(this.player){
                this.player.dispose()
            }
        }
}
</script>
   
<style scoped>
.videoBox {
    box-sizing: border-box;
    position: relative;
    width: 800px;
    height: 500px;
}
</style>
