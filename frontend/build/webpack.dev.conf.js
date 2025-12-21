'use strict'
const path = require('path')
const webpack = require('webpack')
const { merge } = require('webpack-merge')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const baseWebpackConfig = require('./webpack.base.conf')

module.exports = merge(baseWebpackConfig, {
  mode: 'development',
  devtool: 'eval-cheap-module-source-map',

  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['vue-style-loader', 'css-loader', 'postcss-loader']
      }
    ]
  },

  devServer: {
    contentBase: path.join(__dirname, '../static'),
    historyApiFallback: true,
    hot: true,
    compress: true,
    host: '0.0.0.0',  // Allow external access
    port: 3003,
    open: false,  // Don't auto-open browser
    overlay: {
      warnings: false,
      errors: true
    }
  },

  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: '"development"'
      }
    }),
    new webpack.HotModuleReplacementPlugin(),
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: 'index.html',
      inject: true
    }),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, '../static'),
          to: 'static',
          globOptions: {
            ignore: ['.*']
          }
        }
      ]
    })
  ]
})
