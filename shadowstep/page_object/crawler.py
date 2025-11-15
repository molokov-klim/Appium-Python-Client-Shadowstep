# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""All this is in principle implementable, but you'll need to consider several non-trivial nuances and properly break down the task into stages.

1. **Complete scrolling**

   * For each found scrollable element, you need to run "scroll down" until new elements appear — and at each step update the list, filtering by already seen ones (store, say, by unique tuple (resource-id, bounds) or hash).
   * It's important not to rely only on "scroll to end" of one call: usually first try `scroll(location, down)`, and then when there's no more "movement", consider that the bottom is reached.

2. **Python PageObject file generation**

   * Having collected the full set of elements and their transitions, you can run a template (e.g., Jinja2) and on the fly substitute properties: `@property def name/title/...`, transition methods (`edges`) and import `Element`/`PageBaseShadowstep`.
   * Minimize code duplication: in the template describe only the structure, and pass all dynamic attributes (element names, locators, target pages) to the render.

3. **Automatic crawl through all screens (transition graph)**

   * Launch the app, go to the starting Activity and take `PageObjectExtractor` for the current screen.
   * For each interactive element (except those already "pressed" on this page) call `element.tap()`, wait for UI stabilization and try to detect if the screen has changed:

     * Using `is_current_page()` of the old page — if it returns `False`, the transition was successful.
     * Determine the new page either by contextual Activity set, or by another PageObject through a series of `page.is_current_page()`.
   * In this case, add a record to `self.edges[old_name]`: `locator -> new_name`.
   * **Rollback**: to continue crawling from the original page, you need to explicitly go back (Back) or restart the app to the initial state.

4. **Traversal organization**

   * Standard BFS/DFS through the graph: store a queue of screens that haven't been "explored" yet (not passed through all their elements).
   * To prevent infinite loops and duplicates — mark visited pairs ("page + already pressed element").
   * Separately store "already generated" PageObject files to avoid overwriting them unnecessarily.

---

### Main difficulties and what to pay attention to

* **UI instability**: animations, popup dialogs, asynchronous loads — need to wait for stable screen state.
* **Parameterized pages**: the same layout can contain different content (product lists, message lists). The code generator should be able to either generalize such pages, or distinguish them by "key" elements.
* **Logs and debugging**: during crawling you'll encounter unexpected dialogs (permissions, ads, etc.). It's recommended to equip each step with "safe tap" mode — click only after confident element detection.
* **Duration**: full traversal can take dozens and hundreds of clicks. Need timeouts and possibly "resume points" (to not start everything over on failure).

---

### Final opinion

The idea of "scroll, extract, generate PageObject, automatically tap everything and build transition graph" — is quite viable and will ultimately give you a complete "sniffer" of your Android app structure. At the same time:

* The code will be quite complex, and it's advisable to organize it modularly:

  1. Traversal and locator collection
  2. Filtering and scrolling
  3. Code generation
  4. Graph traversal algorithm
* At the first stage, it's better to limit yourself to one Activity or one section, debug scroll logic and code generation, and then scale to the entire hierarchy.

In general — **quite possible**, just need to lay out "crawling" and "crowd-code" automation carefully and test on examples to catch all the nuances of screen changes and dynamic elements.

"""


