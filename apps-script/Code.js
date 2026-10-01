const sheetName = 'Sheet1';

/**
 * Escapes characters that trigger formula execution in spreadsheet software.
 */
function escapeFormula(val) {
  if (typeof val === 'string' && /^[=+\-@\t\r%|]/.test(val)) {
    return "'" + val;
  }
  return val;
}

/**
 * Validates incoming parameters against abuse, honeypot, and format rules.
 */
function validateInputs(parameter) {
  if (parameter.honeypot) {
    throw new Error("Spam detected.");
  }

  const rawName = parameter.name || '';
  const rawEmail = parameter.email || '';
  const rawType = parameter.projectType || '';
  const rawDetails = parameter.details || '';

  if (rawName.length > 200 || rawEmail.length > 200 || rawType.length > 100 || rawDetails.length > 5000) {
    throw new Error("Input exceeds maximum length.");
  }

  const email = rawEmail.trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error("Invalid email address.");
  }

  return {
    rawName,
    rawEmail,
    email,
    rawType,
    rawDetails,
    name: escapeFormula(rawName),
    escapedEmail: escapeFormula(rawEmail),
    projectType: escapeFormula(rawType),
    details: escapeFormula(rawDetails)
  };
}

/**
 * Checks and updates rate limits using CacheService batch operations.
 */
function enforceRateLimits(cache, email) {
  const emailCacheKey = 'rate_limit_' + email;
  const globalCacheKey = 'rate_limit_global';

  const cached = cache.getAll([emailCacheKey, globalCacheKey]);
  const emailCount = parseInt(cached[emailCacheKey] || '0', 10);
  const globalCount = parseInt(cached[globalCacheKey] || '0', 10);

  if (emailCount >= 5 || globalCount >= 50) {
    throw new Error("Rate limit exceeded.");
  }

  cache.putAll({
    [emailCacheKey]: (emailCount + 1).toString(),
    [globalCacheKey]: (globalCount + 1).toString()
  }, 3600);
}

/**
 * Scans recent rows to check for duplicate submission within 10 minutes.
 */
function findRecentDuplicateRow(sheet, rawName, rawEmail, rawType, rawDetails) {
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) return -1;

  // Scan only the most recent rows (up to 25) instead of the entire sheet
  const rowsToScan = Math.min(25, lastRow - 1);
  const startRow = lastRow - rowsToScan + 1;
  const values = sheet.getRange(startRow, 1, rowsToScan, 5).getValues();
  const now = new Date().getTime();

  for (let i = values.length - 1; i >= 0; i--) {
    const row = values[i];
    const rowTime = new Date(row[0]).getTime();

    // Stop scanning if the row is older than 10 minutes
    if (now - rowTime > 10 * 60 * 1000) {
      break;
    }

    if (String(row[1]) === rawName && String(row[2]) === rawEmail && String(row[3]) === rawType && String(row[4]) === rawDetails) {
      return startRow + i;
    }
  }

  return -1;
}

function doPost(e) {
  try {
    const params = (e && e.parameter) ? e.parameter : {};
    const validated = validateInputs(params);

    const lock = LockService.getScriptLock();
    let rowIndex = -1;

    try {
      lock.waitLock(10000);

      const cache = CacheService.getScriptCache();
      enforceRateLimits(cache, validated.email);

      const doc = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = doc.getSheetByName(sheetName);

      // If it's the first time, add headers and format columns
      if (sheet.getLastRow() === 0) {
        sheet.appendRow(['Timestamp', 'Name', 'Email', 'Project Type', 'Details', 'Status']);
        sheet.getRange("B:E").setNumberFormat('@'); // Format B-E as plain text
      }

      // Check for recent duplicate to handle retries gracefully
      rowIndex = findRecentDuplicateRow(sheet, validated.rawName, validated.rawEmail, validated.rawType, validated.rawDetails);

      const timestamp = new Date();

      if (rowIndex === -1) {
        sheet.appendRow([
          timestamp,
          validated.name,
          validated.escapedEmail,
          validated.projectType,
          validated.details,
          'Pending'
        ]);
        rowIndex = sheet.getLastRow();
      } else {
        sheet.getRange(rowIndex, 1).setValue(timestamp);
        sheet.getRange(rowIndex, 6).setValue('Pending');
      }

      // Send the email notification
      const emailTo = "contact@riomhoideas.ie";
      const emailSubject = `New Project Inquiry: ${validated.projectType} from ${validated.name}`;
      const emailBody = `You have received a new inquiry from the website contact form!

Name: ${validated.name}
Email: ${validated.escapedEmail}
Project Type: ${validated.projectType}

Project Details:
${validated.details}

Submitted at: ${timestamp}
`;
      MailApp.sendEmail(emailTo, emailSubject, emailBody);

      sheet.getRange(rowIndex, 6).setValue('Emailed');

    } finally {
      lock.releaseLock();
    }

    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'success', 'row': rowIndex }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    console.error("Error in doPost:", error, error.stack);
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'An internal server error occurred.' }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    escapeFormula,
    validateInputs,
    enforceRateLimits,
    findRecentDuplicateRow,
    doPost
  };
}
