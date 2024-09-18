// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Locally combine TTS and audio in Home Assistant.',
  tagline: 'The official site for Chime TTS documentation, explanations and usage examples.',
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
          alt: 'Chime TTS logo',
          src: 'img/chime_tts.png',
        },
        items: [
          // {
          //   type: 'docSidebar',
          //   sidebarId: 'tutorialSidebar',
          //   position: 'left',
          //   label: 'Wiki',
          // },
          {
            to: '/docs/getting-started',
            label: 'Chime TTS',
            position: 'left'
          },
          // { to: '/docs/quick-start', label: 'Quick Start', position: 'left' },
          {
            to: "/docs/quick-start/",
            label: "Quick Start",
            position: "left",
            items: [
              {
                type: "doc",
                label: "Installation",
                docId: "quick-start/installing-chime-tts"
              },
              {
                type: "doc",
                label: "Adding the Integration",
                docId: "quick-start/adding-the-integration"
              },
            ]
          },
          {
            to: "docs/documentation/",
            label: "Documentation",
            position: "left",
            items: [
              {
                type: "doc",
                label: "Configuration",
                docId: "documentation/configuration"
              },
              {
                type: "doc",
                label: "Say Action",
                docId: "documentation/actions/say-action/index"
              },
              {
                type: "doc",
                label: "Say URL Action",
                docId: "documentation/actions/say_url-action/index"
              },
              {
                type: "doc",
                label: "Replay Action",
                docId: "documentation/actions/replay-action"
              },
              {
                type: "doc",
                label: "Clear Cache Action",
                docId: "documentation/actions/clear_cache-action"
              },
              {
                type: "doc",
                label: "Notify",
                docId: "documentation/notify/index"
              },
            ],
          },
          {
            to: '/docs/support',
            label: 'Support',
            position: 'left'
          },
          {
            href: "https://www.buymeacoffee.com/nimroddolev",
            position: "right",
            className: "header-buymeacoffee-link",
            "aria-label": "Buy me a coffee",
          },
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
                to: '/docs/quick-start/',
              },
              {
                label: "Documentation",
                to: "docs/documentation/"
              },
              {
                label: 'Support',
                to: '/docs/support/',
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
  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        fromExtensions: ['html', 'htm'], // /myPage.html -> /myPage
        toExtensions: ['exe', 'zip'], // /myAsset -> /myAsset.zip (if latter exists)
        redirects: [
          // // /docs/oldDoc -> /docs/newDoc
          // {
          //   to: '/docs/newDoc',
          //   from: '/docs/oldDoc',
          // },
          // // Redirect from multiple old paths to the new path
          // {
          //   to: '/docs/newDoc2',
          //   from: ['/docs/oldDocFrom2019', '/docs/legacyDocFrom2016'],
          // },
        ],
        createRedirects(existingPath) {
          var replacements = [
            {
              from: "docs/documentation/say",
              to: "docs/documentation/actions/say"
            },
            {
              from: "docs/documentation/clear",
              to: "docs/documentation/actions/clear"
            },
            {
              from: "docs/quick-start/configuration",
              to: "docs/documentation/configuration"
            },
            // Rename from "service" to "action"
            {
              from: "docs/documentation/services",
              to: "docs/documentation/actions"
            },
            {
              from: "docs/documentation/services/clear_cache-service",
              to: "docs/documentation/actions/clear_cache-action"
            },
            {
              from: "docs/documentation/services/replay-service",
              to: "docs/documentation/actions/replay-action"
            },
            {
              from: "docs/documentation/services/say_url-service",
              to: "docs/documentation/actions/say_url-action"
            },
            {
              from: "docs/documentation/services/say_url-service/examples",
              to: "docs/documentation/actions/say_url-action/examples"
            },
            {
              from: "docs/documentation/services/say_url-service/parameters",
              to: "docs/documentation/actions/say_url-action/parameters"
            },
            {
              from: "docs/documentation/services/say-service",
              to: "docs/documentation/actions/say-action"
            },
            {
              from: "docs/documentation/services/say-service/examples",
              to: "docs/documentation/actions/say-action/examples"
            },
            {
              from: "docs/documentation/services/say-service/parameters",
              to: "docs/documentation/actions/say-action/parameters"
            },
          ];
          for (var i = 0; i < replacements.length; i++) {
            var replacement = replacements[i];
            if (existingPath.includes(replacement["from"])) {
              return [existingPath.replace(replacement["from"], replacement["to"])];
            }
          }
          return undefined; // Return a falsy value: no redirect created
        },
      },
    ],
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
      },

    ],
  ],
};

export default config;
