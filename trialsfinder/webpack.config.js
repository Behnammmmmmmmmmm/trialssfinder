const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const WorkboxPlugin = require('workbox-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  const isDevelopment = argv.mode === 'development';
  const isAnalyze = env && env.ANALYZE === 'true';

  // Ensure NODE_ENV is set correctly
  process.env.NODE_ENV = isProduction ? 'production' : 'development';

  return {
    entry: {
      main: './src/index.tsx',
    },
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProduction ? 'js/[name].[contenthash:8].js' : 'js/[name].js',
      chunkFilename: isProduction ? 'js/[name].[contenthash:8].chunk.js' : 'js/[name].chunk.js',
      clean: true,
      publicPath: '/',
      assetModuleFilename: 'assets/[name].[hash:8].[ext]',
    },
    mode: isProduction ? 'production' : 'development',
    devtool: isProduction ? 'hidden-source-map' : 'cheap-module-source-map',
    resolve: {
      extensions: ['.ts', '.tsx', '.js', '.jsx', '.mjs'],
      alias: {
        '@': path.resolve(__dirname, 'src'),
        // Use preact in production for smaller bundle
        ...(isProduction && {
          'react': 'preact/compat',
          'react-dom': 'preact/compat',
          'react/jsx-runtime': 'preact/jsx-runtime'
        }),
      },
      // Handle Node.js polyfills
      fallback: {
        'stream': false,
        'http': false,
        'https': false,
        'zlib': false,
        'url': false,
        'util': false,
        'buffer': false,
        'process': false,
      },
    },
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            parse: {
              ecma: 8,
            },
            compress: {
              ecma: 5,
              warnings: false,
              comparisons: false,
              inline: 2,
              drop_console: isProduction,
              drop_debugger: true,
              pure_funcs: isProduction ? ['console.log', 'console.info', 'console.debug', 'console.warn'] : [],
              passes: 2,
              booleans: true,
              conditionals: true,
              dead_code: true,
              evaluate: true,
              if_return: true,
              join_vars: true,
              sequences: true,
              unused: true,
              loops: true,
              toplevel: false,
              top_retain: null,
              hoist_funs: true,
              keep_fargs: false,
              keep_fnames: false,
              hoist_vars: false,
              module: true,
              unsafe: false,
              unsafe_math: true,
              unsafe_proto: false,
              unsafe_regexp: false,
              unsafe_undefined: false,
              side_effects: false,
            },
            mangle: {
              safari10: true,
            },
            format: {
              ecma: 5,
              comments: false,
              ascii_only: true,
            },
          },
          parallel: true,
          extractComments: false,
        }),
        new CssMinimizerPlugin({
          minimizerOptions: {
            preset: [
              'default',
              {
                discardComments: { removeAll: true },
                normalizeWhitespace: true,
                colormin: true,
                convertValues: { precision: 2 },
              },
            ],
          },
        }),
      ],
      runtimeChunk: 'single',
      moduleIds: 'deterministic',
      splitChunks: {
        chunks: 'all',
        maxInitialRequests: 30,
        maxAsyncRequests: 30,
        minSize: 20000,
        cacheGroups: {
          default: false,
          vendors: false,
          // React/Preact bundle
          framework: {
            name: 'framework',
            test: /[\\/]node_modules[\\/](react|react-dom|preact|scheduler|object-assign)[\\/]/,
            priority: 50,
            chunks: 'all',
            enforce: true,
          },
          // React Router and state management
          'react-router': {
            name: 'react-router',
            test: /[\\/]node_modules[\\/](react-router|react-router-dom|history)[\\/]/,
            priority: 40,
            chunks: 'all',
            enforce: true,
          },
          // State management
          state: {
            name: 'state',
            test: /[\\/]node_modules[\\/](zustand|immer)[\\/]/,
            priority: 40,
            chunks: 'all',
            enforce: true,
          },
          // Core vendor libraries
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name(module) {
              // Get the package name
              const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
              
              // Group small packages together
              const corePackages = ['tslib', 'object-assign', 'scheduler'];
              if (corePackages.includes(packageName)) {
                return 'vendor-core';
              }
              
              // Split large packages into separate chunks
              const largePackages = ['axios', 'date-fns', 'i18next'];
              if (largePackages.includes(packageName)) {
                return `vendor-${packageName.replace('@', '')}`;
              }
              
              // Group remaining small packages
              return 'vendor-misc';
            },
            priority: 10,
            minChunks: 1,
            reuseExistingChunk: true,
          },
          // Common chunks
          common: {
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true,
            enforce: true,
          },
        },
      },
    },
    module: {
      rules: [
        // JavaScript/TypeScript
        {
          test: /\.(ts|tsx|js|jsx|mjs)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
              cacheCompression: false,
              compact: isProduction,
              configFile: path.resolve(__dirname, 'babel.config.js'),
              babelrc: false,
              presets: [
                ['@babel/preset-env', {
                  targets: {
                    browsers: '>0.25%, not dead',
                  },
                  modules: false,
                  useBuiltIns: false,
                  // Exclude transforms for modern browsers
                  exclude: ['transform-typeof-symbol'],
                }],
                ['@babel/preset-react', {
                  runtime: 'automatic',
                  development: isDevelopment,
                }],
                '@babel/preset-typescript',
              ],
              plugins: [
                '@babel/plugin-syntax-dynamic-import',
                ...(isProduction ? [
                  ['babel-plugin-transform-react-remove-prop-types', {
                    mode: 'remove',
                    removeImport: true,
                  }],
                ] : []),
              ],
            },
          },
        },
        // CSS
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            {
              loader: 'css-loader',
              options: {
                importLoaders: 1,
                modules: false,
                sourceMap: !isProduction,
              },
            },
            {
              loader: 'postcss-loader',
              options: {
                sourceMap: !isProduction,
              },
            },
          ],
        },
        // Images
        {
          test: /\.(png|svg|jpg|jpeg|gif|webp)$/i,
          type: 'asset',
          parser: {
            dataUrlCondition: {
              maxSize: 4 * 1024, // 4kb
            },
          },
          generator: {
            filename: 'images/[name].[hash:8][ext]',
          },
        },
        // Fonts
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'fonts/[name].[hash:8][ext]',
          },
        },
      ],
    },
    plugins: [
      new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(isProduction ? 'production' : 'development'),
      }),
      new HtmlWebpackPlugin({
        template: 'public/index.html',
        inject: 'body',
        scriptLoading: 'defer',
        minify: isProduction ? {
          removeComments: true,
          collapseWhitespace: true,
          removeRedundantAttributes: true,
          useShortDoctype: true,
          removeEmptyAttributes: true,
          removeStyleLinkTypeAttributes: true,
          keepClosingSlash: true,
          minifyJS: true,
          minifyCSS: true,
          minifyURLs: true,
        } : false,
      }),
      new MiniCssExtractPlugin({
        filename: isProduction ? 'css/[name].[contenthash:8].css' : 'css/[name].css',
        chunkFilename: isProduction ? 'css/[name].[contenthash:8].chunk.css' : 'css/[name].chunk.css',
      }),
      new CopyPlugin({
        patterns: [
          {
            from: 'public',
            to: '.',
            globOptions: {
              ignore: ['**/index.html'],
            },
          },
        ],
      }),
      ...(isProduction ? [
        new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 8192,
          minRatio: 0.8,
        }),
        new CompressionPlugin({
          algorithm: 'brotliCompress',
          test: /\.(js|css|html|svg)$/,
          threshold: 8192,
          minRatio: 0.8,
          filename: '[path][base].br',
        }),
        new WorkboxPlugin.GenerateSW({
          clientsClaim: true,
          skipWaiting: true,
          exclude: [/\.map$/, /manifest$/, /\.js$/],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis|gstatic\.com/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
                },
              },
            },
            {
              urlPattern: /api/,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                networkTimeoutSeconds: 5,
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 5, // 5 minutes
                },
              },
            },
          ],
        }),
      ] : []),
      ...(isAnalyze ? [new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        openAnalyzer: true,
      })] : []),
    ].filter(Boolean),
    devServer: {
      hot: true,
      port: 3000,
      historyApiFallback: true,
      compress: true,
      open: false,
      static: {
        directory: path.join(__dirname, 'public'),
      },
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
      proxy: [
        {
          context: ['/api'],
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      ],
    },
    performance: {
      hints: isProduction ? 'warning' : false,
      maxEntrypointSize: 250000,
      maxAssetSize: 250000,
    },
  };
};