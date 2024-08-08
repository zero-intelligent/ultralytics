<template>
  <div class="main">
    <div class="hearder">
      <div class="hearder-box">
        <div class="hearder-logo">
          <el-image style="width: 100%; height: 100px" :src="require('./../assets/logo.png')" fit="scale-down"></el-image>
        </div>
        <div class="hearder-mian">
          <el-tabs v-model="activeName" @tab-click="handleClick">
            <el-tab-pane label="汇集位" name="first"></el-tab-pane>
            <el-tab-pane label="用餐区" name="second"></el-tab-pane>
          </el-tabs>
        </div>
        <!-- <div class="hearder-button">
          <i class="el-icon-minus" style="cursor: pointer;"></i>
          <i class="el-icon-close" style="cursor: pointer;"></i>
        </div> -->
      </div>
    </div>
    <div class="middle-box">
      <div class="middle-left">
        <div class="middle-top">
          <el-image style="width: 100%; height: 150px" :src="src" fit="scale-down"></el-image>
        </div>
        <div class="middle-bottom" v-if="activeName=='first'">
          <div v-for="(item, index) in list" :key="index">
            <span class="middle-item-error" style="{backgroundColor:item.conBgColor}">{{ item.title }}</span>
          </div>
        </div>
        <div class="middle-bottom" v-else>
          <div v-for="(item, index) in list" :key="index">
            <div class="middle-item-first" style="font-size: 18px;">{{ item.title }}</div>
            <div v-for="(itm, idx) in item.list" :key="idx" class="middle-item-itm">
              {{ itm.title }}
            </div>
          </div>
        </div>
      </div>
      <div class="middle-right">
        <div class="middle-search">
          <div>
            <el-button type="info" icon='el-icon-video-camera'>导入视频 <i class="el-icon-right"></i></el-button>
            <el-button type="info" icon='el-icon-bangzhu' @click="changeisCameraShow">链接摄像头 <i class="el-icon-right"></i></el-button>
          </div>
          <div>
            <el-select v-model="value" placeholder="请选择">
              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </div>
        </div>
        <div class="middle-main" v-if="isCameraShow">
          <div v-for="(item, index) in cardList" :key="index" class="middle-main-item">
            <div class="middle-main-hearder">
              <div>{{ item.label }}</div>
              <div v-if='item.num > 0'>
                帧率：{{ item.num }}
              </div>
            </div>
            <div class="middle-main-vedio" v-if="isShow">
              <video-component :videoSrc="item.src"></video-component>
            </div>
          </div>
        </div>
        <div class="middle-main-else" v-else>
          <div >
            配置并链接摄像头
          </div>
          <div>
            <el-radio v-model="radio" label="1">本地摄像头</el-radio>
            <el-select v-model="valueCamera" placeholder="请选择">
              <el-option v-for="item in optionsCamera" :key="item.value" :label="item.title" :value="item.value">
              </el-option>
            </el-select>
          </div>
          <div>
            <el-radio v-model="radio" label="2">网络摄像头</el-radio>
            <el-input v-model="input" style="width: 600px;" ></el-input>
          </div>
          <div style="text-align: end;">
          <el-button type="info"  @click="isCameraShow=true"> 取 消 </el-button>
          <el-button type="warning" style="margin-left: 20px;"   @click="submit"> 确 定 </el-button>
          </div>
        </div>
        <div class="middle-footer">
          <el-button type="warning" @click="changeType('1')"> 套餐A </el-button>
          <el-button type="warning" style="margin-left: 20px;"  @click="changeType('2')"> 套餐B </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 
import { getDataHuiji,getDataPeople,changeTaocan,getCamraList,setCamraList} from "./../api/index"
import videoComponent from './../components/videoComponent.vue'
export default {
  name: 'HelloWorld',
  components: {
    videoComponent
  },
  data() {
    return {
      radio: '1',
      activeName: 'first',
      input:"",
      loading: false,
      isCameraShow:true,
      isShow:true,
      src: require('./../assets/matwo.png'),
      optionsCamera:[],
      valueCamera:"",
      options: [{
        value: '4',
        label: 'YOLO V4'
      }, {
        value: '5',
        label: 'YOLO V5'
      }, {
        value: 'YOLO V6',
        label: 'YOLO V6'
      }, {
        value: 'YOLO V7',
        label: 'YOLO V7'
      }, {
        value: 'YOLO V8',
        label: 'YOLO V8'
      }],
      value: 'YOLO V8',
      list: [],
      cardList: [{
        label: "Input",
        src: ""
      }, {
        label: "Output",
        num: 25,
        src: ""
      },
      ]
    }
  },
  mounted() {
    this.refresh()
  },
  methods: {
   async changeisCameraShow(){
      if(this.isCameraShow){
        await this.getCamra()
        this.isCameraShow = false
      }
    },
    async getCamra() {
      try {
        this.loading = true
        let result = await getCamraList()
        if (result.code === 0) {
          this.optionsCamera= result?.list
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
      }
    },
    async submit() {
      try {
        this.loading = true
        let params={
          type:this.radio,
          local:this.valueCamera,
          url:this.input
        }
        let result = await setCamraList(params)
        if (result.code === 0) {
          this.isCameraShow = true
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
      }
    },
    async refresh() {
      try {
        this.loading = true
        this.list = []
        let result = await getDataHuiji()
        if (result.code === 0) {
          this.cardList[0].src = result?.input_video
          this.cardList[1].src = result?.output_video
          this.list = result?.list
          this.isShow = false
          this.$nextTick(()=>{
            this.isShow = true
          })
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
      }
    },
    async refreshOther() {
      try {
        this.loading = true
        this.list = []
        let result = await getDataPeople()
        if (result.code === 0) {
          this.cardList[0].src = result?.input_video
          this.cardList[1].src = result?.output_video
          this.list = result?.data
          this.isShow = false
          this.$nextTick(()=>{
            this.isShow = true
          })
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
      }
    },
    async changeType(type){
      try {
        this.buttonLoading = true
        let params = {
          type:type
        }
        let result = await changeTaocan(params)
        if (result.code === 0) {
          console.log(result)
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.buttonLoading = false
      }
    },
    handleClick() {
      if(this.activeName=='first'){
        this.refresh()
      }else{
        this.refreshOther()
      }
    }
  }
}
</script>

<style>
.main {
  width: 100%;
  height: 98vh;
  background: #000;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.hearder {
  height: 120px;
  box-sizing: border-box;
  padding: 20px 20px 0 20px;
}

.hearder-box {
  width: 100%;
  height: 100%;
  border-bottom: 2px solid #333;
  display: flex;
}

.middle-box {
  width: 100%;
  height: calc(100% - 120px);
  box-sizing: border-box;
  display: flex;
}

.hearder-logo {
  width: 330px;
}

.hearder-mian {
  width: 100%;
}

.hearder-button {
  width: 200px;
  height: 100%;
  line-height: 100px;
  font-size: 24px;
  color: #666;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-sizing: border-box;
  padding: 0 20px;
}

.middle-left {
  width: 330px;
  height: 100%;
  box-sizing: border-box;
  padding: 20px;
  background: #333;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.middle-top {
  height: 150px;
  /* background-color: rgba(48, 253, 46, 1); */
}

.middle-item {
  color: #333;
  background: #30FD2E;
  display: inline-block;
  margin: 10px 0;
  padding: 1px 5px;
}

.middle-item-error {
  color: #fff;
  background: #FF0202;
  display: inline-block;
  margin: 10px 0;
  padding: 1px 5px;
}
.middle-item-first{
  color: #30FD2E;
  margin: 20px 0;
}
.middle-item-itm{
  color: #30FD2E;
  margin: 10px 0;
  padding: 1px 5px;
}
.middle-right {
  width: calc(100% - 330px);
  height: 100%;
  overflow-y: auto;
  box-sizing: border-box;
  padding: 20px;
}
.middle-search {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
}

.middle-main {
  display: flex;
  flex-wrap: wrap;
}
.middle-main-else{
  margin-top: 40px;
  height: 420px;
  background: #444;
  border-radius: 8px;
  display: flex;
  justify-content: space-around;
  flex-direction: column;
  box-sizing: border-box;
  padding: 20px;
}
.middle-main-item {
  width: 48%;
  margin-right: 2%;
  margin-top: 40px;
  height: 420px;
  background: #333;
  border-radius: 8px;
}

.middle-main-hearder {
  display: flex;
  justify-content: space-between;
  background: #666;
  font-size: 16px;
  height: 50px;
  line-height: 50px;
  box-sizing: border-box;
  padding: 0 10px;
  border-radius: 8px;
}

.middle-main-vedio {
  background: #777;
  width: 90%;
  margin-left: 5%;
  height: calc(100% - 100px);
  margin-top: 20px;
  border-radius: 6px;
}

.middle-footer {
  margin-top: 120px;
  padding: 0 10px;
}

.el-tabs__nav {
  float: right;
}

.el-tabs__item {
  height: 100px;
  line-height: 100px;
  font-size: 18px;
  color: #666;
}

.el-tabs__item:hover {
  color: #FFBC0D
}

.el-tabs__item.is-active {
  color: #fff
}

.el-tabs__active-bar {
  background-color: #FFBC0D;
  height: 4px;
}

.el-tabs__nav-wrap::after {
  height: 0;
}

.el-button--info:focus,
.el-button--info:hover {
  background: #333;
}

.el-button--info {
  background: #333;
  border: 0;
  color: #EEE;
}

.el-range-editor.is-active,
.el-range-editor.is-active:hover,
.el-select .el-input.is-focus .el-input__inner {
  border-color: #FFBC0D;
}
.el-radio__input.is-checked+.el-radio__label{
  color: #FFBC0D
}
.el-input__inner {
  background: #333;
  color: #EEE;
  border: 0;
}
.el-radio__inner{
  background: #333;
  color: #EEE;
  border: 0;
}
.el-select-dropdown {
  background: #333;
  color: #EEE;
  border: 0;
}

.el-select-dropdown__item.selected {
  color: #FFBC0D
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover {
  background-color: #FFBC0D;
}
.el-radio__input.is-checked .el-radio__inner{
  background-color: #FFBC0D;
}
.el-button--warning:focus,
.el-button--warning:hover {
  background-color: #FFBC0D;
}

.el-button--warning {
  background-color: #FFBC0D;
  color: #333;
  padding: 10px 30px;
  font-weight: 900;
}
</style>