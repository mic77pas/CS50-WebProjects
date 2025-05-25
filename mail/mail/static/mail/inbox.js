document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));

  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').onsubmit = send_mail;

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  const emailsView = document.querySelector('#emails-view');
  document.querySelector('#emails-view').innerHTML = `<h4 style="padding-bottom: 8px; margin-left: 2px">${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h4>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      emails.forEach(email => {
        const emailDiv = document.createElement('div');
        emailDiv.className = 'email-entry';
        emailDiv.fontFamily = 'Google Sans'
        emailDiv.style.border = '1px solid gray';
        emailDiv.style.borderRadius = '10px';
        emailDiv.style.padding = '10px';
        emailDiv.style.margin = '5px';
        // Prevent hover from being overwritten (styles.css)
        emailDiv.classList.add(email.read ? 'read' : 'unread');
        emailDiv.style.cursor = 'pointer';

        emailDiv.innerHTML = `
          <strong>${mailbox === 'sent' ? email.recipients.join(', ') : email.sender}</strong>
          &nbsp;&nbsp; ${email.subject}
          <span style="float:right">${email.timestamp}</span>
        `;

        emailsView.appendChild(emailDiv);
        emailDiv.addEventListener('click', () => load_email(email.id));
      })
  });
}


function send_mail(event) {

  event.preventDefault();

  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent');
  });

}


function load_email(id) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  const view = document.querySelector('#email-view');
  view.innerHTML = '';

  // Get the email data
  fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      // Mark as read
      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ read: true })
      });

      // Display email fields
      view.innerHTML = `
        <ul style="padding-left: 1em; margin-left: 0;">
          <li><strong>From:</strong> ${email.sender}</li>
          <li><strong>To:</strong> ${email.recipients.join(', ')}</li>
          <li><strong>Subject:</strong> ${email.subject}</li>
          <li><strong>Timestamp:</strong> ${email.timestamp}</li>
        </ul>
        <hr>
        <p>${email.body}</p>
        <hr>
      `;
      if (email.sender !== document.querySelector('#user-email').innerText) {
        const archiveButton = document.createElement('button');
        archiveButton.className = 'btn btn-warning';
        archiveButton.innerText = email.archived ? 'Unarchive' : 'Archive';
        archiveButton.style.marginRight = '14px';
        archiveButton.style.marginBottom = "10px";

        archiveButton.addEventListener('click', () => {
          fetch(`/emails/${email.id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: !email.archived
            })
          })
          .then(() => load_mailbox('inbox'));
        });

        document.querySelector('#email-view').appendChild(archiveButton);
      }

      const replyButton = document.createElement('button');
      replyButton.className = 'btn btn-primary';
      replyButton.innerText = 'Reply';
      replyButton.style.marginBottom = "10px";

      replyButton.addEventListener('click', () => {
        compose_email();

        // Pre-fill form fields
        document.querySelector('#compose-recipients').value = email.sender;

        let subject = email.subject;
        if (!subject.startsWith("Re: ")) {
          subject = "Re: " + subject;
        }
        document.querySelector('#compose-subject').value = subject;

        document.querySelector('#compose-body').value =
          `\n\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
      });

      document.querySelector('#email-view').appendChild(replyButton);
    });
}