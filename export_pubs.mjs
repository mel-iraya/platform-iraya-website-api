import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// To avoid Vite/ESM alias issues with imports in publications.js, 
// we read it as text, remove the import statements, and eval the array.
const pubPath = path.join(__dirname, '..', 'data', 'publications.js')
let code = fs.readFileSync(pubPath, 'utf-8')

// Remove imports
code = code.replace(/import\s+.*?from\s+['"].*?['"]\r?\n/g, '')
// Replace export const
code = code.replace(/export\s+const\s+publications1\s*=\s*/, 'const publications1 = ')
code += '\n\nconsole.log(JSON.stringify(publications1, null, 2))'

// Note: we can't eval easily if the image variables are unassigned.
// Since imports are removed, the variables like greenWorld are undefined.
// We need to extract the aliases instead.

let extractedCode = fs.readFileSync(pubPath, 'utf-8')
const importMap = {}
const importRegex = /import\s+(\w+)\s+from\s+['"]([^'"]+)['"]/g
let match
while ((match = importRegex.exec(extractedCode)) !== null) {
    let p = match[2]
    if (p.startsWith('@/')) p = '/' + p.slice(2)
    importMap[match[1]] = p
}

// Remove imports from extracted code
extractedCode = extractedCode.replace(/import\s+.*?from\s+['"].*?['"]\r?\n/g, '')
extractedCode = extractedCode.replace(/export\s+const\s+publications1\s*=\s*/, 'const publications1 = ')

// Prepend variable definitions as strings
let vars = ''
for (const [key, val] of Object.entries(importMap)) {
    vars += `const ${key} = "${val}";\n`
}

extractedCode = "import fs from 'fs';\n" + vars + '\n' + extractedCode + '\nfs.writeFileSync("pubs.json", JSON.stringify(publications1, null, 2), "utf-8")'

fs.writeFileSync('temp_eval.mjs', extractedCode)
