module.exports = {
  rules: {
    'at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: ['tailwind', 'screen', 'extend', 'responsive'],
      },
    ],
    extends: 'stylelint-config-rawbot',
  },
};
