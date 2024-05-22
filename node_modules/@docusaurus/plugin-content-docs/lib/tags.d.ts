/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/// <reference path="../src/plugin-content-docs.d.ts" />
import type { VersionTags } from './types';
import type { DocMetadata } from '@docusaurus/plugin-content-docs';
export declare function getVersionTags(docs: DocMetadata[]): VersionTags;
