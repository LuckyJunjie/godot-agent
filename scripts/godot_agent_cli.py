#!/usr/bin/env python3
"""
Godot Agent CLI - Command-line interface for asset generation and project management.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Godot Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate image
    gen_parser = subparsers.add_parser("generate-image", help="Generate an image asset")
    gen_parser.add_argument("--prompt", required=True, help="Image generation prompt")
    gen_parser.add_argument("--name", required=True, help="Asset name")
    gen_parser.add_argument("--model", default="dall-e-3", help="Model to use")
    gen_parser.add_argument("--size", default="256x256", help="Image size")
    gen_parser.add_argument("--negative", help="Negative prompt")
    gen_parser.add_argument("--project", default=".", help="Project root")
    
    # Generate audio
    audio_parser = subparsers.add_parser("generate-audio", help="Generate an audio asset")
    audio_parser.add_argument("--prompt", required=True, help="Audio generation prompt")
    audio_parser.add_argument("--name", required=True, help="Asset name")
    audio_parser.add_argument("--model", default="elevenlabs", help="Model to use")
    audio_parser.add_argument("--duration", type=int, default=5, help="Duration in seconds")
    audio_parser.add_argument("--project", default=".", help="Project root")
    
    # List assets
    list_parser = subparsers.add_parser("list-assets", help="List generated assets")
    list_parser.add_argument("--type", choices=["sprite", "audio", "model"], help="Asset type")
    list_parser.add_argument("--project", default=".", help="Project root")
    
    # Run tests
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--project", default=".", help="Project root")
    
    # MCP servers
    mcp_parser = subparsers.add_parser("mcp", help="MCP server management")
    mcp_parser.add_argument("action", choices=["start", "stop", "list"], help="Action")
    mcp_parser.add_argument("--server", help="Server name")
    mcp_parser.add_argument("--project", default=".", help="Project root")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle commands
    if args.command == "generate-image":
        from godot_agent.assets import AssetPipeline, ImageMeta
        
        size_parts = args.size.split("x")
        resolution = (int(size_parts[0]), int(size_parts[1]))
        
        pipeline = AssetPipeline(args.project)
        pipeline.initialize()
        
        meta = ImageMeta(
            prompt=args.prompt,
            negative_prompt=args.negative or "",
            model=args.model,
            resolution=resolution
        )
        
        async def run():
            path = await pipeline.generate_image(meta, args.name)
            print(f"Generated: {path}")
        
        asyncio.run(run())
        return 0
    
    elif args.command == "generate-audio":
        from godot_agent.assets import AssetPipeline, AudioMeta
        
        pipeline = AssetPipeline(args.project)
        pipeline.initialize()
        
        meta = AudioMeta(
            prompt=args.prompt,
            model=args.model,
            duration=args.duration
        )
        
        async def run():
            path = await pipeline.generate_audio(meta, args.name)
            print(f"Generated: {path}")
        
        asyncio.run(run())
        return 0
    
    elif args.command == "list-assets":
        from godot_agent.assets import AssetPipeline
        
        pipeline = AssetPipeline(args.project)
        pipeline.initialize()
        
        assets = pipeline.list_assets(args.type)
        
        for asset in assets:
            print(asset.name)
        
        return 0
    
    elif args.command == "test":
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/", "-v"],
            cwd=args.project,
            capture_output=True
        )
        print(result.stdout.decode())
        return result.returncode
    
    elif args.command == "mcp":
        from godot_agent.mcp import create_godot_mcp_client
        
        client = create_godot_mcp_client(args.project)
        
        async def run_mcp():
            if args.action == "start":
                results = await client.start_all()
                for name, success in results.items():
                    status = "SUCCESS" if success else "FAILED"
                    print(f"{name}: {status}")
            elif args.action == "stop":
                await client.stop_all()
                print("All servers stopped")
            elif args.action == "list":
                for name, config in client.servers.items():
                    print(f"{name}: {config.command} {' '.join(config.args)}")
        
        asyncio.run(run_mcp())
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
