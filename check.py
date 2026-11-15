import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
async def test():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
  page=await browser.new_page(viewport={'width':1360,'height':930}); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content(Path('/mnt/data/v23_fix/index.html').read_text(),wait_until='domcontentloaded',timeout=90000)
  await page.wait_for_timeout(1300)
  print('loaded',await page.evaluate('({tab:TAB,rows:D?.t?.length,series:S.length})'))
  await page.locator('#nv button[data-t="a"]').click()
  print('artist',await page.evaluate('({count:S.length,active:G.all.length,unique:new Set(G.all.map(s=>s.col)).size,colors:G.all.map(s=>s.col).slice(0,10)})'))
  await page.locator('#fl details[data-k="country"] summary').click()
  print('country hint', await page.locator('#fl details[data-k="country"] .dim-help').get_attribute('data-help'))
  print('group hint',await page.locator('#xc .dim-help').count())
  await page.locator('#nv button[data-t="s"]').click()
  print('songs',await page.evaluate('({series:S.length,unique:new Set(G.all.map(s=>s.col)).size,active:G.all.length})'))
  await page.locator('#lang-en').click();await page.wait_for_timeout(250)
  await page.locator('#fl details[data-k="country"] summary').click()
  print('en hint',await page.locator('#fl details[data-k="country"] .dim-help').get_attribute('data-help'))
  print('errors',errors[:4]);assert not errors
  assert await page.evaluate('new Set(G.all.map(s=>s.col)).size===G.all.length')
  await browser.close()
asyncio.run(test())
