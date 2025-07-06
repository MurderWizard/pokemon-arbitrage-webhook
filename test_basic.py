#!/usr/bin/env python3
print("Python is working!")
import os
print("OS module works")
from dotenv import load_dotenv
print("dotenv works")
load_dotenv()
print("Environment loaded")
token = os.getenv('TG_TOKEN')
print(f"Token exists: {bool(token)}")
print("Test completed successfully!")
