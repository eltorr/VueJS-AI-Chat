const path = require('path');

module.exports = {
  transpileDependencies: true,
  
  // Output directory for production build
  outputDir: path.resolve(__dirname, '../backend/static'),
  
  // Modify asset paths to be relative
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  
  // Configure development proxy
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  },

  // Generate source maps for production
  productionSourceMap: false,
  
  // Configure webpack to handle static assets
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].title = 'Omni Chat';
      return args;
    });
  }
}