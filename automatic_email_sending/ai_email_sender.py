import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import AzureOpenAI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import json
from groq import Groq
class EmailSender:
    def __init__(self):
        """
        Initialize the EmailSender with environment variables and OpenAI client.
        """
        load_dotenv()
        
        # Initialize Azure OpenAI client
        # self.openai_client = AzureOpenAI(
        #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        #     api_version="2024-08-01-preview",
        #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        # )
        

        self.client=Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def send_email(self, to_email: str, body_content: str, subject: str) -> Dict[str, str]:
        """
        Send an email using SendGrid.
        
        Args:
            to_email (str): Recipient's email address
            body_content (str): HTML body of the email
            subject (str): Email subject line
        
        Returns:
            Dict[str, str]: Status of email sending
        """
        sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        from_email = Email(
            email=os.getenv('MAIL_DEFAULT_SENDER'),
            name=os.getenv('MAIL_DEFAULT_SENDER_NAME', 'Appointment System')
        )

        # Wrap content in HTML template
        content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            {body_content}
            </div>
        </body>
        </html>
        """

        message = Mail(
            from_email=from_email,
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", content.strip())
        )

        try:
            sg.send(message)
            return {'status': 'success', 'message': f'Email sent successfully to {to_email}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def generate_email_content(self, conversation: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Generate email content using OpenAI's chat completion.
        
        Args:
            conversation (str): The conversation to summarize
            system_prompt (str, optional): Custom system prompt for content generation
        
        Returns:
            Dict[str, Any]: Generated email details
        """
        # Use default system prompt if not provided
        if system_prompt is None:
            system_prompt = """
            You are an advanced summarization bot and email sender. 
            Summarize the given conversation concisely, focusing on:
            - Key discussion points
            - Action items
            - Decisions made
            - Next steps
            
            Create a professional, clear, and concise report and then sending email.
            """

        # Define function for email generation
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email with summarized content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_email": {
                                "type": "string",
                                "description": "Recipient's email address"
                            },
                            "body_content": {
                                "type": "string",
                                "description": "HTML content of the email"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Subject line of the email"
                            }
                        },
                        "required": ["to_email", "body_content", "subject"]
                    }
                }
            }
        ]

        # Generate email content using OpenAI
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation}
            ],
            tools=functions
        )

        # Process the response
        message = response.choices[0].message
        
        if message.tool_calls:
            # Parse function arguments if a tool call is present
            return json.loads(message.tool_calls[0].function.arguments)
        
        # If no tool call, return the generated content
        return {
            "body_content": message.content,
            "subject": "Conversation Summary",
            "to_email": os.getenv('DEFAULT_RECIPIENT_EMAIL', '')
        }

    def process_and_send_email(self, conversation: str, system_prompt: str = None) -> Dict[str, str]:
        """
        Generate email content and send the email.
        
        Args:
            conversation (str): The conversation to summarize
            system_prompt (str, optional): Custom system prompt for content generation
        
        Returns:
            Dict[str, str]: Result of email sending process
        """
        # Generate email content
        email_details = self.generate_email_content(conversation, system_prompt)
        
        # Send email
        return self.send_email(
            to_email=email_details.get('to_email', ''),
            body_content=email_details.get('body_content', ''),
            subject=email_details.get('subject', 'Conversation Summary')
        )

# Example usage
def main():
    # Initialize the EmailSender
    email_sender = EmailSender()
    
    # Example conversation to summarize and send
    sample_conversation = """
    Patient: I've been experiencing headaches for the past week.
    Doctor: Can you describe the pain? When does it occur?
    Patient: Usually in the afternoon, sharp pain on the right side.
    Doctor: We should run some tests to understand the cause.
    Doctor: ok i am sending you an email of this conversation summary to manishindiyaar@gmail.com
    """
    
    # Process and send email
    result = email_sender.process_and_send_email(sample_conversation)
    print(result)

if __name__ == "__main__":
    main()