"""
CLI helper — called by Claude Code (the consultant) to run a Gemini worker step.

Usage:
  python gemini_call.py --system "..." --instructions "..." [--context "..."]
"""
import argparse
import os
import sys
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True)
    parser.add_argument("--instructions", required=True)
    parser.add_argument("--context", default="")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    content = args.instructions
    if args.context:
        content = f"Context from previous steps:\n{args.context}\n\n---\n\n{args.instructions}"

    resp = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=content,
        config=types.GenerateContentConfig(
            system_instruction=args.system,
        ),
    )
    print(resp.text)

if __name__ == "__main__":
    main()
