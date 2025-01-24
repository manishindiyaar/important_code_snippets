import os
from dotenv import load_dotenv
import json
import math
from groq import Groq

class CalculatorAssistant:
    def __init__(self):
        """Initialize Azure OpenAI client with environment variables."""
        load_dotenv()
        self.client = Groq(
            
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def calculate(self, operation: str, x: float, y: float = None) -> float:
        """
        Perform mathematical operations.
        
        Args:
            operation (str): Type of mathematical operation
            x (float): First number
            y (float, optional): Second number for binary operations
        
        Returns:
            float: Calculation result
        """
        operations = {
            'add': lambda x, y: x + y,
            'subtract': lambda x, y: x - y,
            'multiply': lambda x, y: x * y,
            'divide': lambda x, y: x / y if y != 0 else "Error: Division by zero",
            'power': lambda x, y: x ** y,
            'sqrt': lambda x, _: math.sqrt(x),
            'log': lambda x, _: math.log(x),
            'sin': lambda x, _: math.sin(x),
            'cos': lambda x, _: math.cos(x)
        }
        
        if operation not in operations:
            raise ValueError(f"Unsupported operation: {operation}")
        
        return operations[operation](x, y) if y is not None else operations[operation](x, None)

    def calculator_function_call(self, user_message: str) -> str:
        """
        Process user message and perform calculator function call.
        
        Args:
            user_message (str): User's input message
        
        Returns:
            str: Calculation result or error message
        """
        # Define calculator function schema
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform mathematical calculations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "add", "subtract", "multiply", "divide", 
                                    "power", "sqrt", "log", "sin", "cos"
                                ],
                                "description": "Mathematical operation to perform"
                            },
                            "x": {
                                "type": "number",
                                "description": "First number for calculation"
                            },
                            "y": {
                                "type": "number",
                                "description": "Second number for binary operations"
                            }
                        },
                        "required": ["operation", "x"]
                    }
                }
            }
        ]

        # Generate response using OpenAI
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful calculator assistant. Translate user requests into mathematical operations."
                },
                {"role": "user", "content": user_message}
            ],
            tools=functions
        )

        # Process the response
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            if tool_call.function.name == "calculate":
                # Parse function arguments
                args = json.loads(tool_call.function.arguments)
                
                try:
                    result = self.calculate(
                        operation=args["operation"],
                        x=args["x"],
                        y=args.get("y")
                    )
                    return f"Result: {result}"
                except Exception as e:
                    return f"Calculation error: {str(e)}"
        
        return message.content

def main():
    """Example usage of CalculatorAssistant"""
    calculator = CalculatorAssistant()
    
    # Example queries
    queries = [
        "What is 5 plus 3?",
        "Calculate the square root of 16",
        "Multiply 7 by 6",
        "Divide 20 by 4"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        print(calculator.calculator_function_call(query))
        print()

if __name__ == "__main__":
    main()