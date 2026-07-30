/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {type: 'category', label: 'Quick Start', items: ['quick-start/installing-chime-tts', 'quick-start/adding-the-integration', 'quick-start/additional-requirements']},
    {
      type: 'category',
      label: 'Configuration (Settings Panel Beta)',
      link: {type: 'doc', id: 'documentation/configuration'},
      items: [
        'documentation/configuration/tts-defaults-fallback',
        'documentation/configuration/playback-options',
        'documentation/configuration/audio-files-folders',
        'documentation/configuration/action-script-options',
      ],
    },
    {type: 'doc', id: 'documentation/chimes', label: 'Chimes'},
    {type: 'doc', id: 'documentation/chime-sets', label: 'Chime Sets (Beta)'},
    {type: 'category', label: 'Notification Profiles', link: {type: 'doc', id: 'documentation/notify/index'}, items: ['documentation/notify/adding', 'documentation/notify/sending']},
    {type: 'category', label: 'Actions and Parameters', link: {type: 'doc', id: 'documentation/actions/index'}, items: ['documentation/actions/say-action/index', 'documentation/actions/say-action/parameters', 'documentation/actions/say-action/examples', 'documentation/actions/say_url-action/index', 'documentation/actions/clear_cache-action', 'documentation/actions/replay-action']},
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
