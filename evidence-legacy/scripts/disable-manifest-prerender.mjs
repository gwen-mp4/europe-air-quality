import fs from 'node:fs';
import path from 'node:path';

const routeFile = path.resolve(
	'node_modules/@evidence-dev/evidence/template/src/pages/manifest.webmanifest/+server.js'
);

if (!fs.existsSync(routeFile)) {
	throw new Error(`Evidence manifest route not found: ${routeFile}`);
}

const source = fs.readFileSync(routeFile, 'utf8');
const updated = source.replace(/export const prerender = true;/, 'export const prerender = false;');

if (source === updated) {
	console.log('Evidence manifest route already configured.');
} else {
	fs.writeFileSync(routeFile, updated);
	console.log('Disabled Evidence manifest route prerendering.');
}
