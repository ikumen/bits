const path = require('path');
const HtmlWebPackPlugin = require("html-webpack-plugin");
const CompressionPlugin = require('compression-webpack-plugin');

const htmlPlugin = new HtmlWebPackPlugin({
  template: "./frontend/index.html",
  filename: "./index.html"
});

const devServer = 'http://localhost:5000'

module.exports = {
  entry: __dirname + '/frontend/app.js',
  output: {
    filename: 'static/js/app.js',
    publicPath: '/',
    path: path.resolve(__dirname, 'public')
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
            "style-loader", 
            "css-loader"
        ],
      }
    ]
  },
  plugins: [
      htmlPlugin,
      new CompressionPlugin()
  ],
  devServer: {
    disableHostCheck: true,
    headers: {
        'Access-Control-Allow-Origin': '*'
    },  
    contentBase: __dirname + '/frontend',
    historyApiFallback: {
        rewrites: [
          { from: /^\/$/, to: '/index.html' },
          { from: /^\/@\S+/, to: '/index.html' }
        ]
    },
    proxy: {
      '/api': devServer,
      '/signin': devServer,
      '/signout': devServer,
      '/sync': devServer,
    }
  }
};
