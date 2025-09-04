const { registerTransforms } = require('@tokens-studio/sd-transforms');

module.exports = {
  source: ['tokens.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/css/',
      files: [
        {
          destination: 'variables.css',
          format: 'css/variables'
        }
      ]
    }
  },
  hooks: {
    prebuild: () => registerTransforms()
  }
};
