module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: ['@liip-lausanne', 'plugin:prettier/recommended'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
};
