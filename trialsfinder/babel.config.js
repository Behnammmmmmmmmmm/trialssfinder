module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        browsers: ['>0.25%', 'not dead']
      },
      modules: false,
      useBuiltIns: false
    }],
    ['@babel/preset-react', {
      runtime: 'automatic'
    }],
    '@babel/preset-typescript'
  ],
  plugins: [
    '@babel/plugin-syntax-dynamic-import'
  ],
  env: {
    production: {
      plugins: [
        ['babel-plugin-transform-react-remove-prop-types', {
          mode: 'remove',
          removeImport: true
        }]
      ]
    }
  }
};