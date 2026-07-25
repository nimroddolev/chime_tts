import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const servicesPath = path.join(root, 'custom_components/chime_tts/services.yaml');
const metadataPath = path.join(root, 'docs/data/reference-metadata.json');
const outputPath = path.join(root, 'docs/generated/reference-data.json');

/**
 * Extract the Home Assistant service fields needed by the documentation. This
 * deliberately reads the committed services.yaml snapshot rather than the
 * running integration, so site builds are reproducible and dependency-free.
 */
function parseServices(source) {
  const services = {};
  let currentService;
  let currentField;
  let currentAttribute;
  let inFields = false;

  for (const line of source.split(/\r?\n/)) {
    const service = line.match(/^([a-z][\w_]+):$/);
    if (service) {
      currentService = service[1];
      services[currentService] = { fields: [] };
      currentField = undefined;
      currentAttribute = undefined;
      inFields = false;
      continue;
    }
    if (!currentService) continue;
    if (/^  fields:$/.test(line)) {
      inFields = true;
      continue;
    }
    if (!inFields) continue;
    const field = line.match(/^    ([a-z][\w_]+):$/);
    if (field) {
      currentField = { key: field[1] };
      services[currentService].fields.push(currentField);
      currentAttribute = undefined;
      continue;
    }
    if (!currentField) continue;
    const attribute = line.match(/^      (name|description|example|default|required):\s*(.*)$/);
    if (attribute) {
      const [, key, rawValue] = attribute;
      currentField[key] = rawValue.replace(/^['"]|['"]$/g, '');
      currentAttribute = key;
      continue;
    }
    if (currentAttribute === 'description' && /^        \S/.test(line)) {
      currentField.description += ` ${line.trim()}`;
    }
  }
  return services;
}

const services = parseServices(fs.readFileSync(servicesPath, 'utf8'));
const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
const references = {
  generatedFrom: 'custom_components/chime_tts/services.yaml',
  actions: Object.fromEntries(
    ['say', 'say_url', 'clear_cache'].map((service) => [service, services[service]?.fields ?? []]),
  ),
  configuration: metadata.configuration,
  notifyProfiles: metadata.notifyProfiles,
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${JSON.stringify(references, null, 2)}\n`);
