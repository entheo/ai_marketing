module.exports = {
  devServer: {
   // host:'0.0.0.0',
    //port:8081,
    allowedHosts:'all',
    proxy: {
      '/account': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true
      },
      '/api': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true
      }
    }
  }
}
