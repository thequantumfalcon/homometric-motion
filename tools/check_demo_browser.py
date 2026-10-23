"""Audit the offline explorer with optional Playwright and save visual evidence.

This checks presentation and browser interactions, not the mathematical theorem.
Playwright and browser binaries are separate developer tools, never certificate
dependencies. Screenshots still require separate visual inspection.
"""

import argparse
import hashlib
import json
import math
from importlib.metadata import version
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

ROOT = Path(__file__).resolve().parents[1]
VIEWPORTS = {
    "desktop": (1440, 1000),
    "tablet": (768, 1024),
    "mobile": (390, 844),
    "narrow": (320, 740),
}


def check(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def check_links(page, checks: list[str]) -> None:
    """Check local resources and in-page anchors without following external links."""
    page_url = urlparse(page.url)
    for href in page.locator("a[href]").evaluate_all("nodes => nodes.map(n => n.href)"):
        parsed = urlparse(href)
        if parsed.scheme != "file":
            continue
        target = Path(url2pathname(unquote(parsed.path)))
        check(target.is_file(), f"local link exists: {target.name}", checks)
        if parsed.path == page_url.path and parsed.fragment:
            exists = page.evaluate(
                "id => document.getElementById(id) !== null", unquote(parsed.fragment)
            )
            check(exists, f"page anchor exists: {parsed.fragment}", checks)


def screenshot(page, directory: Path, name: str, screenshots: list[dict]) -> None:
    target = directory / f"{name}.png"
    page.screenshot(path=str(target), full_page=True, animations="disabled")
    screenshots.append(
        {"file": target.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    )


def section_screenshot(page, directory: Path, name: str, selector: str, screenshots: list) -> None:
    target = directory / f"{name}.png"
    page.locator(selector).screenshot(path=str(target), animations="disabled")
    screenshots.append(
        {"file": target.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    )


def inspect_state(page) -> dict:
    return page.evaluate("HomometricDemo.inspectState()")


def check_accessibility(page, axe_script: Path) -> dict:
    page.add_script_tag(path=str(axe_script))
    result = page.evaluate(
        "async () => { const r = await axe.run(document, {runOnly: {type: 'tag', "
        "values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice']}}); "
        "const compact = entries => entries.map(x => ({id:x.id, impact:x.impact, "
        "description:x.description, help:x.help, helpUrl:x.helpUrl, "
        "nodes:x.nodes.map(n => ({target:n.target, failureSummary:n.failureSummary}))})); "
        "return {version:r.testEngine.version, passes:r.passes.length, "
        "violations:compact(r.violations), incomplete:compact(r.incomplete)};}"
    )
    result["script_sha256"] = hashlib.sha256(axe_script.read_bytes()).hexdigest()
    return result


def check_motion(page, checks: list[str]) -> None:
    check(page.locator("#sample-motion").count() == 1, "motion control is present", checks)
    initial = inspect_state(page)
    page.locator("#sample-motion").click()
    first = inspect_state(page)
    check(first != initial, "explicit sample action changes motion state", checks)
    for side in ("A", "B"):
        values = first["displacements"][side]
        check(
            len(values) == 63 and all(math.isfinite(value) for value in values),
            f"sample has 63 finite {side} displacements",
            checks,
        )
        check(
            max(abs(value) for value in values) > 0
            and abs(sum(values)) < 1e-12 * max(abs(value) for value in values),
            f"{side} sample removes center-of-mass translation",
            checks,
        )
    page.locator("#reset-motion").click()
    reset = inspect_state(page)
    check(reset == initial, "reset restores mean geometry and initial seed", checks)
    page.locator("#sample-motion").click()
    check(inspect_state(page) == first, "sample replay is deterministic", checks)
    page.locator("#magnification").focus()
    page.keyboard.press("Home")
    zero_scale = inspect_state(page)
    page.keyboard.press("End")
    restored = inspect_state(page)
    check(restored == first, "magnification round trip preserves sampled state", checks)

    def without_scale(state):
        return {key: value for key, value in state.items() if key != "magnification"}

    check(
        without_scale(first) == without_scale(zero_scale),
        "display magnification does not alter the sampled displacement",
        checks,
    )
    old_viewport = page.viewport_size
    page.set_viewport_size({"width": 768, "height": 900})
    page.wait_for_timeout(120)
    check(inspect_state(page) == first, "resize preserves sampled state", checks)
    page.set_viewport_size(old_viewport)
    page.wait_for_timeout(120)
    page.locator("#reset-motion").click()


def stress_motion(page, checks: list[str]) -> dict:
    result = page.evaluate(
        """() => {
          let minimumMargin = Infinity;
          for (const view of ['full', 'detail']) {
            document.querySelector(`input[name="geometry-view"][value="${view}"]`).click();
            document.querySelector('#reset-motion').click();
            for (let sample = 0; sample < 128; sample++) {
              document.querySelector('#sample-motion').click();
              const svg = document.querySelector('#geometry');
              const box = svg.viewBox.baseVal;
              for (const point of svg.querySelectorAll('circle')) {
                const x = point.cx.baseVal.value, y = point.cy.baseVal.value;
                const radius = point.r.baseVal.value;
                const margin = Math.min(x-radius, y-radius, box.width-x-radius,
                                        box.height-y-radius);
                if (!Number.isFinite(margin)) return {ok:false, reason:'nonfinite point'};
                minimumMargin = Math.min(minimumMargin, margin);
              }
            }
          }
          document.querySelector('#reset-motion').click();
          document.querySelector('input[name="geometry-view"][value="full"]').click();
          return {ok:minimumMargin >= 0, draws_per_view:128,
                  views:['full','detail'], minimum_svg_margin:minimumMargin};
        }"""
    )
    check(result["ok"], "128 snapshots in each geometry view stay inside the SVG", checks)
    return result


def check_interactions(page, checks: list[str]) -> dict:
    """Exercise user input independently of the page's internal display checks."""
    result = page.evaluate("HomometricDemo.runChecks()")
    check(result.get("status") == "PASS", "embedded display checks pass", checks)
    check(bool(result.get("checks")), "embedded display assertions are present", checks)
    check(all(result.get("checks", {}).values()), "every embedded assertion passes", checks)
    frequency = page.locator("#frequency")
    frequency.focus()
    before = frequency.input_value()
    page.keyboard.press("ArrowRight")
    check(frequency.input_value() != before, "frequency supports arrow keys", checks)
    page.keyboard.press("Home")
    check(float(frequency.input_value()) == 0, "frequency supports Home", checks)
    page.keyboard.press("End")
    check(
        abs(float(frequency.input_value()) - float(frequency.get_attribute("max"))) < 1e-13,
        "frequency supports End",
        checks,
    )
    page.locator("#null-frequency").click()
    check(
        abs(float(frequency.input_value()) - 3.141592653589793 / 3) < 1e-13,
        "null preset restores the selected frequency",
        checks,
    )
    page.locator("#log-scale").uncheck()
    check(not page.locator("#log-scale").is_checked(), "linear scale accepts pointer input", checks)
    page.locator("#log-scale").check()
    for side, other in (("A", "B"), ("B", "A")):
        page.locator(f"#show-{side.lower()}").uncheck()
        check(
            not page.locator(f'#spectrum path[data-curve="{side}"]').is_visible()
            and page.locator(f'#spectrum path[data-curve="{other}"]').is_visible(),
            f"hide {side} while retaining {other} curve",
            checks,
        )
        page.locator(f"#show-{side.lower()}").check()
    for view in ("detail", "full"):
        page.locator(f'input[name="geometry-view"][value="{view}"]').check()
        check(inspect_state(page)["geometryView"] == view, f"geometry view {view} works", checks)
    page.locator("#sweep").click()
    initial = float(frequency.input_value())
    page.wait_for_function(
        "value => Math.abs(Number(document.querySelector('#frequency').value) - value) > 0.001",
        arg=initial,
        timeout=3000,
    )
    check(True, "frequency sweep actually advances", checks)
    page.locator("#sweep").click()
    paused = frequency.input_value()
    page.wait_for_timeout(180)
    check(frequency.input_value() == paused, "paused sweep remains stopped", checks)
    page.locator("#null-frequency").click()
    for profile in ("original-verify", "long-exposure-v1"):
        page.locator("#profile").select_option(profile)
        check(
            page.locator("#profile").input_value() == profile,
            f"profile can be selected: {profile}",
            checks,
        )
        expected = page.evaluate(
            "profile => profile === 'original-verify' ? HOMOMETRIC_DEMO_DATA.certificate : "
            "HOMOMETRIC_DEMO_DATA.profiles[profile].certificate",
            profile,
        )
        check(
            page.locator("#window-count").inner_text().replace(",", "").replace("\n", "")
            == expected["sufficient_observation_windows"],
            f"full observation count matches {profile} data",
            checks,
        )
        for mode in ("expanded", "latent"):
            radio = page.locator(f'input[name="bound-mode"][value="{mode}"]')
            radio.check()
            check(radio.is_checked(), f"interval mode {mode} works in {profile}", checks)
            key = "expanded_skewness_display" if mode == "expanded" else "skewness_display"
            for side in ("A", "B"):
                interval = expected["classes"][side][key]
                expected_text = f"[{interval[0]:.10f}, {interval[1]:.10f}]"
                check(
                    page.locator(f"#bound-{side.lower()}").inner_text().removeprefix("≈ ")
                    == expected_text,
                    f"{side} displayed {mode} endpoints match {profile} data",
                    checks,
                )
    check_motion(page, checks)
    return result


def audit_viewport(
    browser, name: str, size: tuple[int, int], output: Path, demo_url: str, axe_script: Path | None
) -> dict:
    checks: list[str] = []
    screenshots: list[dict] = []
    errors: list[str] = []
    remote_requests: list[str] = []
    failed_requests: list[str] = []
    context = browser.new_context(
        viewport={"width": size[0], "height": size[1]},
        reduced_motion="reduce",
        color_scheme="light",
        locale="en-US",
    )

    def route_request(route) -> None:
        if urlparse(route.request.url).scheme in {"http", "https", "ws", "wss"}:
            remote_requests.append(route.request.url)
            route.abort()
        else:
            route.continue_()

    context.route("**/*", route_request)
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("requestfailed", lambda request: failed_requests.append(request.url))
    record = {"viewport": {"width": size[0], "height": size[1]}, "checks": checks}
    try:
        page.goto(demo_url, wait_until="load")
        page.wait_for_function("typeof HomometricDemo !== 'undefined'")
        check(page.locator("h1").count() == 1, "one primary heading", checks)
        check(page.locator("main").count() == 1, "one main landmark", checks)
        check(page.locator("html").get_attribute("lang") == "en", "document language", checks)
        unnamed_controls = page.locator("input,select,button").evaluate_all(
            "nodes => nodes.filter(n => !(n.getAttribute('aria-label') || "
            "n.getAttribute('aria-labelledby') || (n.labels && n.labels.length) || "
            "(n.tagName === 'BUTTON' && n.textContent.trim()))).map(n => n.id)"
        )
        check(not unnamed_controls, "form controls have accessible names", checks)
        check(
            page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"),
            "no horizontal page overflow",
            checks,
        )
        check(
            page.evaluate("getComputedStyle(document.documentElement).scrollBehavior !== 'smooth'"),
            "reduced motion disables smooth scrolling",
            checks,
        )
        check(
            page.locator('#sweep[aria-pressed="true"]').count() == 0,
            "no frequency animation starts automatically",
            checks,
        )
        initial_state = inspect_state(page)
        page.wait_for_timeout(180)
        check(inspect_state(page) == initial_state, "motion does not autoplay", checks)
        check_links(page, checks)
        screenshot(page, output, f"{name}-initial", screenshots)
        page.keyboard.press("Tab")
        check(
            page.evaluate("document.activeElement.classList.contains('skip')"),
            "keyboard starts with the skip link",
            checks,
        )
        page.keyboard.press("Enter")
        record["display_checks"] = check_interactions(page, checks)
        record["motion_stress"] = stress_motion(page, checks)
        if size[0] <= 390:
            small_buttons = page.locator("button").evaluate_all(
                "nodes => nodes.filter(n => {const r=n.getBoundingClientRect(); "
                "return r.width > 0 && (r.height < 43.9 || r.width < 43.9);}).map(n => n.id)"
            )
            check(not small_buttons, "mobile buttons have 44px touch targets", checks)
            check(
                page.locator("#intensity-a").is_visible()
                and page.locator("#intensity-b").is_visible(),
                "mobile keeps both intensity readouts visible",
                checks,
            )
        page.evaluate("window.scrollTo(0, 0)")
        screenshot(page, output, f"{name}-overview", screenshots)
        for section in ("explorer", "diffraction", "certificate", "assumptions"):
            locator = page.locator(f"#{section}")
            if locator.count():
                section_screenshot(page, output, f"{name}-{section}", f"#{section}", screenshots)
        page.locator("#sample-motion").click()
        section_screenshot(page, output, f"{name}-motion-sample", ".geometry-panel", screenshots)
        page.locator('input[name="geometry-view"][value="detail"]').check()
        section_screenshot(
            page, output, f"{name}-motion-detail-sample", ".geometry-panel", screenshots
        )
        page.locator('input[name="geometry-view"][value="full"]').check()
        page.locator("#reset-motion").click()
        page.locator('input[name="bound-mode"][value="expanded"]').check()
        for profile in ("original-verify", "long-exposure-v1"):
            page.locator("#profile").select_option(profile)
            section_screenshot(
                page, output, f"{name}-{profile}-expanded", "#certificate", screenshots
            )
        check(not remote_requests, "page makes no network requests", checks)
        check(not failed_requests, "all local resources load", checks)
        check(not errors, "no browser JavaScript errors", checks)
        record["failed_resource_count"] = len(failed_requests)
        if axe_script:
            record["accessibility"] = check_accessibility(page, axe_script)
            record["accessibility"]["tool_resource_failure_count"] = len(failed_requests)
            check(
                not record["accessibility"]["violations"],
                "axe reports no accessibility violations",
                checks,
            )
        record["status"] = "PASS"
    except Exception as error:
        record["status"] = "FAIL"
        record["error"] = str(error).replace(demo_url, "<demo>/index.html")
        screenshot(page, output, f"{name}-failure", screenshots)
    finally:
        record["screenshots"] = screenshots
        record["javascript_errors"] = errors
        record["network_request_count"] = len(remote_requests)
        record.setdefault("failed_resource_count", len(failed_requests))
        context.close()
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-dir", type=Path, default=ROOT / "demo")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / ".build" / "demo-audit" / "current"
    )
    parser.add_argument(
        "--browsers", default="chromium", help="comma-separated chromium,firefox,webkit engines"
    )
    parser.add_argument(
        "--allow-missing-browsers", action="store_true", help="record absent engines as SKIPPED"
    )
    parser.add_argument(
        "--axe-script", type=Path, help="optional local axe-core script for accessibility checks"
    )
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise SystemExit(
            "Optional browser tools are absent. Install Playwright in a separate developer "
            "environment, then install the requested browser binaries."
        ) from error
    names = args.browsers.split(",")
    if not names or any(name not in {"chromium", "firefox", "webkit"} for name in names):
        parser.error("--browsers must name chromium, firefox and/or webkit")
    demo = args.demo_dir.resolve()
    if not (demo / "index.html").is_file():
        parser.error("--demo-dir must contain index.html")
    if args.axe_script and not args.axe_script.is_file():
        parser.error("--axe-script must name a local axe-core JavaScript file")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    demo_url = (demo / "index.html").as_uri()
    report = {
        "schema_version": 1,
        "playwright_version": version("playwright"),
        "scope": "Offline browser behavior and screenshot capture; not mathematical verification.",
        "visual_inspection": "Required separately; screenshots alone do not establish visual quality.",
        "source_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(demo.iterdir())
            if path.is_file() and path.suffix in {".html", ".css", ".js", ".json"}
        },
        "browsers": {},
    }
    with sync_playwright() as playwright:
        for name in names:
            engine = getattr(playwright, name)
            if not Path(engine.executable_path).is_file():
                report["browsers"][name] = {
                    "status": "SKIPPED" if args.allow_missing_browsers else "FAIL",
                    "reason": "Requested browser binary is not installed.",
                }
                continue
            directory = output / name
            directory.mkdir(exist_ok=True)
            browser = engine.launch()
            records = {
                label: audit_viewport(browser, label, size, directory, demo_url, args.axe_script)
                for label, size in VIEWPORTS.items()
            }
            report["browsers"][name] = {
                "version": browser.version,
                "status": "PASS"
                if all(r["status"] == "PASS" for r in records.values())
                else "FAIL",
                "viewports": records,
            }
            browser.close()
    statuses = [record["status"] for record in report["browsers"].values()]
    report["status"] = "PASS" if "PASS" in statuses and "FAIL" not in statuses else "FAIL"
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name, record in report["browsers"].items():
        print(f"{record['status']}: {name} offline explorer audit")
        for label, viewport in record.get("viewports", {}).items():
            print(f"  {viewport['status']}: {label}; {len(viewport['checks'])} browser assertions")
            if "error" in viewport:
                print(f"    {viewport['error']}")
    print("Screenshots require separate visual inspection; no theorem verification is asserted.")
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
