/* eslint-disable */
<template>
  <div class="main">
    <div class="hearder">
      <div class="hearder-box">
        <div class="hearder-logo">
          <el-image style="width: 100%; height: 100px" :src="require('./../assets/logo.png')" fit="contain"></el-image>
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
          <el-image style="width: 100%; height: 150px" :src="src"></el-image>
        </div>
        <div class="middle-middle" v-if="activeName == 'first'">
          <div v-if="configInfo.total_taocan_result_state == 'correct'" class="middle-middle-title"> 配 餐 完 整</div>
          <div v-if="configInfo.total_taocan_result_state == 'incorrect'" class="middle-middle-title-error"> 配 餐 不 完 整
          </div>
        </div>
        <div class="middle-bottom" v-if="activeName == 'first'">
          <span v-if="isShow">
            <span class="middle-item-title">套餐内食品</span><br />
            <div v-for="(item, index) in list" :key="index">
              <span class="middle-item-error" v-if="item.is_in_taocan"
                :style='{ backgroundColor: item.count === item.real_count ? "#30FD2E" : "#FF0202" }'>{{
                  item.name }}</span>
            </div>
          </span>
          <span v-if="isShow">
            <span class="middle-item-title">非套餐内食品</span>
            <div v-for="(item, index) in list" :key="index">
              <span class="middle-item-error" v-if="!item.is_in_taocan"
                :style='{ backgroundColor: item.count === item.real_count ? "#30FD2E" : "#FF0202" }'>{{
                  item.name }}</span>
            </div>
          </span>
        </div>
        <div class="middle-bottom" v-else>
          <div v-for="(item, index) in list" :key="index">
            <div class="middle-item-first" style="font-size: 18px;">人员{{ index }}:{{ item }}秒</div>
            <!-- <div v-for="(itm, idx) in item.list" :key="idx" class="middle-item-itm">
              {{ itm.title }}
            </div> -->
          </div>
        </div>
      </div>
      <div class="middle-right">
        <div class="middle-search">
          <div style="display: flex;">
            <el-upload ref="upload" multiple action="" :show-file-list="false" :http-request="handleFileUpload"
              :limit="10" :on-exceed="handleExceed" :on-success="handleAvatarSuccess">
              <el-button type="info" icon='el-icon-video-camera' style="padding: 13px; " :disabled="disabled">导入视频 <i
                  class="el-icon-right"></i></el-button>
            </el-upload>
            <el-button type="info" icon='el-icon-bangzhu' @click="changeisCameraShow" style="margin-left: 20px;">链接摄像头 <i
                class="el-icon-right"></i></el-button>
          </div>
          <div>
            <el-select v-model="value" placeholder="请选择">
              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value">
              </el-option>
            </el-select>
          </div>
        </div>
        <div class="middle-main" v-if="isCameraShow">
          <span style="display: inline-block;margin-top: 40px;padding-right: 8px;width: 72px;"> 
            <!-- slot="placeholder" class="image-slot" -->
            <div>
              {{ configInfo.running_state }}
              <span class="dot">...</span>
            </div>
            <div v-if='frame_rate > 0'>
              帧率：{{ frame_rate }}
            </div>
          </span>
          <div v-for="(item, index) in cardList" :key="index" class="middle-main-item">
            <div class="middle-main-hearder">
              <div>{{ item.label }}</div>

            </div>
            <!-- <div class="middle-main-vedio" v-if="isShow && configInfo && configInfo.data_type === 'video_file'">
              <video-component :videoSrc="getSrc(item.src)"></video-component>
            </div> -->
            <!-- <div class="middle-main-vedio" v-if="isShow && configInfo && configInfo.data_type === 'camera'"> -->
            <div class="middle-main-vedio">

              <el-image :src="getSrc(item.src)" width="100%" height="100%" style="width: 100%; height: 100%"
                :preview-src-list="getSrcList(item.src)" fit="cover">

              </el-image>
            </div>
          </div>
        </div>
        <div class="middle-main-else" v-else>
          <div>
            配置并链接摄像头
          </div>
          <div>
            <el-radio v-model="radio" label="1">本地摄像头</el-radio>
            <el-select v-model="valueCamera" placeholder="请选择">
              <el-option v-for="(item, index) in optionsCamera" :key="index" :label="item" :value="index">
              </el-option>
            </el-select>
          </div>
          <div>
            <el-radio v-model="radio" label="2">网络摄像头</el-radio>
            <el-input v-model="input" style="width: 600px;"></el-input>
          </div>
          <div style="text-align: end;">
            <el-button type="info" @click="isCameraShow = true"> 取 消 </el-button>
            <el-button type="warning" style="margin-left: 20px;" @click="submit"> 确 定 </el-button>
          </div>
        </div>
        <div class="middle-footer" v-if="activeName != 'second'">
          <el-button type="warning" @click="changeType(0)"
            :style="{ color: configInfo.taocan_id === 0 ? '#fff' : '', textDecoration: configInfo.taocan_id === 0 ? 'underline' : '' }">
            套餐A </el-button>
          <el-button type="warning" style="margin-left: 20px;" @click="changeType(1)"
            :style="{ color: configInfo.taocan_id === 1 ? '#fff' : '', textDecoration: configInfo.taocan_id === 1 ? 'underline' : '' }">
            套餐B </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 
import { getDataHuiji, getDataPeople, changeTaocan, getCamraList, modeDatasource, uploadCamera, getConfig, switchMode, baseUrl } from "./../api/index"
// import videoComponent from './../components/videoComponent.vue'
// import SparkMD5 from "spark-md5";
export default {
  name: 'HelloWorld',
  components: {
    // videoComponent
  },
  data() {
    return {
      radio: '1',
      activeName: 'first',
      frame_rate: 0,
      input: "",
      loading: false,
      isCameraShow: true,
      isShow: true,
      src: require('./../assets/matwo.png'),
      optionsCamera: [],
      valueCamera: "",
      options: [
        {
          value: 'YOLO V8',
          label: 'YOLO V8'
        }],
      value: 'YOLO V8',
      list: [],
      cardList: [{
        label: "Input",
        src: "video_source_feed",
      }, {
        label: "Output",
        src: "video_output_feed"
      },
      ],
      disabled: false,
      configInfo: {},
      timer: null,
      eventSource: null
    }
  },

  beforeDestroy() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  },

  async mounted() {
    await this.getConfigInfo()

    this.connectEventSource();
  },
  created() {

  },
  methods: {

    connectEventSource() {
      this.eventSource = new EventSource(baseUrl + '/config_sse');
      //this.eventSource = new EventSource('http://192.168.31.77:6789/config_sse');

      this.eventSource.onmessage = (event) => {
        console.log(event.data)
        const data = JSON.parse(event.data);
        console.log(data);
        // this.events.push(data);
        let dataJson = {
          code: 0,
          data: data
        };
        this.doGetConfig(dataJson);
      };

      this.eventSource.onopen = function (event) {
        console.log('EventSource open ', event);
      }

      this.eventSource.onerror = (error) => {
        console.error('EventSource failed', error);
      };
    },

    getSrc(src) {
      if (src == "" || src == "null" || src == null) {
        return "";
      }
      if (src[0] != "/") {
        src = "/" + src;
      }
      return baseUrl + src
      //return 'http://192.168.31.77:6789' + src
    },
    getSrcList(src) {
      if (src == "" || src == "null" || src == null) {
        return [];
      }
      if (src[0] != "/") {
        src = "/" + src;
      }
      return [baseUrl + src]
      //return ['http://192.168.31.77:6789' + src]
    },
    async changeisCameraShow() {
      await this.switchTypeFun("2")
      if (this.isCameraShow) {
        await this.getCamra()
        this.isCameraShow = false
      }
    },
    async getCamra() {
      try {
        this.loading = true
        let result = await getCamraList()
        if (result.code === 0) {
          this.optionsCamera = result?.data
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
        let params = {
          // type: this.radio,
          data_source: this.radio == '1' ? this.valueCamera : this.input,
          data_source_type: "camera",
          mode: this.activeName == 'first' ? "huiji_detect" : "person_detect"
          // url: this.input
        }
        let result = await modeDatasource(params)
        if (result.code === 0) {
          this.isCameraShow = true

          // this.cardList[0].src = ""
          // this.cardList[1].src = ""

          // this.getConfigInfo()
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
      }
    },
    async switchModeFun(modeType) {
      try {
        this.list = []
        let params = {
          mode: modeType
        }
        let result = await switchMode(params)
        if (result.code === 0) {
          console.log(result)

        }
      } catch (error) {
        console.log(error)
      }
    },
    async getConfigInfo() {
      try {

        this.loading = true
        let result = await getConfig();
        this.doGetConfig(result);
        // clearInterval(this.timer);
        // this.timer = setInterval(() => {
        // setTimeout(async () => {
        //   this.getConfigTarget();
        // }, 3000);
        // }, 3000);

        // if (this.configInfo.data_type === 'video_file') {
        //   //if (!this.configInfo?.data_file_source || this.configInfo?.data_file_source == null) {
        //     clearInterval(this.timer);
        //     this.timer = setInterval(() => {
        //       setTimeout(async () => {
        //         this.getConfigTarget();
        //       }, 0);
        //     }, 3000);
        //   //}
        // } else {
        //   if (this.activeName == 'first') {
        //     this.list = []
        //     this.refresh()
        //     clearInterval(this.timer);
        //     this.timer = setInterval(() => {
        //       setTimeout(async () => {
        //         this.refresh();
        //       }, 0);
        //     }, 3000);
        //     // this.timer = setInterval(this.refresh(), 3000);
        //   } else {
        //     this.list = []
        //     this.refreshOther();
        //     clearInterval(this.timer);
        //     this.timer = setInterval(() => {
        //       setTimeout(async () => {
        //         this.refreshOther();
        //       }, 0);
        //     }, 3000);
        //     // this.timer = setInterval(this.refreshOther(), 3000);
        //   } 
        // }
        // } else {
        //   this.configInfo = {}
        // }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
      }
    },

    doGetConfig(result) {
      if (result.code === 0) {
        this.configInfo = { ...result.data }
        this.radio = this.configInfo.camera_type === 0 ? "1" : "2"
        this.valueCamera = this.configInfo.camera_local
        this.input = this.configInfo.camera_url
        if (this.configInfo.mode == 'huiji_detect') {
          this.activeName = 'first'
        } else {
          this.activeName = 'second'
        }
        // this.cardList[0].src = result?.data?.video_source //+ "?mode=" + this.configInfo.mode
        // this.cardList[1].src = result?.data?.video_target //+ "?mode=" + this.configInfo.mode
        this.frame_rate = this.configInfo.frame_rate
        if (this.configInfo.mode == "person_detect") {
          this.list = result?.data?.current_person_result
          this.isShow = false
          this.$nextTick(() => {
            this.isShow = true
          })
        } else {
          this.list = result?.data?.current_taocan_result
          this.isShow = false
          this.$nextTick(() => {
            this.isShow = true
          })
        }
      } else {
        this.configInfo = {}
      }
    },

    async getConfigTarget() {
      try {
        this.loading = true
        let result = await getConfig()
        if (result.code === 0) {
          this.configInfo = { ...result.data }
          this.radio = this.configInfo.camera_type === 0 ? "1" : "2"
          this.valueCamera = this.configInfo.camera_local
          this.input = this.configInfo.camera_url
          if (this.configInfo.mode == 'huiji_detect') {
            this.activeName = 'first'
          } else {
            this.activeName = 'second'
          }
          // this.cardList[0].src = result?.data?.video_source //+ "?mode=" + this.configInfo.mode
          // this.cardList[1].src = result?.data?.video_target //+ "?mode=" + this.configInfo.mode
          this.frame_rate = this.configInfo.frame_rate
          if (this.configInfo.mode == "person_detect") {
            this.list = result?.data?.current_person_result
            this.isShow = false
            this.$nextTick(() => {
              this.isShow = true
            })
          } else {
            this.list = result?.data?.current_taocan_result
            this.isShow = false
            this.$nextTick(() => {
              this.isShow = true
            })
          }

        } else {
          this.configInfo = {}
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
        setTimeout(async () => {
          this.getConfigTarget();
        }, 3000);
      }
    },
    async refresh() {
      try {
        this.loading = true
        let result = await getDataHuiji()
        if (result.code === 0) {
          // this.cardList[0].src = result?.data?.input_video
          // this.cardList[1].src = result?.data?.output_video
          this.list = result?.data?.current_taocan_result
          this.isShow = false
          this.$nextTick(() => {
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
        let result = await getDataPeople()
        if (result.code === 0) {
          // this.cardList[0].src = result?.data?.input_video
          // this.cardList[1].src = result?.data?.output_video
          this.list = result?.data?.data
          this.isShow = false
          this.$nextTick(() => {
            this.isShow = true
          })
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.loading = false
      }
    },
    async changeType(type) {
      try {
        this.buttonLoading = true
        let params = {
          taocan_id: type
        }
        let result = await changeTaocan(params)
        if (result.code === 0) {
          this.configInfo.taocan_id = type
          console.log(result)
        }
      } catch (error) {
        console.log(error)
      } finally {
        this.buttonLoading = false
      }
    },
    async switchTypeFun(type) {
      console.log(type);
      // try {
      //   this.buttonLoading = true
      //   let params = {
      //     type: type == '1' ? "video_file" : "camera"
      //   }
      //   let result = await switchType(params)
      //   if (result.code === 0) {
      //     console.log(result)
      //   }
      // } catch (error) {
      //   console.log(error)
      // } finally {
      //   this.buttonLoading = false
      // }
    },
    async handleClick() {
      await clearInterval(this.timer)
      if (this.activeName == 'first') {
        // this.refresh()
        await this.switchModeFun("huiji_detect")
      } else {
        // this.refreshOther()
        await this.switchModeFun("person_detect")
      }
      //this.getConfigInfo()
    },
    getMd5(file, spark) {
      return new Promise((resolve) => {
        // 对文件对象的处理
        var fileReader = new FileReader();
        fileReader.readAsArrayBuffer(file);
        // fileReader.onload为异步函数，要放到Promise对象中，等待状态的变更后再返回生成的md5值
        fileReader.onload = function (e) {
          spark.append(e.target.result);
          resolve(spark.end());
        };
      });
    },
    // 上传(同时选择多个文件时会多次上传该文件)
    async handleFileUpload(item) {
      //先停掉定时任务
      console.log("handleFileUpload");
      clearInterval(this.timer);
      console.log("clear end");

      await this.switchTypeFun(1)
      console.log("sefdsafadsf");
      let file = item.file
      this.disabled = true;
      console.log("start to upload33");
      console.log(this.list)
      //this.list = [...this.list, file]; //用于展示进度
      this.list = [file]; //用于展示进度
      console.log("start to upload222");
      this.uploadModal = true; // 展示进度弹窗
      console.log("start to upload111");
      // 文件大于50MB时分片上传
      // if (file.size / 1024 / 1024 < 50) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("name", file.name);
      console.log("start to upload");
      uploadCamera(formData).then((res) => {
        if (res.error !== "error") {
          this.list.forEach((item) => {
            if (item.name === file.name) {
              item.percent = 100;
            }
          })
          this.$message.success(`${file.name}：上传完成`);
          this.getConfigInfo();
        } else {
          this.list.forEach((item) => {
            if (item.name === file.name) {
              item.typeProgress = 1;
            }
          })
        }
      }).finally(() => {
        this.disabled = false;
      });
      // } else {
      // const size = 1 * 1024 * 1024; // 10MB 每个分片大小
      // let current = 0; // 当前分片index(从0开始)
      // let total = Math.ceil(file.size / size); // 分片总数
      // let startByte = 0;
      // // 通过文件获取对应的md5值
      // let dataFileStart = file.slice(0, size); // 第一片文件
      // let dataFileEnd = file.slice(size * (total - 1), file.size) // 最后一片文件
      // var spark = new SparkMD5.ArrayBuffer();
      // //获取文件二进制数据
      // let md5Start = await this.getMd5(dataFileStart, spark); // 第一片的md5值
      // let md5End = await this.getMd5(dataFileEnd, spark); // 最后一片的md5值
      // let md5 = md5Start + md5End;

      // let identifier = "file_" + Date.now()

      // 文件完整性检测
      // uploadCamera({ md5: md5, fileName: file.name }).then((res) => {
      //   if (res.error !== "error") {
      // current = 0; //res?.indexOf("0") === -1 ? 0 : res?.indexOf("0"); // 当前服务器应该上传的分片下标
      // startByte = size * current
      // this.uploadChunk(identifier, file, startByte, current, md5);
      //   }
      // }).finally(() => {
      //   this.disabled = false;
      // });
      // }
      // return false;
    },
    uploadChunk(identifier, file, startByte, current, md5) {
      console.log("uploadChunk")
      const formData = new FormData();
      const size = 1 * 1024 * 1024;
      let total = Math.ceil(file.size / size); // 分片总数
      const endByte = Math.min(startByte + size, file.size);
      const chunk = file.slice(startByte, endByte); // 当前分片文件
      formData.append("identifier", identifier);
      formData.append("file", chunk);
      formData.append("name", file.name);
      formData.append("current", current);
      formData.append("total", total);
      formData.append("md5", md5);
      uploadCamera(formData).then((res) => {
        if (res.code == 200) {
          console.log("res", res);
          this.list.forEach((item) => {
            if (item.name === file.name) {
              item.percent = Math.floor(((Number(current) + 1) * 100) / total);
            }
          })
          this.list = [...this.list]
          startByte = endByte;
          if (startByte < file.size) {
            current++;
            this.uploadChunk(file, startByte, current, md5);
          } else {
            this.$message.success(`${file.name}：上传完成`);
          }
        } else {
          this.list.forEach((item) => {
            if (item.name === file.name) {
              item.typeProgress = 1;
            }
          })
        }
      }).finally(() => {
        this.disabled = false;
        this.getConfigInfo()
      });
    },
    // 文件超出个数限制时的钩子
    handleExceed(files) {
      this.$message.warning(`最多同时上传 10 个文件，本次选择了 ${files.length} 个文件`);
    },
    // 文件上传成功时的钩子(清除上传历史记录，防止文件限制超出)
    handleAvatarSuccess() {
      this.$refs.upload.clearFiles();
    },
    // refreshFirst() {
    //   this.timer = setInterval(this.fetchData, 3000);
    // },
    // async fetchData() {
    //   try {
    //     const response = await this.$http.get('/api/data'); // 假设使用axios
    //     this.data = response.data;
    //     if (data) {
    //       clearInterval(this.timer)
    //     }
    //   } catch (error) {
    //     console.error('Error fetching data:', error);
    //   }
    // }
  }
}
</script>

<style>
.main {
  width: 100%;
  height: 100vh;
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
  justify-content: space-around;
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

.middle-middle-title {
  color: #30FD2E;
  display: inline-block;
  margin: 10px 0;
  font-size: 30px;
  font-weight: 900;
}

.middle-middle-title-error {
  color: #FF0202;
  display: inline-block;
  margin: 10px 0;
  font-size: 30px;
  font-weight: 900;
}

.middle-item-title {
  color: #fff;
  display: inline-block;
  margin: 10px 0;
  font-size: 20px;
  font-weight: 900;
}

.middle-item-error {
  color: #fff;
  background: #FF0202;
  display: inline-block;
  margin: 10px 0;
  padding: 1px 5px;
}

.middle-item-first {
  color: #30FD2E;
  margin: 20px 0;
}

.middle-item-itm {
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

.middle-main-else {
  margin-top: 40px;
  height: 520px;
  background: #444;
  border-radius: 8px;
  display: flex;
  justify-content: space-around;
  flex-direction: column;
  box-sizing: border-box;
  padding: 20px;
}

.middle-main-item {
  width:  calc(47% - 36px);
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

.el-radio__input.is-checked+.el-radio__label {
  color: #FFBC0D
}

.el-input__inner {
  background: #333;
  color: #EEE;
  border: 0;
}

.el-radio__inner {
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

.el-radio__input.is-checked .el-radio__inner {
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