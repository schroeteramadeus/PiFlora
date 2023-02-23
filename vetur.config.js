// vetur.config.js
//from https://stackoverflow.com/questions/66985894/vetur-cant-find-package-json
/** @type {import('vls').VeturConfig} */
module.exports = {
    // **optional** default: `{}`
    // override vscode settings
    // Notice: It only affects the settings used by Vetur.
    //settings: {
    //  "vetur.useWorkspaceDependencies": true,
    //  "vetur.experimental.templateInterpolationService": true
    //},
    // **optional** default: `[{ root: './' }]`
    // support monorepos
    projects: [
        {
          root: './vue', // root of your vue project (should contain package.json)
          //package: './package.json', // Relative to root property, don't change this.
          //tsconfig: './tsconfig.json',  // Relative to root property, don't change this.
        }
    ]
  }