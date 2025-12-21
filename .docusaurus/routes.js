import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/Root',
    component: ComponentCreator('/Root', '940'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '1ab'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '94c'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'bce'),
            routes: [
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 1/ros2_module1_chapter1',
                component: ComponentCreator('/docs/Module 1/ros2_module1_chapter1', '2f0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 1/ros2_module1_chapter2',
                component: ComponentCreator('/docs/Module 1/ros2_module1_chapter2', '3fc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 1/ros2_module1_chapter3',
                component: ComponentCreator('/docs/Module 1/ros2_module1_chapter3', '85f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 1/ros2_module1_chapter4',
                component: ComponentCreator('/docs/Module 1/ros2_module1_chapter4', '419'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 2/gazebo_module2_chapter1',
                component: ComponentCreator('/docs/Module 2/gazebo_module2_chapter1', 'e07'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 2/gazebo_module2_chapter2',
                component: ComponentCreator('/docs/Module 2/gazebo_module2_chapter2', '4ff'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 2/gazebo_module2_chapter3',
                component: ComponentCreator('/docs/Module 2/gazebo_module2_chapter3', '0d5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 2/gazebo_module2_chapter4',
                component: ComponentCreator('/docs/Module 2/gazebo_module2_chapter4', '985'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 2/gazebo_module2_chapter5',
                component: ComponentCreator('/docs/Module 2/gazebo_module2_chapter5', '248'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 2/gazebo_module2_chapter6',
                component: ComponentCreator('/docs/Module 2/gazebo_module2_chapter6', 'b3d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 2/gazebo_module2_chapter7',
                component: ComponentCreator('/docs/Module 2/gazebo_module2_chapter7', '03d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 3/isaac_module3_chapter1',
                component: ComponentCreator('/docs/Module 3/isaac_module3_chapter1', 'a31'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 3/isaac_module3_chapter2',
                component: ComponentCreator('/docs/Module 3/isaac_module3_chapter2', '668'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 3/isaac_module3_chapter3',
                component: ComponentCreator('/docs/Module 3/isaac_module3_chapter3', 'a13'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 3/isaac_module3_chapter4',
                component: ComponentCreator('/docs/Module 3/isaac_module3_chapter4', 'a3d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 3/isaac_module3_chapter5',
                component: ComponentCreator('/docs/Module 3/isaac_module3_chapter5', '2a9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 3/isaac_module3_chapter6',
                component: ComponentCreator('/docs/Module 3/isaac_module3_chapter6', '0e7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 4/vla_module4_capstone',
                component: ComponentCreator('/docs/Module 4/vla_module4_capstone', 'ddb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 4/vla_module4_chapter1',
                component: ComponentCreator('/docs/Module 4/vla_module4_chapter1', '39c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 4/vla_module4_chapter2',
                component: ComponentCreator('/docs/Module 4/vla_module4_chapter2', '655'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/Module 4/vla_module4_chapter3',
                component: ComponentCreator('/docs/Module 4/vla_module4_chapter3', '6f7'),
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
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
