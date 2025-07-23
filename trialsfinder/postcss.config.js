module.exports = {
  plugins: [
    require('postcss-import'),
    require('postcss-preset-env')({
      stage: 1,
      features: {
        'custom-properties': true,
        'custom-media-queries': true,
        'nesting-rules': true,
        'focus-visible-pseudo-class': true,
        'prefers-color-scheme-query': true
      },
      autoprefixer: {
        grid: 'autoplace'
      }
    }),
    require('autoprefixer')
  ]
};