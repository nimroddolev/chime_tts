/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/// <reference path="../src/plugin-content-docs.d.ts" />
import type { LoadedContent } from '@docusaurus/plugin-content-docs';
import type { TranslationFile } from '@docusaurus/types';
export declare function getLoadedContentTranslationFiles(loadedContent: LoadedContent): TranslationFile[];
export declare function translateLoadedContent(loadedContent: LoadedContent, translationFiles: TranslationFile[]): LoadedContent;
