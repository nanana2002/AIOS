# Send Email Node

A MOFA node that provides email sending functionality through SMTP. This node enables automated email delivery with support for various SMTP servers and secure authentication.

## Features

- **SMTP Email Sending**: Send emails through any SMTP server
- **Secure Authentication**: Support for TLS/SSL encryption and app passwords
- **Gmail Integration**: Pre-configured for Gmail SMTP with app password support
- **Flexible Configuration**: Configurable SMTP server settings
- **Environment Variable Support**: Secure credential management
- **MOFA Integration**: Seamless integration with MOFA agent framework

## Installation

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

### Environment Configuration (`.env.secret`)
Required environment variables:

```bash
# Email Account Configuration
EMAIL=your_email@gmail.com
PASSWORD=your_app_password_or_password
RECEIVER_EMAIL=recipient@example.com

# SMTP Server Configuration (optional, defaults to Gmail)
SMTP_SERVER=smtp.gmail.com  # Default: smtp.gmail.com
```

**Note**: For Gmail, you'll need to use an App Password instead of your regular password. See [Gmail App Passwords](https://support.google.com/accounts/answer/185833) for setup instructions.

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email_data` | string | Yes | The email content to send (used as both subject and body) |

### Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `send_email_result` | string | Confirmation message indicating email was sent successfully |

## Usage Example

### Basic Dataflow Configuration

```yaml
# send-email-dataflow.yml
nodes:
  - id: terminal-input
    build: pip install -e ../../node-hub/terminal-input
    path: dynamic
    outputs:
      - data
    inputs:
      send_email_result: send-email-agent/send_email_result
  - id: send-email-agent
    build: pip install -e ../../agent-hub/send-email
    path: send-email
    outputs:
      - send_email_result
    inputs:
      email_data: terminal-input/data
    env:
      IS_DATAFLOW_END: true
      WRITE_LOG: true
```

### Running the Node

1. **Set up environment variables:**
   ```bash
   echo "EMAIL=your_email@gmail.com" > .env.secret
   echo "PASSWORD=your_app_password" >> .env.secret
   echo "RECEIVER_EMAIL=recipient@example.com" >> .env.secret
   ```

2. **Start the MOFA framework:**
   ```bash
   dora up
   ```

3. **Build and start the dataflow:**
   ```bash
   dora build send-email-dataflow.yml
   dora start send-email-dataflow.yml
   ```

4. **Send email content:**
   Type your email message in the terminal input, and it will be sent to the configured recipient.

## Code Example

The core functionality is implemented in `main.py`:

```python
import os
from dotenv import load_dotenv
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@run_agent
def run(agent: MofaAgent):
    load_dotenv(dotenv_path='.env.secret')
    
    # Get email configuration from environment
    sender_email = os.getenv('EMAIL')
    app_password = os.getenv('PASSWORD')
    receiver_email = os.getenv('RECEIVER_EMAIL')
    
    # Create email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    
    # Get email content from input
    data = agent.receive_parameter('email_data')
    message["Subject"] = data
    message.attach(MIMEText(data, "plain"))
    
    # Send email through SMTP
    server = smtplib.SMTP(os.getenv('SMTP_SERVER', "smtp.gmail.com"), 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    
    agent.send_output(agent_output_name='send_email_result', agent_result="Email sent successfully!")

def main():
    agent = MofaAgent(agent_name='send-email-agent')
    run(agent)
```

## Dependencies

- **pyarrow** (>= 5.0.0): For data serialization and arrow format support
- **python-dotenv**: For environment variable management
- **smtplib**: Built-in Python SMTP library (included in standard library)
- **email.mime**: Built-in Python email handling (included in standard library)
- **mofa**: MOFA framework (automatically available in MOFA environment)

## Key Features

### Email Composition
- **Simple Text Emails**: Sends plain text emails with subject and body
- **Unified Content**: Uses input data as both subject and message body
- **MIME Support**: Proper email formatting with MIME multipart messages

### SMTP Configuration
- **Multiple Providers**: Support for Gmail, Outlook, Yahoo, and custom SMTP servers
- **Secure Connection**: TLS encryption for secure email transmission
- **Authentication**: Username/password and app password authentication

### Environment Management
- **Secure Credentials**: Environment variable-based credential storage
- **Flexible Configuration**: Customizable SMTP server settings
- **Development Friendly**: Easy local development with .env.secret files

## Use Cases

### Automated Notifications
- **System Alerts**: Send system status and alert notifications
- **Process Completion**: Notify when automated processes complete
- **Error Reporting**: Email error reports and exceptions
- **Status Updates**: Regular status updates and reports

### Business Workflows
- **Order Confirmations**: Send order and transaction confirmations
- **Report Distribution**: Automated distribution of reports and analytics
- **Customer Communication**: Automated customer notifications
- **Internal Communications**: Team notifications and updates

### Development and Testing
- **Testing Workflows**: Test email functionality in development
- **Debug Notifications**: Send debug information and logs
- **Integration Testing**: Test email integration with other systems
- **Monitoring**: System monitoring and health check notifications

## Advanced Configuration

### Custom SMTP Server Setup
```bash
# For Outlook/Hotmail
SMTP_SERVER=smtp-mail.outlook.com
EMAIL=your_email@outlook.com
PASSWORD=your_password

# For Yahoo Mail
SMTP_SERVER=smtp.mail.yahoo.com
EMAIL=your_email@yahoo.com
PASSWORD=your_app_password

# For custom SMTP server
SMTP_SERVER=mail.yourdomain.com
EMAIL=your_email@yourdomain.com
PASSWORD=your_password
```

### Gmail App Password Setup
1. Enable 2-factor authentication on your Google account
2. Go to Google Account settings > Security > App passwords
3. Generate a new app password for "Mail"
4. Use this app password in the PASSWORD environment variable

### Enhanced Email Configuration
```python
# Example of extending the functionality
def send_enhanced_email(sender_email, app_password, receiver_email, subject, body, smtp_server="smtp.gmail.com", port=587):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
```

## Troubleshooting

### Common Issues
1. **Authentication Errors**: 
   - For Gmail, ensure you're using an App Password, not your regular password
   - Verify 2-factor authentication is enabled for Gmail
   - Check that the email and password are correct

2. **Connection Errors**:
   - Verify SMTP server settings and port numbers
   - Check internet connectivity
   - Ensure firewall isn't blocking SMTP ports

3. **Email Delivery Issues**:
   - Check spam/junk folders in recipient email
   - Verify recipient email address is correct
   - Some providers may block emails from certain IP addresses

### Debug Tips
- Test email credentials with a simple email client first
- Check SMTP server logs if available
- Verify TLS/SSL support on the SMTP server
- Monitor network connectivity during email sending

### SMTP Server Settings
Common SMTP configurations:
```bash
# Gmail
SMTP_SERVER=smtp.gmail.com (Port 587)

# Outlook/Hotmail
SMTP_SERVER=smtp-mail.outlook.com (Port 587)

# Yahoo
SMTP_SERVER=smtp.mail.yahoo.com (Port 587 or 465)

# Custom servers may use different ports (25, 465, 587)
```

## Performance Considerations

### Optimization
- **Connection Reuse**: For high-volume scenarios, consider connection pooling
- **Error Handling**: Implement retry logic for transient failures
- **Rate Limiting**: Be aware of email provider rate limits
- **Timeout Settings**: Configure appropriate timeouts for SMTP connections

### Security
- **App Passwords**: Always use app passwords for Gmail and other providers that support them
- **Environment Variables**: Never hardcode credentials in source code
- **TLS Encryption**: Always use TLS for secure email transmission
- **Credential Rotation**: Regularly rotate email passwords and app passwords

## Contributing

1. Add support for HTML email content
2. Implement email templates and formatting options
3. Add attachment support for files and documents
4. Improve error handling and logging capabilities

## License

MIT License - see LICENSE file for details.

## Links

- [MOFA Framework](https://github.com/moxin-org/mofa)
- [MOFA Documentation](https://github.com/moxin-org/mofa/blob/main/README.md)
- [Gmail App Passwords Guide](https://support.google.com/accounts/answer/185833)
- [Python SMTP Documentation](https://docs.python.org/3/library/smtplib.html)