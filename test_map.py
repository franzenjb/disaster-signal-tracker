#!/usr/bin/env python3
"""
Playwright test to verify the US disaster map is working
"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_disaster_map():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to False to see the browser
        page = await browser.new_page()
        
        # Set viewport for consistent screenshots
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        print("🚀 Testing US Disaster Map...")
        
        # Navigate to the disaster map
        url = "https://franzenjb.github.io/disaster-signal-tracker/usmap.html"
        print(f"📍 Loading: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for the map to load
            print("⏳ Waiting for map to initialize...")
            await page.wait_for_selector('#map', timeout=10000)
            
            # Take screenshot of initial load
            await page.screenshot(path="map_initial.png", full_page=True)
            print("📸 Screenshot saved: map_initial.png")
            
            # Wait a moment for any dynamic content
            await page.wait_for_timeout(3000)
            
            # Click the scan button to load disasters
            print("🔍 Clicking 'Scan All US Disasters' button...")
            scan_button = page.locator('button:has-text("Scan All US Disasters")')
            await scan_button.click()
            
            # Wait for data to load
            print("⏳ Waiting for disaster data to load...")
            await page.wait_for_timeout(5000)
            
            # Take screenshot after data loads
            await page.screenshot(path="map_with_data.png", full_page=True)
            print("📸 Screenshot saved: map_with_data.png")
            
            # Check for disaster counts
            weather_count = await page.locator('#weatherCount').text_content()
            earthquake_count = await page.locator('#earthquakeCount').text_content()
            fire_count = await page.locator('#fireCount').text_content()
            
            print(f"📊 DISASTER COUNTS:")
            print(f"   🌪️ Weather Events: {weather_count}")
            print(f"   🌍 Earthquakes: {earthquake_count}")
            print(f"   🔥 Wildfires: {fire_count}")
            
            # Test layer toggles
            print("🎛️ Testing layer controls...")
            
            # Test weather layer
            await page.click('button:has-text("Weather Events")')
            await page.wait_for_timeout(1000)
            await page.screenshot(path="map_weather_only.png", full_page=True)
            print("📸 Weather layer screenshot: map_weather_only.png")
            
            # Test earthquake layer
            await page.click('button:has-text("Earthquakes")')
            await page.wait_for_timeout(1000)
            await page.screenshot(path="map_earthquakes_only.png", full_page=True)
            print("📸 Earthquake layer screenshot: map_earthquakes_only.png")
            
            # Test wildfire layer
            await page.click('button:has-text("Wildfires")')
            await page.wait_for_timeout(1000)
            await page.screenshot(path="map_wildfires_only.png", full_page=True)
            print("📸 Wildfire layer screenshot: map_wildfires_only.png")
            
            # Check if any markers are clickable
            print("🖱️ Testing marker interactions...")
            markers = await page.locator('svg circle').count()
            print(f"   Found {markers} markers on map")
            
            if markers > 0:
                # Click on first marker to test popup
                await page.locator('svg circle').first.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path="map_popup.png", full_page=True)
                print("📸 Popup screenshot: map_popup.png")
            
            # Test different map views by zooming to different states
            print("🗺️ Testing map navigation...")
            
            # Focus on California (high wildfire activity)
            await page.evaluate("map.setView([36.7783, -119.4179], 6)")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="map_california.png", full_page=True)
            print("📸 California view: map_california.png")
            
            # Focus on Alaska (earthquake activity)
            await page.evaluate("map.setView([64.0685, -152.2782], 5)")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="map_alaska.png", full_page=True)
            print("📸 Alaska view: map_alaska.png")
            
            # Focus on Eastern US (weather activity)
            await page.evaluate("map.setView([39.0458, -76.6413], 6)")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="map_eastern_us.png", full_page=True)
            print("📸 Eastern US view: map_eastern_us.png")
            
            # Return to full US view
            await page.evaluate("map.setView([39.8, -98.6], 4)")
            await page.wait_for_timeout(2000)
            
            # Final screenshot
            await page.screenshot(path="map_final.png", full_page=True)
            print("📸 Final screenshot: map_final.png")
            
            print("✅ MAP TEST COMPLETED SUCCESSFULLY!")
            print(f"✅ Weather alerts: {weather_count}")
            print(f"✅ Earthquake reports: {earthquake_count}")
            print(f"✅ Wildfire detections: {fire_count}")
            print(f"✅ Interactive markers: {markers}")
            print("✅ All screenshots saved")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            await page.screenshot(path="map_error.png", full_page=True)
            print("📸 Error screenshot saved: map_error.png")
        
        # Keep browser open for 10 seconds to see the final result
        print("⏸️ Keeping browser open for 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_disaster_map())