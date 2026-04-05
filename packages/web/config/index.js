const path = require('path');

module.exports = {
  projectName: 'jzhuang-web',
  date: '2026-04-05',
  designWidth: 750,
  deviceRatio: {
    '375': 2,
    '640': 1,
    '750': 1
  },
  sourceRoot: 'src',
  outputRoot: 'dist',
  plugins: [],
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
    'process.env.API_BASE_URL': JSON.stringify(process.env.API_BASE_URL || 'http://localhost:8000')
  },
  alias: {
    '@/': path.resolve(__dirname, 'src/'),
    '@/components/': path.resolve(__dirname, 'src/components/'),
    '@/pages/': path.resolve(__dirname, 'src/pages/'),
    '@/stores/': path.resolve(__dirname, 'src/stores/'),
    '@/services/': path.resolve(__dirname, 'src/services/'),
    '@/utils/': path.resolve(__dirname, 'src/utils/'),
    '@/constants/': path.resolve(__dirname, 'src/constants/')
  },
  mini: {},
  h5: {
    publicPath: '/',
    staticDirectory: 'static',
    webpackChain: (chain) => {
      chain.merge({
        module: {
          rule: [
            {
              test: /\.(png|jpe?g|gif|svg|webp)$/i,
              type: 'asset/resource'
            }
          ]
        }
      });
    }
  },
  frameworks: ['react']
};