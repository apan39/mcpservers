#!/usr/bin/env python3
"""Test tool registration."""

from tools.math_tools import register_math_tools
from tools.text_tools import register_text_tools
from tools.crawl4ai_tools import register_crawl4ai_tools
from tools.coolify_tools import register_coolify_tools

tool_registry = {}

try:
    print("Registering math tools...")
    register_math_tools(tool_registry)
    print(f"Math tools registered: {len(tool_registry)}")
    
    print("Registering text tools...")
    register_text_tools(tool_registry)
    print(f"Total tools after text: {len(tool_registry)}")
    
    print("Registering crawl4ai tools...")
    register_crawl4ai_tools(tool_registry)
    print(f"Total tools after crawl4ai: {len(tool_registry)}")
    
    print("Registering coolify tools...")
    register_coolify_tools(tool_registry)
    print(f"Total tools after coolify: {len(tool_registry)}")
    
    print("\nTool registry contents:")
    for name, data in tool_registry.items():
        print(f"- {name}: {type(data.get('definition', 'NO DEF'))}")
        if 'definition' in data:
            print(f"  Definition: {data['definition']}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()