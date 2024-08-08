
module.exports = {
  devServer: {
    port: 8000, // 更改开发服务器的端口
    allowedHosts: [
      'pinda.org.cn', 
    ],
  },
  publicPath: process.env.NODE_ENV === 'production' ? '' : '/',
  outputDir: 'dist',
  assetsDir: 'static',

}