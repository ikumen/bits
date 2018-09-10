const webpack = require('webpack');
const HtmlWebPackPlugin = require("html-webpack-plugin");

const config = {
    entry: __dirname + '/js/index.jsx',
    output: {
			path: __dirname + '/dist',
			filename: 'js/bundle.js',
    },
    resolve: {
			extensions: ['.js', '.jsx', '.css']
    },
    module: {
		rules: [
			{
				test: /\.jsx?/,
				exclude: '/node_modules/',
				use: {
					loader: 'babel-loader'
				}
			}
		]
	},
	plugins: [new HtmlWebPackPlugin({
		template: "./index.html",
		filename: 'index.html'
	})],
	devServer: {
		proxy: {
			'/api': 'http://localhost:5000'
		}		
	}
};
module.exports = config;
