// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Official Chime TTS Wiki',
  tagline: 'The official Chime TTS wiki including documentation, explanations and usage examples',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://github.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/chime_tts/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'nimroddolev', // Usually your GitHub org/user name.
  projectName: 'chime_tts', // Usually your repo name.
  deploymentBranch: 'gh-pages',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          // editUrl:
          //   'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          // editUrl:
          //   'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      // image: 'img/docusaurus-social-card.jpg',
      image: 'img/chime_tts.jpg',
      navbar: {
        title: 'Home',
        logo: {
          alt: 'Chime TTS Logo',
          src: 'img/chime_tts.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Tutorial',
          },
          // { to: '/blog', label: 'Blog', position: 'left' },
          {
            href: 'https://github.com/nimroddolev/chime_tts',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Chime TTS',
                to: '/docs/getting-started',
              },
              {
                label: 'Quick Start',
                to: '/docs/category/quick-start',
              },
              {
                label: 'Say Service',
                to: '/docs/category/say-url-service',
              },
              {
                label: 'Say URL Service',
                to: '/docs/category/say-url-service',
              },
              {
                label: 'Clear Cache Service',
                to: '/docs/clear-cache-service',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Home Assistant Forum',
                href: 'https://community.home-assistant.io/t/chime-tts-play-audio-before-after-tts-audio-lag-free/578430',
              },
              {
                label: 'Discussion on GitHub',
                href: 'https://github.com/nimroddolev/chime_tts/discussions',
              },
            ],
          },
          {
            title: 'More',
            items: [
              // {
              //   label: 'Blog',
              //   to: '/blog',
              // },
              {
                label: 'GitHub',
                href: 'https://github.com/nimroddolev/chime_tts',
              },
              {
                label: 'Have an Issue?',
                href: 'https://github.com/nimroddolev/chime_tts/issues',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Nimrod Dolev.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
