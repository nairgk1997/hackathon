#phone_app.py

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp_client():
    print("Starting MCP Client...")
    
    # 1. Tell the client to start the server in the background
    server_params = StdioServerParameters(
        command="python",
        args=["email_server.py"] 
    )

    # 2. Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            print("Initializing connection to Email Server...")
            await session.initialize()

            print("Triggering the 'send_email' tool...")
            
            # 3. Instruct the server to send the email
            try:
                result = await session.call_tool(
                    "send_email",
                    arguments={
                        "to_email": "nairgk1997@gmail.com",
                        "subject": "Success! MCP is Working",
                        "body": "This email was triggered successfully from scratch using your custom Python MCP setup."
                    }
                )
                
                # 4. Print the success or failure message from the server
                for content_block in result.content:
                    print(f"Server Response: {content_block.text}")
                    
            except Exception as e:
                print(f"An error occurred while calling the tool: {e}")

if __name__ == "__main__":
    asyncio.run(run_mcp_client())

#########################################


#email_reader.py

import imaplib
import email
from email.header import decode_header

# # --- 1. Your Credentials ---
# EMAIL_ACCOUNT = "your_email@gmail.com"      # <-- Put your Gmail here
# APP_PASSWORD = "your_app_password_here"     # <-- Put your 16-digit App Password here

EMAIL_ACCOUNT = "nairgk1997@gmail.com"      # <-- Put your Gmail here
APP_PASSWORD = "jdbp kqys tvhy qrwl" # <-- Put your 16-digit App Password here


def check_for_replies():
    print("Connecting to Gmail to check for replies...")
    
    try:
        # --- 2. Connect to Gmail's IMAP Server ---
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
        mail.select("inbox")

        # --- 3. Search Filter ---
        # UNSEEN: Only grabs unread emails
        # SUBJECT: Only grabs emails replying to your specific subject line
        # NOTE: If you change the subject in your sender script, change it here too!
        search_criteria = '(UNSEEN SUBJECT "Re: Success! MCP is Working")'
        status, messages = mail.search(None, search_criteria)

        if not messages[0]:
            print("No new replies found yet.")
            mail.logout()
            return

        # Convert message string to a list of IDs
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} new reply(ies)!")

        # --- 4. Read the Emails ---
        for e_id in email_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the raw email bytes
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Get the sender's email address
                    from_header = msg.get("From")
                    print(f"\n{'-'*40}")
                    print(f"📥 NEW REPLY FROM: {from_header}")
                    
                    # Extract the actual text body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")
                    
                    print(f"📝 MESSAGE:\n{body.strip()}")
                    
                    # --- 5. The "Brain" (Logic Check) ---
                    # For a hackathon, checking keywords is the fastest way. 
                    # If you want to use an LLM, you would pass the 'body' variable to OpenAI here.
                    body_lower = body.lower()
                    if "yes" in body_lower or "agree" in body_lower:
                        print("\n✅ DECISION: The user AGREED!")
                        print("🚀 TRIGGERING NEXT FLOW... (Add your next code here)")
                        # trigger_next_step_function()
                    else:
                        print("\n❌ DECISION: The user did not explicitly agree.")

        mail.logout()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("SCRIPT STARTED!")
    check_for_replies()


#################################################


#email_server.py

import smtplib
from email.message import EmailMessage
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("EmailServer")

# --- YOUR CREDENTIALS ---
SENDER_EMAIL = "nairgk1997@gmail.com"      # <-- Put your Gmail here
SENDER_PASSWORD = "jdbp kqys tvhy qrwl" # <-- Put your 16-digit App Password here

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

@mcp.tool()
def send_email(to_email: str, subject: str, body: str) -> str:
    """Triggers an email to the specified address."""
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        return f"Successfully sent email to {to_email}."
    except Exception as e:
        return f"Failed to send email: {str(e)}"

if __name__ == "__main__":
    # Start the server listening for MCP requests
    mcp.run()






