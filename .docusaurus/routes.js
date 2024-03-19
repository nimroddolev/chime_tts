import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/chime_tts/blog',
    component: ComponentCreator('/chime_tts/blog', '364'),
    exact: true
  },
  {
    path: '/chime_tts/blog/archive',
    component: ComponentCreator('/chime_tts/blog/archive', 'cda'),
    exact: true
  },
  {
    path: '/chime_tts/blog/first-blog-post',
    component: ComponentCreator('/chime_tts/blog/first-blog-post', '38b'),
    exact: true
  },
  {
    path: '/chime_tts/blog/long-blog-post',
    component: ComponentCreator('/chime_tts/blog/long-blog-post', '178'),
    exact: true
  },
  {
    path: '/chime_tts/blog/mdx-blog-post',
    component: ComponentCreator('/chime_tts/blog/mdx-blog-post', '107'),
    exact: true
  },
  {
    path: '/chime_tts/blog/tags',
    component: ComponentCreator('/chime_tts/blog/tags', '481'),
    exact: true
  },
  {
    path: '/chime_tts/blog/tags/docusaurus',
    component: ComponentCreator('/chime_tts/blog/tags/docusaurus', '048'),
    exact: true
  },
  {
    path: '/chime_tts/blog/tags/facebook',
    component: ComponentCreator('/chime_tts/blog/tags/facebook', 'f16'),
    exact: true
  },
  {
    path: '/chime_tts/blog/tags/hello',
    component: ComponentCreator('/chime_tts/blog/tags/hello', '3a4'),
    exact: true
  },
  {
    path: '/chime_tts/blog/tags/hola',
    component: ComponentCreator('/chime_tts/blog/tags/hola', '2e2'),
    exact: true
  },
  {
    path: '/chime_tts/blog/welcome',
    component: ComponentCreator('/chime_tts/blog/welcome', '838'),
    exact: true
  },
  {
    path: '/chime_tts/markdown-page',
    component: ComponentCreator('/chime_tts/markdown-page', '99f'),
    exact: true
  },
  {
    path: '/chime_tts/docs',
    component: ComponentCreator('/chime_tts/docs', '013'),
    routes: [
      {
        path: '/chime_tts/docs',
        component: ComponentCreator('/chime_tts/docs', '175'),
        routes: [
          {
            path: '/chime_tts/docs',
            component: ComponentCreator('/chime_tts/docs', 'c32'),
            routes: [
              {
                path: '/chime_tts/docs/category/tutorial---basics',
                component: ComponentCreator('/chime_tts/docs/category/tutorial---basics', '52d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/category/tutorial---extras',
                component: ComponentCreator('/chime_tts/docs/category/tutorial---extras', 'c2e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/getting-started',
                component: ComponentCreator('/chime_tts/docs/getting-started', '02e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/intro',
                component: ComponentCreator('/chime_tts/docs/intro', '44a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-basics/congratulations',
                component: ComponentCreator('/chime_tts/docs/tutorial-basics/congratulations', 'ab9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-basics/create-a-blog-post',
                component: ComponentCreator('/chime_tts/docs/tutorial-basics/create-a-blog-post', '7f3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-basics/create-a-document',
                component: ComponentCreator('/chime_tts/docs/tutorial-basics/create-a-document', '530'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-basics/create-a-page',
                component: ComponentCreator('/chime_tts/docs/tutorial-basics/create-a-page', '406'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-basics/deploy-your-site',
                component: ComponentCreator('/chime_tts/docs/tutorial-basics/deploy-your-site', '519'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-basics/markdown-features',
                component: ComponentCreator('/chime_tts/docs/tutorial-basics/markdown-features', '7c7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-extras/manage-docs-versions',
                component: ComponentCreator('/chime_tts/docs/tutorial-extras/manage-docs-versions', '789'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/chime_tts/docs/tutorial-extras/translate-your-site',
                component: ComponentCreator('/chime_tts/docs/tutorial-extras/translate-your-site', 'ccb'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/chime_tts/',
    component: ComponentCreator('/chime_tts/', '229'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
