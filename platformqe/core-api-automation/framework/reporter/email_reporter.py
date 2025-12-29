#!/usr/bin/env python3
"""
Send email notifications with test report attachments.
Usage: python send_email_report.py --build-number <num> --job-status <status> --reports-path <path>
"""

import smtplib
import os
import sys
import argparse
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_email_report(build_number, job_status, reports_path, build_id, team_project, collection_uri,
                     smtp_server, smtp_port, from_addr, to_addrs, cc_addrs, bcc_addrs, subject_prefix, service_name=''):
    """Send email with test report attachments.
    
    Args:
        service_name: Service being tested (e.g., 'parties', 'work_item_notification')
                     Used to route emails to service-specific teams
    """
    
    # Parse email addresses (comma-separated strings to lists)
    to_list = [addr.strip() for addr in to_addrs.split(',') if addr.strip()]
    cc_list = [addr.strip() for addr in cc_addrs.split(',') if addr.strip()] if cc_addrs else []
    bcc_list = [addr.strip() for addr in bcc_addrs.split(',') if bcc_addrs else []
    
    # Add service-specific recipients if service_name is provided
    if service_name:
        service_key = service_name.upper().replace('-', '_').replace(' ', '_')
        
        # Check for service-specific email lists from environment variables
        service_to = os.getenv(f'EMAIL_TO_{service_key}', '')
        service_cc = os.getenv(f'EMAIL_CC_{service_key}', '')
        service_bcc = os.getenv(f'EMAIL_BCC_{service_key}', '')
        
        # Merge service-specific lists with default lists (avoid duplicates)
        if service_to:
            to_list.extend([addr.strip() for addr in service_to.split(',') if addr.strip() and addr.strip() not in to_list])
        if service_cc:
            cc_list.extend([addr.strip() for addr in service_cc.split(',') if addr.strip() and addr.strip() not in cc_list])
        if service_bcc:
            bcc_list.extend([addr.strip() for addr in service_bcc.split(',') if addr.strip() and addr.strip() not in bcc_list])
        
        print(f"📧 Service-specific routing for '{service_name}': TO={len(to_list)}, CC={len(cc_list)}, BCC={len(bcc_list)}")
    
    subject = f'{subject_prefix}{job_status} - API Test Report - Build {build_number}'
    if service_name:
        subject += f' - {service_name.upper()}'
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_list)
    if cc_list:
        msg['Cc'] = ', '.join(cc_list)
    msg['Subject'] = subject
    
    # Build URL
    build_url = f"{collection_uri}{team_project}/_build/results?buildId={build_id}"
    
    # Email body
    body = f"""
    <html>
    <body>
    <h2>API Test Report</h2>
    <p><strong>Build Number:</strong> {build_number}</p>
    <p><strong>Job Status:</strong> {job_status}</p>
    <p><strong>Build URL:</strong> <a href="{build_url}">View Build</a></p>
    <p>Test reports are attached to this email and published as build artifacts.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    
    # Attach files
    print(f"Looking for attachments in: {reports_path}")
    
    # Find and attach reports
    for file_pattern in ['junit_report*.xml', 'test_summary.json', 'performance_report.html']:
        files = glob.glob(os.path.join(reports_path, file_pattern))
        for filepath in files:
            if os.path.exists(filepath):
                print(f"Attaching: {filepath}")
                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filepath)}')
                    msg.attach(part)
    
    # Send email
    try:int(smtp_port)) as server:
            # Combine all recipients (to, cc, bcc)
            recipients = to_list + cc_list + bcc_listport) as server:
            recipients = to_addrs + cc_addrs
            server.sendmail(from_addr, recipients, msg.as_string())
            print(f"✅ Email sent successfully to {', '.join(recipients)}")
            return 0
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send email report with test attachments')
    parser.add_argument('--build-number', required=True, help='Build number')
    parser.add_argument('--job-status', required=True, help='Job status (Succeeded/Failed)')
    parser.add_argument('--reports-path', required=True, help='Path to reports directory')
    parser.add_argument('--build-id', required=True, help='Build ID')
    parser.add_argument('--team-project', required=True, help='Team project name')
    parser.add_argument('--collection-uri', required=True, help='Collection URI')
    # Service name for routing to specific teams
    parser.add_argument('--service-name', default='', help='Service being tested (e.g., parties, work_item_notification)')
    
    # Email configuration from environment variables (populated from variable group)
    parser.add_argument('--smtp-server', default=os.getenv('SMTP_SERVER', 'smtp-nonprod.corp.local'))
    parser.add_argument('--smtp-port', default=os.getenv('SMTP_PORT', '25'))
    parser.add_argument('--from-addr', default=os.getenv('EMAIL_FROM', 'noreply@assetmark.com'))
    parser.add_argument('--to-addrs', default=os.getenv('EMAIL_TO', ''))
    parser.add_argument('--cc-addrs', default=os.getenv('EMAIL_CC', ''))
    parser.add_argument('--bcc-addrs', default=os.getenv('EMAIL_BCC', ''))
    parser.add_argument('--subject-prefix', default=os.getenv('EMAIL_SUBJECT_PREFIX', ''))
    
    args = parser.parse_args()
    
    exit_code = send_email_report(
        args.build_number,
        args.job_status,
        args.reports_path,
        args.build_id,
        args.team_project,
        args.collection_uri,
        args.smtp_server,
        args.smtp_port,
        args.from_addr,
        args.to_addrs,
        args.cc_addrs,
        args.bcc_addrs,
        args.subject_prefix
        args.collection_uri
    )
    
    sys.exit(exit_code)
