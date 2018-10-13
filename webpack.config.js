const HtmlWebPackPlugin = require("html-webpack-plugin");
const CompressionPlugin = require('compression-webpack-plugin');

const htmlPlugin = new HtmlWebPackPlugin({
  template: "./client/index.html",
  filename: "./index.html"
});

module.exports = {
  entry: __dirname + '/client/app.js',
  output: {
    filename: 'static/js/main.js',
    publicPath: '/'
  },
  module: {
    rules: [
      // loaders are loaded bottom up
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        },
      },
      {
        test: /\.css$/,
        use: [
          {
            loader: "style-loader"
          },
          {
            loader: "css-loader",
            options: {
              modules: true,
              importLoaders: 1,
              localIdentName: "[name]_[local]_[hash:base64]",
              sourceMap: true,
              minimize: true
            }
          }          
        ]
      }
    ]
  },
  plugins: [
      htmlPlugin,
      new CompressionPlugin()
  ],
  devServer: {
    contentBase: __dirname + '/client',
    historyApiFallback: {
        rewrites: [
          { from: /^\/$/, to: '/index.html' },
          { from: /^\/@\S+/, to: '/index.html' }
        ]
    },
    proxy: {
      '/api': 'http://localhost:5000',
      '/signin': 'http://localhost:5000'
    }
  }
};