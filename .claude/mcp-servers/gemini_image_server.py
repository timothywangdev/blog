#!/usr/bin/env python3
"""
MCP Server for Gemini Image Generation

Requires:
    pip install google-genai mcp Pillow

Set environment variable:
    export GEMINI_API_KEY="your-api-key"
"""

import os
import io
import base64
from pathlib import Path
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# Check for google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

server = Server("gemini-image-generator")


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="gemini_generate_image",
            description="Generate an image using Gemini API",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Description of the image to generate"
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "enum": ["1:1", "16:9", "9:16", "4:3", "3:4"],
                        "default": "1:1",
                        "description": "Aspect ratio of the generated image"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save the image (relative to project root)"
                    }
                },
                "required": ["prompt"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name != "gemini_generate_image":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    if not GENAI_AVAILABLE:
        return [TextContent(
            type="text",
            text="Error: google-genai not installed. Run: pip install google-genai"
        )]

    if not PIL_AVAILABLE:
        return [TextContent(
            type="text",
            text="Error: Pillow not installed. Run: pip install Pillow"
        )]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return [TextContent(
            type="text",
            text="Error: GEMINI_API_KEY environment variable not set"
        )]

    prompt = arguments.get("prompt")
    aspect_ratio = arguments.get("aspect_ratio", "1:1")
    output_path = arguments.get("output_path")

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )

        # Extract image from response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                image_data = part.inline_data.data

                # Save if output path provided
                if output_path:
                    # Ensure directory exists
                    save_path = Path(output_path)
                    save_path.parent.mkdir(parents=True, exist_ok=True)

                    # Decode and save
                    image = Image.open(io.BytesIO(image_data))
                    image.save(save_path)

                    return [TextContent(
                        type="text",
                        text=f"Image generated and saved to: {output_path}"
                    )]
                else:
                    # Generate default filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    default_path = f"images/generated/gemini_{timestamp}.png"
                    Path(default_path).parent.mkdir(parents=True, exist_ok=True)

                    image = Image.open(io.BytesIO(image_data))
                    image.save(default_path)

                    return [TextContent(
                        type="text",
                        text=f"Image generated and saved to: {default_path}"
                    )]

        return [TextContent(
            type="text",
            text="No image was generated. The model may have returned text only."
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error generating image: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
