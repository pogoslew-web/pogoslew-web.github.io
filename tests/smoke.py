import asyncio, json, sys
from playwright.async_api import async_playwright
B="http://localhost:4321"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        out={}
        errs=[]
        ctx=await b.new_context(viewport={"width":1366,"height":850})
        pg=await ctx.new_page()
        pg.on("console",lambda m: errs.append((m.type,m.text[:160])) if m.type=="error" else None)
        pg.on("pageerror",lambda e: errs.append(("pageerror",str(e)[:160])))
        pg.on("requestfailed",lambda r: errs.append(("reqfail",r.url[-80:])))
        await pg.goto(B+"/"); await pg.wait_for_load_state("networkidle")
        out["home_title"]=await pg.title()
        await pg.screenshot(path="/home/claude/overrank/tests/shots/home_desktop.png")
        # palette
        await pg.keyboard.press("Control+k"); await pg.wait_for_selector("#palette[data-open=true]")
        await pg.fill("#palette-q","reaper"); await pg.wait_for_selector(".palette-item")
        out["palette_results"]=await pg.locator(".palette-item").count()
        out["palette_first"]=(await pg.locator(".palette-item .t").first.inner_text())
        await pg.screenshot(path="/home/claude/overrank/tests/shots/palette.png")
        await pg.keyboard.press("Enter"); await pg.wait_for_url("**/classes/reaper/**"); await pg.wait_for_load_state("networkidle")
        out["after_enter_url"]=pg.url
        # no results
        await pg.goto(B+"/"); await pg.keyboard.press("/"); await pg.fill("#palette-q","zzzxqv"); await pg.wait_for_selector(".palette-empty")
        out["noresult_ok"]=True
        await pg.keyboard.press("Escape")
        # items list
        await pg.goto(B+"/items/"); await pg.wait_for_load_state("networkidle")
        out["items_count_text"]=await pg.locator("#f-count").inner_text()
        vis=lambda: pg.locator("#f-grid .cell:not([hidden])").count()
        out["items_visible_initial"]=await vis()
        await pg.select_option("[data-facet=Kind]",index=2); out["items_after_facet"]=(await pg.locator("#f-count").inner_text(), await vis())
        await pg.select_option("#f-sort","az"); first=await pg.locator("#f-grid .cell:not([hidden]) .entry-title").first.inner_text(); out["sort_az_first"]=first
        await pg.click("#f-reset"); await pg.fill("#f-q","zzzzqq"); out["empty_state"]=await pg.locator("#f-empty").is_visible()
        await pg.click("#f-clear"); await pg.click("#v-list"); out["list_view"]=await pg.locator("#f-grid.list-view").count()
        await pg.goto(B+"/items/?q=weapon"); await pg.wait_for_load_state("networkidle"); out["weapons_shortcut"]=await pg.locator("#f-count").inner_text()
        await pg.screenshot(path="/home/claude/overrank/tests/shots/items_desktop.png")
        # detail
        await pg.goto(B+"/classes/assassin/"); await pg.wait_for_load_state("networkidle")
        out["assassin_sections"]=await pg.locator("details[data-sec]").count()
        await pg.click(".toc a[href='#skills']") ; out["hash"]=pg.url.split("#")[-1]
        await pg.screenshot(path="/home/claude/overrank/tests/shots/detail_desktop.png")
        # table sort
        await pg.locator("#skills table th").first.click(); out["sorted_attr"]=await pg.locator("#skills table th[aria-sort]").count()
        # odds filter
        await pg.goto(B+"/odds/"); await pg.wait_for_load_state("networkidle"); await pg.fill("#intro-q","chest")
        out["odds_filter"]=await pg.locator("#intro-count").inner_text()
        # codes
        await pg.goto(B+"/codes/"); await pg.wait_for_load_state("networkidle")
        out["code_status"]=await pg.locator("[data-status]").all_inner_texts()
        # search page
        await pg.goto(B+"/search/?q=guardian"); await pg.wait_for_selector("#sres a"); out["search_page_results"]=await pg.locator("#sres a").count()
        # random
        await pg.goto(B+"/random/"); await pg.wait_for_url(lambda u: "/random/" not in u,timeout=8000); out["random_to"]=pg.url
        out["desktop_errors"]=errs[:12]
        await ctx.close()
        # mobile
        mctx=await b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
        m=await mctx.new_page(); merrs=[]
        m.on("pageerror",lambda e: merrs.append(str(e)[:160]))
        over={}
        for path in ["/","/items/","/classes/assassin/","/odds/","/codes/","/integrity/","/database/","/search/?q=rift","/monsters/","/ranks/overview/","/news/","/skills/","/formulas/combat/" ]:
            r=await m.goto(B+path); await m.wait_for_load_state("networkidle")
            sw=await m.evaluate("document.documentElement.scrollWidth"); cw=await m.evaluate("document.documentElement.clientWidth")
            over[path]=(r.status,sw,cw,sw>cw)
        out["mobile_overflow"]={k:v for k,v in over.items()}
        await m.goto(B+"/"); await m.screenshot(path="/home/claude/overrank/tests/shots/home_mobile.png")
        await m.click("#menu-open"); await m.wait_for_selector("#drawer[data-open=true]"); await m.screenshot(path="/home/claude/overrank/tests/shots/drawer_mobile.png")
        await m.click("#menu-close")
        await m.goto(B+"/classes/assassin/"); await m.screenshot(path="/home/claude/overrank/tests/shots/detail_mobile.png",full_page=False)
        await m.goto(B+"/items/"); await m.screenshot(path="/home/claude/overrank/tests/shots/items_mobile.png")
        out["mobile_errors"]=merrs
        await b.close()
        print(json.dumps(out,indent=1,default=str))
asyncio.run(main())
