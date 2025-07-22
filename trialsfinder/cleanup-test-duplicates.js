const fs = require('fs');
const path = require('path');

// Remove duplicate mock files from parent test directory
const duplicateMocks = [
  '../test/__mocks__/axios.ts',
  '../test/__mocks__/fileMock.js',
  '../test/__mocks__/styleMock.js',
  '../test/__mocks__/date-fns.js',
  '../test/__mocks__/react-router-dom.js'
];

duplicateMocks.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    console.log(`Removed duplicate: ${file}`);
  }
});

// Remove duplicate test files
const duplicateTests = [
  '../test/e2e',
  '../test/integration',
  '../test/performance'
];

duplicateTests.forEach(dir => {
  const dirPath = path.join(__dirname, dir);
  if (fs.existsSync(dirPath)) {
    fs.rmSync(dirPath, { recursive: true, force: true });
    console.log(`Removed duplicate directory: ${dir}`);
  }
});

console.log('Cleanup complete!');