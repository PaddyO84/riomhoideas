const sheetName = 'Sheet1';

function doPost(e) {
  try {
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

    const name = escapeFormula(e.parameter.name);
    const email = escapeFormula(e.parameter.email);
    const projectType = escapeFormula(e.parameter.projectType);
    const details = escapeFormula(e.parameter.details);
    
    // Check for existing inquiry to avoid duplicates on retries
    const data = sheet.getDataRange().getValues();
    let rowIndex = -1;
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
    const emailSubject = `New Project Inquiry: ${e.parameter.projectType} from ${e.parameter.name}`;
    const emailBody = `You have received a new inquiry from the website contact form!

Name: ${e.parameter.name}
Email: ${e.parameter.email}
Project Type: ${e.parameter.projectType}

Project Details:
${e.parameter.details}

Submitted at: ${timestamp}
`;
    MailApp.sendEmail(emailTo, emailSubject, emailBody);

    // Update status to Emailed upon successful send
    sheet.getRange(rowIndex, 6).setValue('Emailed');

    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'success', 'row': sheet.getLastRow() }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': error }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
