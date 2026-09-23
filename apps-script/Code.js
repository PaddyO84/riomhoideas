const sheetName = 'Sheet1';

function doPost(e) {
  try {
    // Abuse checks: honeypot, length limits, rate limits
    if (e.parameter.honeypot) {
      throw new Error("Spam detected.");
    }
    // Note: Captcha validation is skipped because there is no frontend integration for it yet.

    const rawName = e.parameter.name || '';
    const rawEmail = e.parameter.email || '';
    const rawType = e.parameter.projectType || '';
    const rawDetails = e.parameter.details || '';

    if (rawName.length > 200 || rawEmail.length > 200 || rawType.length > 100 || rawDetails.length > 5000) {
      throw new Error("Input exceeds maximum length.");
    }

    const cache = CacheService.getScriptCache();
    const cacheKey = 'rate_limit_' + rawEmail; // Use email for rate limiting
    const count = parseInt(cache.get(cacheKey) || '0', 10);
    if (count >= 5) {
      throw new Error("Rate limit exceeded.");
    }
    cache.put(cacheKey, (count + 1).toString(), 3600); // 1 hour cap

    const lock = LockService.getScriptLock();
    let rowIndex = -1;

    try {
      lock.waitLock(10000);
      
      const doc = SpreadsheetApp.getActiveSpreadsheet();
      const sheet = doc.getSheetByName(sheetName);
      
      // If it's the first time, add headers
      if (sheet.getLastRow() === 0) {
        sheet.appendRow(['Timestamp', 'Name', 'Email', 'Project Type', 'Details', 'Status']);
      }

      const escapeFormula = (val) => {
        if (typeof val === 'string' && /^[=+\-@]/.test(val)) {
          return "'" + val;
        }
        return val;
      };

      const name = escapeFormula(rawName);
      const email = escapeFormula(rawEmail);
      const projectType = escapeFormula(rawType);
      const details = escapeFormula(rawDetails);
      
      // Check for existing inquiry to avoid duplicates on retries
      const data = sheet.getDataRange().getValues();
      for (let i = data.length - 1; i >= 1; i--) {
        const row = data[i];
        if (row[1] === name && row[2] === email && row[3] === projectType && row[4] === details) {
          rowIndex = i + 1; // 1-based index for Google Sheets
          break;
        }
      }

      const timestamp = new Date();
      
      if (rowIndex === -1) {
        // Append the new data with Pending status
        sheet.appendRow([
          timestamp,
          name,
          email,
          projectType,
          details,
          'Pending'
        ]);
        rowIndex = sheet.getLastRow();
      } else {
        // Update existing row's timestamp and reset status to Pending
        sheet.getRange(rowIndex, 1).setValue(timestamp);
        sheet.getRange(rowIndex, 6).setValue('Pending');
      }

      // Send the email notification
      const emailTo = "contact@riomhoideas.ie";
      const emailSubject = `New Project Inquiry: ${projectType} from ${name}`;
      const emailBody = `You have received a new inquiry from the website contact form!

Name: ${name}
Email: ${email}
Project Type: ${projectType}

Project Details:
${details}

Submitted at: ${timestamp}
`;
      MailApp.sendEmail(emailTo, emailSubject, emailBody);

      // Update status to Emailed upon successful send
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
