const test = require('node:test');
const assert = require('node:assert');

// Mock Google Apps Script environment
global.LockService = {
  getScriptLock: () => ({
    waitLock: () => true,
    releaseLock: () => true,
  })
};

let cacheStore = {};
global.CacheService = {
  getScriptCache: () => ({
    get: (key) => cacheStore[key] || null,
    put: (key, val) => { cacheStore[key] = val; },
    getAll: (keys) => {
      const result = {};
      keys.forEach(k => {
        if (cacheStore[k] !== undefined) result[k] = cacheStore[k];
      });
      return result;
    },
    putAll: (obj) => {
      Object.assign(cacheStore, obj);
    }
  })
};

let rows = [];
const mockSheet = {
  getLastRow: () => rows.length,
  appendRow: (row) => rows.push(row),
  getRange: (row, col, numRows, numCols) => ({
    setNumberFormat: () => {},
    setValue: (val) => {
      if (rows[row - 1]) rows[row - 1][col - 1] = val;
    },
    getValues: () => {
      const slice = rows.slice(row - 1, row - 1 + (numRows || 1));
      return slice.map(r => r.slice(col - 1, col - 1 + (numCols || 1)));
    }
  })
};

global.SpreadsheetApp = {
  getActiveSpreadsheet: () => ({
    getSheetByName: () => mockSheet
  })
};

let sentEmails = [];
global.MailApp = {
  sendEmail: (to, subject, body) => {
    sentEmails.push({ to, subject, body });
  }
};

global.ContentService = {
  MimeType: { JSON: 'application/json' },
  createTextOutput: (text) => ({
    text,
    setMimeType: (mime) => ({ text, mime })
  })
};

const {
  escapeFormula,
  validateInputs,
  enforceRateLimits,
  findRecentDuplicateRow,
  doPost
} = require('../apps-script/Code.js');

test.beforeEach(() => {
  cacheStore = {};
  rows = [];
  sentEmails = [];
});

test('Formula Escaping Helper covers Excel/CSV injection triggers', () => {
  assert.strictEqual(escapeFormula('=SUM(1,2)'), "'=SUM(1,2)");
  assert.strictEqual(escapeFormula('+cmd|'), "'+cmd|");
  assert.strictEqual(escapeFormula('-cmd'), "'-cmd");
  assert.strictEqual(escapeFormula('@test'), "'@test");
  assert.strictEqual(escapeFormula('|calc'), "'|calc");
  assert.strictEqual(escapeFormula('%tag'), "'%tag");
  assert.strictEqual(escapeFormula('\tleadingTab'), "'\tleadingTab");
  assert.strictEqual(escapeFormula('Normal string'), 'Normal string');
  assert.strictEqual(escapeFormula(12345), 12345);
});

test('Honeypot detection throws spam error', () => {
  assert.throws(() => {
    validateInputs({ honeypot: 'bot filled this' });
  }, /Spam detected/);
});

test('Input length validation enforces maximum thresholds', () => {
  assert.throws(() => {
    validateInputs({ name: 'A'.repeat(201), email: 'test@example.com' });
  }, /Input exceeds maximum length/);

  assert.throws(() => {
    validateInputs({ email: 'A'.repeat(201) + '@example.com' });
  }, /Input exceeds maximum length/);

  assert.throws(() => {
    validateInputs({ email: 'test@example.com', projectType: 'A'.repeat(101) });
  }, /Input exceeds maximum length/);

  assert.throws(() => {
    validateInputs({ email: 'test@example.com', details: 'A'.repeat(5001) });
  }, /Input exceeds maximum length/);
});

test('Email validation rejects malformed email addresses', () => {
  const invalidEmails = ['plainaddress', 'missingdomain@', '@missinguser.com', 'spaces in@mail.com'];
  for (const email of invalidEmails) {
    assert.throws(() => {
      validateInputs({ email, name: 'Alice' });
    }, /Invalid email address/);
  }

  const valid = validateInputs({ email: ' user.name@domain.co.uk ', name: 'Alice' });
  assert.strictEqual(valid.email, 'user.name@domain.co.uk');
});

test('Rate limiting triggers on per-email threshold', () => {
  const cache = global.CacheService.getScriptCache();
  cacheStore['rate_limit_user@example.com'] = '5';

  assert.throws(() => {
    enforceRateLimits(cache, 'user@example.com');
  }, /Rate limit exceeded/);
});

test('Rate limiting triggers on global threshold', () => {
  const cache = global.CacheService.getScriptCache();
  cacheStore['rate_limit_global'] = '50';

  assert.throws(() => {
    enforceRateLimits(cache, 'newuser@example.com');
  }, /Rate limit exceeded/);
});

test('doPost processes a valid inquiry end-to-end', () => {
  const res = doPost({
    parameter: {
      name: 'Eoin O Donnell',
      email: 'eoin@example.com',
      projectType: 'Custom App Development',
      details: 'Need a high-performance Kotlin Multiplatform application.'
    }
  });

  const parsed = JSON.parse(res.text);
  assert.strictEqual(parsed.result, 'success');
  assert.strictEqual(sentEmails.length, 1);
  assert.strictEqual(sentEmails[0].to, 'contact@riomhoideas.ie');
});

test('doPost handles and catches internal errors safely', () => {
  const res = doPost({
    parameter: {
      honeypot: 'bot'
    }
  });

  const parsed = JSON.parse(res.text);
  assert.strictEqual(parsed.result, 'error');
  assert.strictEqual(parsed.error, 'An internal server error occurred.');
});
