/* eslint-env node */
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const TerserJSPlugin = require('terser-webpack-plugin');
const SpriteLoaderPlugin = require('svg-sprite-loader/plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

const isDev = process.env.NODE_ENV !== 'production';
const plugins = [
  new MiniCssExtractPlugin({
    filename: isDev ? '[name].css' : '[name].[contenthash].css',
    chunkFilename: isDev ? '[id].css' : '[id].[contenthash].css',
  }),
  new SpriteLoaderPlugin(),
  new CleanWebpackPlugin({
    cleanOnceBeforeBuildPatterns: ['**/*', '!.gitkeep'],
  }),
];

module.exports = {
  mode: process.env.NODE_ENV,
  devtool: 'inline-source-map',
  resolve: {
    extensions: ['.js', '.css'],
    alias: {
      '@': path.resolve(__dirname, 'assets'),
    },
  },
  entry: {
    common: path.resolve(__dirname, 'assets/js/common.js'),
  },
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    publicPath: '/static/dist/',
    filename: '[name].js',
  },
  plugins,
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
        ],
      },
      {
        test: /\.(svg|png|jpe?g|gif|webp|woff|woff2|eot|ttf|otf)$/,
        exclude: path.resolve('./assets/icons'),
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'assets/',
            },
          },
        ],
      },
      {
        test: /\.svg$/,
        include: path.resolve('./assets/icons'),
        use: [
          {
            loader: 'svg-sprite-loader',
            options: {
              extract: true,
              spriteFilename: 'icons.svg',
              esModule: false,
            },
          },
          'svgo-loader',
        ],
      },
    ],
  },
  devServer: {
    proxy: {
      '**': {
        target: process.env.BACKEND_URL || 'http://backend:8000',
      },
    },
    allowedHosts: (process.env.ALLOWED_HOSTS || 'localhost').split(/\s+/),
    host: '0.0.0.0',
    port: 3000,
    compress: true,
    client: {
      overlay: true,
      // Enable `webSocketURL` if you use Pontsun configuration
      // webSocketURL: {
      //   port: 443,
      // },
    },
    static: {
      directory: './{{ cookiecutter.project_slug }}/**/templates/**/*.html',
    },
  },
  optimization: {
    minimizer: [new TerserJSPlugin(), new CssMinimizerPlugin()],
  },
};
