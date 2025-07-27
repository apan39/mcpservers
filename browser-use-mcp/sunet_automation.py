#!/usr/bin/env python3
"""
Test script to automate navigation to sunet.se and click e-möte button
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add current directory to path to import server modules
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent
from patchright.async_api import async_playwright

async def automate_sunet_navigation():
    """Automate navigation to sunet.se and click e-möte button"""
    
    print("🚀 Starting sunet.se automation...")
    
    async with async_playwright() as p:
        # Launch browser in headless mode to avoid display issues
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("📍 Navigating to sunet.se...")
            await page.goto("https://sunet.se")
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            
            print("🔍 Looking for e-möte button...")
            
            # Try multiple selectors for the e-möte button
            selectors_to_try = [
                'text=E-möte',
                'text=e-möte', 
                'a[href*="zoom"]',
                'a[href*="meet"]',
                'text=Zoom',
                '[href*="zoom"]'
            ]
            
            clicked = False
            for selector in selectors_to_try:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        print(f"✅ Found element with selector: {selector}")
                        await element.click()
                        clicked = True
                        print("🎯 Clicked the e-möte/Zoom button!")
                        break
                except:
                    print(f"❌ Selector not found: {selector}")
                    continue
            
            if not clicked:
                print("⚠️  Could not find e-möte button, trying to get page content...")
                content = await page.content()
                # Look for links containing zoom or möte
                if 'zoom' in content.lower() or 'möte' in content.lower():
                    print("📝 Found zoom/möte content on page")
                    # Try to find any clickable elements
                    zoom_elements = await page.query_selector_all('a, button, [role="button"]')
                    for element in zoom_elements:
                        text = await element.text_content()
                        if text and ('zoom' in text.lower() or 'möte' in text.lower()):
                            print(f"🎯 Found and clicking: {text}")
                            await element.click()
                            clicked = True
                            break
            
            if clicked:
                # Wait a bit to see the result
                await page.wait_for_timeout(3000)
                print("📸 Taking screenshot of result...")
                await page.screenshot(path='sunet_result.png')
                
                # Get current URL
                current_url = page.url
                print(f"🌐 Current URL: {current_url}")
            else:
                print("❌ Could not find or click e-möte button")
                await page.screenshot(path='sunet_page.png')
                print("📸 Saved screenshot of the page as sunet_page.png")
            
        except Exception as e:
            print(f"❌ Error during automation: {e}")
            await page.screenshot(path='sunet_error.png')
            
        finally:
            await browser.close()
            print("✅ Browser closed")

if __name__ == "__main__":
    asyncio.run(automate_sunet_navigation())