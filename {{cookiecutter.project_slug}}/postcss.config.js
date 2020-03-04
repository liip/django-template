const purgecss = require('@fullhuman/postcss-purgecss')({
  content: ['./{{ cookiecutter.project_slug }}/**/*.html'],

  defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || [],
});

module.exports = {
  plugins: [
    require('postcss-import'),
    require('tailwindcss'),
    require('precss'),
    require('postcss-extend-rule'),
    require('postcss-preset-env'),
    ...(process.env.NODE_ENV === 'production' ? [purgecss] : []),
  ],
};
